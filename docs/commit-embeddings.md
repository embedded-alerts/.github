# Git commit embeddings

The organization-owned `commit-embeddings` composite action converts Git
commits into model-versioned vector records after GitHub receives a push. A
GitHub-hosted workflow cannot run a server-side pre-push hook, so repository
callers use the `push` event and also expose `workflow_dispatch` for bounded
history backfills.

## Runtime flow

1. The caller checks out complete Git history without persisting credentials.
2. The action selects commits in `before..after`. A new branch or unavailable
   force-push base indexes only the delivered head instead of replaying the
   repository's entire history.
3. Each commit becomes one or more bounded documents containing metadata,
   message, changed paths, and the textual first-parent patch.
4. Potential credential lines and private-key blocks are removed. Common
   environment and private-key file types are excluded from patch content.
5. GitHub Models generates 512-dimensional
   `openai/text-embedding-3-small` vectors with the caller's short-lived
   `GITHUB_TOKEN`; no long-lived model API key is required.
6. Records are uploaded as a uniquely named Actions artifact. If an HTTPS
   webhook is configured, the exact newline-delimited JSON payload is also
   delivered to that endpoint and a non-success response fails the job.

The default artifact retention request is 90 days. The effective retention may
be lower if organization or repository policy imposes a smaller maximum.

## Caller contract

Every caller must grant only the permissions the action needs:

```yaml
permissions:
  contents: read
  models: read
```

The caller must check out with `fetch-depth: 0` and invoke the organization
action at a full 40-character commit SHA. This immutable pin is part of the
organization workflow policy.

The optional organization/repository configuration is:

- variable `EAL_COMMIT_EMBEDDINGS_WEBHOOK_URL`: credential-free HTTPS URL;
- secret `EAL_COMMIT_EMBEDDINGS_WEBHOOK_TOKEN`: optional bearer token.

The webhook receives `Content-Type: application/x-ndjson` and these metadata
headers:

- `X-EAL-Schema-Version: eal.git-commit-embedding.v1`;
- `X-EAL-Repository: owner/name`;
- `X-EAL-After-SHA: <40-character commit SHA>`.

Redirects are intentionally rejected so an authorization header cannot be
forwarded to a different origin. Delivery retries HTTP 429 and transient 5xx
responses with bounded backoff.

## Record schema

Each JSONL line is independently ingestible and contains:

- a deterministic SHA-256 record ID;
- repository, ref, canonical commit URL, commit SHA, parents, author name,
  timestamps, subject, and changed paths;
- chunk index/count, bounded source content, and its SHA-256 digest;
- embedding provider, model, configured model-space revision, dimensions,
  encoding, and normalization policy;
- the float vector.

Author email addresses are deliberately omitted. Each record ID incorporates
the repository, commit, chunk, embedding space, and content digest, making
webhook ingestion naturally idempotent.

## Backfills and unusual pushes

Run the repository's **Git commit embeddings** workflow manually to backfill up
to the configured `max-commits` ending at a selected `after-sha`. Provide both
`before-sha` and `after-sha` for an exact range. If `before-sha` is omitted on a
manual run, the most recent bounded history ending at `after-sha` is processed.

Pushes larger than the configured limit fail visibly instead of silently
dropping commits. Split those histories into bounded manual ranges. Deleted
branch events are skipped. Merge commits are represented by their change from
the first parent, which matches the change introduced on the pushed branch.

## Security and operating boundaries

- Only a push or an explicitly requested backfill sends source text to the
  model endpoint; pull requests do not receive model permissions.
- The action never persists checkout credentials and does not write back to the
  repository.
- Binary content is not embedded. Patch bytes, document bytes, commit counts,
  retries, and network timeouts are bounded.
- The webhook token is optional, is never written into an artifact, and is not
  logged.
- GitHub Models access must be enabled for the organization. A disabled policy
  fails closed at the model request rather than producing placeholder vectors.
- Artifacts provide generation and recovery, not a query service. Configure the
  webhook when records must enter a durable pgvector or other vector index.
