# Embedded Alerts acceptance matrix

Status: evidence plan for `eal-api-server.rs` issue #5. This matrix is a
boundary contract, not a claim that the live ingestion, embedding, or
notification system is complete.

## Capability boundaries

| surface | required input/output | safety gate | proof required |
| --- | --- | --- | --- |
| authorized ingest | allowlisted source URL/provider, immutable fetch identity, normalized page/event | HTTPS, bounded bytes/time/redirects, no arbitrary private-source access | malformed, oversized, timeout, redirect, duplicate, change-detection tests |
| provenance | source ID, fetched revision/time, content digest, parser revision | provenance is immutable and redacted; credentials never enter payloads | round-trip fixture and changed-source audit event |
| embedding | model ID, actual dimension, input digest, embedding revision | dimensions/model identity are explicit; padding never makes unlike models comparable | model/dimension mismatch is rejected; stale embeddings are not matched |
| hybrid search | tenant-scoped text and vector candidates with explainable scores | every query carries tenant scope and bounded limits | cross-tenant and malformed query tests |
| notification | consented tenant/channel recipient and delivery result | retention/deletion, rate limits, and provider-secret redaction | failed delivery is distinct from accepted/viewed/signed |
| semantic topology | Claritas export consumed by the customer's own server/client | no provider dashboard dependency; typed versioned export | schema, empty graph, large graph, and unknown-node tests |

## Canonical evidence envelope

Every accepted item should be representable without storing source contents:

```json
{
  "format": "embedded-alerts-evidence/v1",
  "tenantId": "<opaque id>",
  "sourceId": "<opaque id>",
  "sourceRevision": "<provider revision or canonical URL digest>",
  "contentSha256": "<sha256>",
  "parserRevision": "<immutable revision>",
  "model": { "id": "<model id>", "dimension": 1536, "revision": "<revision>" },
  "delivery": { "channel": "<channel>", "result": "queued|delivered|failed" },
  "observedAt": "<timestamp>",
  "payloadRedacted": true
}
```

`tenantId`, `sourceId`, and recipient identity are authorization inputs, not
search terms. A deletion request must remove source content, derived
embeddings, matches, and notification payloads according to the retention
policy, while preserving only the minimum redacted audit evidence.

## Required test slices

- [ ] Ingest accepts only an authorized source and rejects private or
      unallowlisted URLs.
- [ ] Fetch/parser limits cap bytes, redirects, parser work, and wall time.
- [ ] A duplicate source revision is idempotent; a changed revision creates one
      new provenance event.
- [ ] Cross-tenant source, query, match, and notification access is rejected.
- [ ] Model ID and actual vector dimension are checked on write and query.
- [ ] Stale embeddings are marked stale or regenerated; they are never silently
      compared to a new model's vectors.
- [ ] Failed notification delivery does not become a delivered/consented event.
- [ ] Topology export is versioned, typed, and renderable outside the producer.
- [ ] Logs and metrics contain digests/opaque IDs only, never source bodies,
      provider headers, historical credentials, or raw notification payloads.

Each completed slice should link its exact-head PR, test run, fixture digest,
and any deletion/retention receipt. Missing evidence keeps the corresponding
row open.
