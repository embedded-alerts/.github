from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "embed_commits.py"
SPEC = importlib.util.spec_from_file_location("embed_commits", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
embed_commits = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(embed_commits)


class ChunkingTests(unittest.TestCase):
    def test_chunk_utf8_preserves_text_and_byte_limit(self) -> None:
        text = ("alpha βeta 🚨\n" * 200) + "tail"
        chunks = embed_commits.chunk_utf8(text, 257)

        self.assertEqual("".join(chunks), text)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk.encode("utf-8")) <= 257 for chunk in chunks))

    def test_commit_documents_repeat_bounded_metadata(self) -> None:
        metadata = {
            "sha": "a" * 40,
            "parents": ["b" * 40],
            "author_name": "Example Author",
            "authored_at": "2026-08-24T00:00:00Z",
            "committed_at": "2026-08-24T00:00:01Z",
            "message": "feat: add a bounded change",
        }
        documents = embed_commits.commit_documents(
            "embedded-alerts/example",
            "main",
            metadata,
            ["src/main.rs"],
            "line\n" * 4_000,
            2_000,
        )

        self.assertGreater(len(documents), 1)
        for document in documents:
            self.assertIn("Repository: embedded-alerts/example", document)
            self.assertIn("Commit: " + "a" * 40, document)
            self.assertLessEqual(len(document.encode("utf-8")), 2_000)


class RedactionTests(unittest.TestCase):
    def test_redacts_known_credentials_and_private_keys(self) -> None:
        credential_value = "abcdefghijklmno" + "pqrstuvwxyz123456"
        github_token = "gh" + "p_" + credential_value
        private_key_label = "PRIVATE" + " KEY"
        text = "\n".join(
            (
                "+ normal code",
                f"+ token = '{credential_value}'",
                "+ " + github_token,
                f"+ -----BEGIN {private_key_label}-----",
                "+ private-material",
                f"+ -----END {private_key_label}-----",
                "+ normal tail",
            )
        )

        redacted = embed_commits.redact_potential_secrets(text)

        self.assertIn("+ normal code", redacted)
        self.assertIn("+ normal tail", redacted)
        self.assertNotIn(credential_value, redacted)
        self.assertNotIn("private-material", redacted)
        self.assertIn("[REDACTED:", redacted)


class LocalEmbeddingTests(unittest.TestCase):
    def test_embedding_is_deterministic_l2_normalized_and_sized(self) -> None:
        text = "feat: parse GitCommit payload\nfn parse_git_commit() {}"

        first = embed_commits.local_embedding(text, 256)
        second = embed_commits.local_embedding(text, 256)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 256)
        self.assertAlmostEqual(sum(value * value for value in first), 1.0, places=12)

    def test_embedding_changes_with_content(self) -> None:
        left = embed_commits.local_embedding("rust webhook retry", 256)
        right = embed_commits.local_embedding("css dashboard layout", 256)

        self.assertNotEqual(left, right)

    def test_identifier_features_split_camel_and_snake_case(self) -> None:
        features = embed_commits.embedding_features("parseGitCommit commit_sha")

        self.assertIn("identifier:parse", features)
        self.assertIn("identifier:git", features)
        self.assertIn("identifier:commit", features)
        self.assertIn("identifier:sha", features)

    def test_empty_document_is_rejected(self) -> None:
        with self.assertRaises(embed_commits.EmbeddingError):
            embed_commits.local_embedding("", 256)


class WebhookValidationTests(unittest.TestCase):
    def test_accepts_credential_free_https(self) -> None:
        value = "https://ingest.example.test/v1/commit-embeddings"
        self.assertEqual(embed_commits.validate_webhook_url(value), value)

    def test_rejects_insecure_or_credentialed_urls(self) -> None:
        invalid = (
            "http://ingest.example.test/v1",
            "https://user:pass@ingest.example.test/v1",
            "https://ingest.example.test/v1#fragment",
        )
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(embed_commits.EmbeddingError):
                    embed_commits.validate_webhook_url(value)


if __name__ == "__main__":
    unittest.main()
