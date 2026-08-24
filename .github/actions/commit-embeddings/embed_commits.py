#!/usr/bin/env python3
"""Generate model-versioned embeddings for Git commits.

The script is intentionally dependency-free so it can run on a stock GitHub
hosted runner. It reads a checked-out repository, derives bounded documents
from commit metadata and textual patches, generates deterministic local
feature-hash embeddings, writes newline-delimited JSON, and optionally forwards
the same records to an HTTPS webhook.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from collections import Counter
from typing import Any, Sequence
import unicodedata
from urllib import error, parse, request


SCHEMA_VERSION = "eal.git-commit-embedding.v1"
MODEL_ID = "eal/git-commit-hash-v1"
ZERO_SHA = "0" * 40
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
FEATURE_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}|[0-9]+|[^\s\w]{1,4}")

EXCLUDED_PATCH_PATHS = (
    ":(exclude,glob)**/.env",
    ":(exclude,glob)**/.env.*",
    ":(exclude,glob)**/*.key",
    ":(exclude,glob)**/*.pem",
    ":(exclude,glob)**/*.p12",
    ":(exclude,glob)**/*.pfx",
    ":(exclude,glob)**/id_rsa*",
    ":(exclude,glob)**/id_ed25519*",
)

SECRET_LINE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(
        r"(?i)\b(?:api[_-]?key|client[_-]?secret|password|token)\b"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9+/_.=-]{16,}"
    ),
)


class EmbeddingError(RuntimeError):
    """Raised for a safe, actionable indexing failure."""


def env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.environ.get(name, str(default)).strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise EmbeddingError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise EmbeddingError(f"{name} must be between {minimum} and {maximum}")
    return value


def git_bytes(*args: str, check: bool = True) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise EmbeddingError(f"git {' '.join(args[:2])} failed: {detail}")
    return completed.stdout


def git_text(*args: str, check: bool = True) -> str:
    return git_bytes(*args, check=check).decode("utf-8", errors="replace")


def is_commit(sha: str) -> bool:
    if not SHA_RE.fullmatch(sha):
        return False
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def resolve_commit(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise EmbeddingError(f"{label} is required")
    resolved = git_text("rev-parse", "--verify", f"{value}^{{commit}}").strip()
    if not SHA_RE.fullmatch(resolved):
        raise EmbeddingError(f"{label} did not resolve to a commit")
    return resolved.lower()


def select_commits(
    before: str, after: str, max_commits: int, event_name: str
) -> list[str]:
    after_sha = resolve_commit(after, "after SHA")
    before = before.strip().lower()

    if before and before != ZERO_SHA and is_commit(before):
        commits = git_text(
            "rev-list", "--reverse", "--topo-order", f"{before}..{after_sha}"
        ).splitlines()
    elif event_name == "workflow_dispatch":
        commits = git_text(
            "rev-list",
            "--reverse",
            "--topo-order",
            f"--max-count={max_commits}",
            after_sha,
        ).splitlines()
    else:
        # New branches and force-pushes can reference an unavailable `before`
        # object. Index the delivered head without silently replaying all history.
        commits = [after_sha]

    if len(commits) > max_commits:
        raise EmbeddingError(
            f"push contains {len(commits)} commits; limit is {max_commits}. "
            "Use workflow_dispatch with bounded ranges to backfill it."
        )
    return [sha.lower() for sha in commits]


def commit_metadata(sha: str) -> dict[str, Any]:
    parents = git_text("show", "-s", "--format=%P", sha).strip().split()
    message = git_text("show", "-s", "--format=%B", sha).strip()
    subject = next((line.strip() for line in message.splitlines() if line.strip()), "")
    return {
        "sha": sha,
        "parents": parents,
        "author_name": git_text("show", "-s", "--format=%an", sha).strip(),
        "authored_at": git_text("show", "-s", "--format=%aI", sha).strip(),
        "committed_at": git_text("show", "-s", "--format=%cI", sha).strip(),
        "subject": subject,
        "message": message,
    }


def changed_files(sha: str, parents: Sequence[str]) -> list[str]:
    if parents:
        raw = git_bytes("diff", "--name-only", "-z", parents[0], sha, "--")
    else:
        raw = git_bytes(
            "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", sha
        )
    return [part.decode("utf-8", errors="replace") for part in raw.split(b"\0") if part]


def textual_patch(sha: str, parents: Sequence[str], max_patch_bytes: int) -> str:
    common = (
        "--no-ext-diff",
        "--unified=3",
        "--no-color",
        "--find-renames",
        "--find-copies",
    )
    if parents:
        raw = git_bytes(
            "diff", *common, parents[0], sha, "--", *EXCLUDED_PATCH_PATHS
        )
    else:
        raw = git_bytes(
            "show",
            "--format=",
            *common,
            sha,
            "--",
            *EXCLUDED_PATCH_PATHS,
        )

    truncated = len(raw) > max_patch_bytes
    raw = raw[:max_patch_bytes]
    text = raw.decode("utf-8", errors="replace")
    text = redact_potential_secrets(text)
    if truncated:
        text += "\n[patch truncated at configured byte limit]\n"
    return text.strip()


def redact_potential_secrets(text: str) -> str:
    redacted: list[str] = []
    private_key = False
    for line in text.splitlines():
        if "-----BEGIN" in line and "PRIVATE KEY-----" in line:
            private_key = True
            redacted.append("[REDACTED: potential private key material]")
            continue
        if private_key:
            if "-----END" in line and "PRIVATE KEY-----" in line:
                private_key = False
            continue
        if any(pattern.search(line) for pattern in SECRET_LINE_PATTERNS):
            redacted.append("[REDACTED: potential credential material]")
        else:
            redacted.append(line)
    return "\n".join(redacted)


def truncate_utf8(text: str, max_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    candidate = encoded[:max_bytes]
    while candidate:
        try:
            return candidate.decode("utf-8")
        except UnicodeDecodeError as exc:
            candidate = candidate[: exc.start]
    return ""


def chunk_utf8(text: str, max_bytes: int) -> list[str]:
    if not text:
        return [""]
    chunks: list[str] = []
    remaining = text
    while remaining:
        chunk = truncate_utf8(remaining, max_bytes)
        if not chunk:
            raise EmbeddingError("unable to split commit document safely")
        if len(chunk) < len(remaining):
            newline = chunk.rfind("\n")
            if newline >= len(chunk) // 2:
                chunk = chunk[: newline + 1]
        chunks.append(chunk)
        remaining = remaining[len(chunk) :]
    return chunks


def bounded_file_list(files: Sequence[str], max_bytes: int = 8_000) -> str:
    lines: list[str] = []
    used = 0
    for name in files:
        line = f"- {name}\n"
        size = len(line.encode("utf-8"))
        if used + size > max_bytes:
            lines.append(f"- [... {len(files) - len(lines)} additional paths omitted]\n")
            break
        lines.append(line)
        used += size
    return "".join(lines).rstrip() or "- (none)"


def commit_documents(
    repository: str,
    ref_name: str,
    metadata: dict[str, Any],
    files: Sequence[str],
    patch: str,
    max_chunk_bytes: int,
) -> list[str]:
    header = (
        f"Repository: {repository}\n"
        f"Ref: {ref_name}\n"
        f"Commit: {metadata['sha']}\n"
        f"Parents: {' '.join(metadata['parents']) or '(root)'}\n"
        f"Author: {metadata['author_name']}\n"
        f"Authored: {metadata['authored_at']}\n"
        f"Committed: {metadata['committed_at']}\n\n"
        f"Commit message:\n{metadata['message'] or '(empty)'}\n\n"
        f"Changed files:\n{bounded_file_list(files)}\n"
    )
    header = truncate_utf8(header, max_chunk_bytes // 2)
    overhead = len(header.encode("utf-8")) + 64
    body_limit = max(256, max_chunk_bytes - overhead)
    patch_chunks = chunk_utf8(patch or "(no textual patch)", body_limit)
    count = len(patch_chunks)
    return [
        f"{header}\n\nPatch chunk {index + 1}/{count}:\n{chunk}".strip()
        for index, chunk in enumerate(patch_chunks)
    ]


def retry_delay(headers: Any, attempt: int) -> float:
    raw = headers.get("Retry-After") if headers is not None else None
    if raw:
        try:
            return min(30.0, max(0.0, float(raw)))
        except ValueError:
            pass
    return min(16.0, float(2**attempt))


def identifier_parts(token: str) -> list[str]:
    with_boundaries = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", token)
    return [part.lower() for part in re.split(r"[_\W]+", with_boundaries) if part]


def embedding_features(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKC", text)
    raw_tokens = FEATURE_TOKEN_RE.findall(normalized)
    tokens = [token.lower() for token in raw_tokens]
    features = [f"token:{token}" for token in tokens]

    for raw in raw_tokens:
        if not (raw[0].isalpha() or raw[0] == "_"):
            continue
        for part in identifier_parts(raw):
            features.append(f"identifier:{part}")
            bounded = f"^{part}$"
            if len(bounded) >= 3:
                features.extend(
                    f"identifier-trigram:{bounded[index:index + 3]}"
                    for index in range(len(bounded) - 2)
                )

    features.extend(
        f"token-bigram:{left}\u241f{right}"
        for left, right in zip(tokens, tokens[1:])
    )
    return features


def local_embedding(text: str, dimensions: int) -> list[float]:
    if dimensions < 1:
        raise EmbeddingError("embedding dimensions must be positive")
    counts = Counter(embedding_features(text))
    vector = [0.0] * dimensions
    for feature, count in counts.items():
        digest = hashlib.sha256(f"{MODEL_ID}\0{feature}".encode("utf-8")).digest()
        index = int.from_bytes(digest[:8], "big") % dimensions
        sign = 1.0 if digest[8] & 1 else -1.0
        vector[index] += sign * (1.0 + math.log(float(count)))

    norm = math.sqrt(sum(value * value for value in vector))
    if not math.isfinite(norm) or norm == 0.0:
        raise EmbeddingError("commit document did not produce a finite embedding")
    normalized = [value / norm for value in vector]
    if not all(math.isfinite(value) for value in normalized):
        raise EmbeddingError("local embedder produced a non-finite value")
    return normalized


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def validate_webhook_url(value: str) -> str:
    parsed = parse.urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
    ):
        raise EmbeddingError("webhook URL must be credential-free HTTPS without a fragment")
    return value


def post_webhook(url: str, token: str, payload: bytes, repository: str, after_sha: str) -> None:
    url = validate_webhook_url(url)
    headers = {
        "Content-Type": "application/x-ndjson",
        "User-Agent": "embedded-alerts-commit-embeddings/1",
        "X-EAL-Schema-Version": SCHEMA_VERSION,
        "X-EAL-Repository": repository,
        "X-EAL-After-SHA": after_sha,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    opener = request.build_opener(NoRedirect())

    for attempt in range(5):
        req = request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with opener.open(req, timeout=60) as response:
                if not 200 <= response.status < 300:
                    raise EmbeddingError(f"webhook returned HTTP {response.status}")
                response.read(1024)
                return
        except error.HTTPError as exc:
            if (exc.code == 429 or 500 <= exc.code < 600) and attempt < 4:
                time.sleep(retry_delay(exc.headers, attempt))
                continue
            raise EmbeddingError(f"webhook delivery failed with HTTP {exc.code}") from exc
        except (error.URLError, TimeoutError) as exc:
            if attempt < 4:
                time.sleep(retry_delay(None, attempt))
                continue
            raise EmbeddingError("webhook delivery failed after retries") from exc


def set_action_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"{name}={value}\n")


def append_step_summary(lines: Sequence[str]) -> None:
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("\n".join(lines) + "\n")


def main() -> int:
    repository = os.environ.get("EAL_REPOSITORY", "").strip()
    ref_name = os.environ.get("EAL_REF_NAME", "").strip() or "(detached)"
    before = os.environ.get("EAL_BEFORE_SHA", "")
    after = os.environ.get("EAL_AFTER_SHA", "") or os.environ.get("GITHUB_SHA", "")
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    output_file = Path(
        os.environ.get(
            "EAL_OUTPUT_FILE", ".artifacts/commit-embeddings/records.jsonl"
        )
    )
    webhook_url = os.environ.get("EAL_WEBHOOK_URL", "").strip()
    webhook_token = os.environ.get("EAL_WEBHOOK_TOKEN", "")
    dimensions = env_int("EAL_EMBEDDING_DIMENSIONS", 1_024, 64, 8_192)
    max_commits = env_int("EAL_MAX_COMMITS", 100, 1, 1_000)
    max_chunk_bytes = env_int("EAL_MAX_CHUNK_BYTES", 6_000, 2_000, 24_000)
    max_patch_bytes = env_int("EAL_MAX_PATCH_BYTES", 1_000_000, 10_000, 20_000_000)

    if not repository or "/" not in repository:
        raise EmbeddingError("repository must use owner/name form")
    commit_shas = select_commits(before, after, max_commits, event_name)
    if not commit_shas:
        set_action_output("record-count", "0")
        set_action_output("commit-count", "0")
        print("No new commits were found in the delivered range.")
        return 0

    documents: list[dict[str, Any]] = []
    metadata_by_sha: dict[str, dict[str, Any]] = {}
    files_by_sha: dict[str, list[str]] = {}
    for sha in commit_shas:
        metadata = commit_metadata(sha)
        files = changed_files(sha, metadata["parents"])
        patch = textual_patch(sha, metadata["parents"], max_patch_bytes)
        chunks = commit_documents(
            repository, ref_name, metadata, files, patch, max_chunk_bytes
        )
        metadata_by_sha[sha] = metadata
        files_by_sha[sha] = files
        for index, content in enumerate(chunks):
            documents.append(
                {
                    "sha": sha,
                    "chunk_index": index,
                    "chunk_count": len(chunks),
                    "content": content,
                }
            )

    contents = [document["content"] for document in documents]
    vectors = [local_embedding(content, dimensions) for content in contents]

    records: list[dict[str, Any]] = []
    for document, vector in zip(documents, vectors, strict=True):
        sha = document["sha"]
        metadata = metadata_by_sha[sha]
        content = document["content"]
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        identity = "\0".join(
            (
                repository,
                sha,
                str(document["chunk_index"]),
                MODEL_ID,
                str(dimensions),
                content_sha256,
            )
        )
        records.append(
            {
                "schema_version": SCHEMA_VERSION,
                "id": "sha256:" + hashlib.sha256(identity.encode("utf-8")).hexdigest(),
                "source_type": "git-commit",
                "canonical_uri": (
                    f"https://github.com/{repository}/commit/{sha}"
                    f"#chunk-{document['chunk_index']}"
                ),
                "repository": repository,
                "ref": ref_name,
                "commit": {
                    "sha": sha,
                    "parents": metadata["parents"],
                    "author_name": metadata["author_name"],
                    "authored_at": metadata["authored_at"],
                    "committed_at": metadata["committed_at"],
                    "subject": metadata["subject"],
                    "changed_files": files_by_sha[sha],
                },
                "chunk_index": document["chunk_index"],
                "chunk_count": document["chunk_count"],
                "content": content,
                "content_sha256": "sha256:" + content_sha256,
                "embedding_space": {
                    "provider": "local",
                    "model": MODEL_ID,
                    "model_revision": MODEL_ID,
                    "dimensions": dimensions,
                    "encoding": "float",
                    "normalization": "l2",
                },
                "embedding": vector,
            }
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = b"".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        + b"\n"
        for record in records
    )
    output_file.write_bytes(payload)

    after_sha = resolve_commit(after, "after SHA")
    if webhook_url:
        post_webhook(webhook_url, webhook_token, payload, repository, after_sha)

    artifact_name = f"commit-embeddings-{repository.replace('/', '-')}-{after_sha[:12]}"
    set_action_output("record-count", str(len(records)))
    set_action_output("commit-count", str(len(commit_shas)))
    set_action_output("output-file", str(output_file))
    set_action_output("artifact-name", artifact_name[:200])
    append_step_summary(
        (
            "### Commit embeddings",
            "",
            f"- Commits indexed: `{len(commit_shas)}`",
            f"- Vector records: `{len(records)}`",
            f"- Model: `{MODEL_ID}`",
            f"- Dimensions: `{dimensions}`",
            f"- Webhook delivered: `{'yes' if webhook_url else 'not configured'}`",
        )
    )
    print(
        f"Generated {len(records)} embedding records from {len(commit_shas)} commits "
        f"with {MODEL_ID} ({dimensions} dimensions)."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EmbeddingError as exc:
        print(f"commit embedding generation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
