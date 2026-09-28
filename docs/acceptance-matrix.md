# Embedded Alerts production acceptance matrix

This document defines the evidence required before an Embedded Alerts capability is described as production-ready. It is an acceptance contract, not a claim that every row is implemented.

The initial product target is a curated web-scale alerting service: roughly 1,000 approved domains and about 10,000 new or changed pages per day, with semantic matching against saved alert embeddings rather than literal-keyword matching.

## Capability matrix

| surface | required behavior | safety / correctness boundary | acceptance evidence |
| --- | --- | --- | --- |
| source admission | only explicitly approved public sources enter crawl discovery | no arbitrary private-network, local-file, credential-bearing, or unapproved authenticated-source access | allowlist tests, redirect-boundary tests, SSRF tests, bounded fetch tests |
| crawl / fetch | discover new and changed public pages with bounded concurrency and retry | per-host budgets, redirect limits, byte/time limits, user-agent policy, backoff, robots/site-policy support where applicable | deterministic fixtures plus timeout, retry, duplicate, and change-detection tests |
| immutable provenance | every accepted page revision has stable source, canonical URL identity, fetch time, parser revision, and content digest | provenance is append-only; raw credentials never enter payloads or audit evidence | round-trip fixture and idempotent retry evidence |
| alert hot index | each enabled alert revision has one immutable embedding per certified model space | tenant, rule revision, model, model version, dimensions, and normalization must match before comparison | schema constraints plus exact-head DB integration tests |
| reverse semantic matching | each incoming page embedding queries active saved-alert embeddings and persists immutable match evidence | tenant/source filters apply before admission; candidate fanout is bounded; transient page vectors need not be retained | exact-head PostgreSQL/pgvector tests for matching, retries, tenant isolation, source isolation, and model-space isolation |
| historical search | optional persisted page embeddings support user-initiated semantic search | historical search remains separate from the reverse-alert hot path and obeys the same tenant/model boundaries | contract and DB integration tests |
| notification planning | accepted matches become deduplicated delivery intents | consent, per-channel policy, digest windows, rate limits, and quiet periods apply before send | duplicate/retry tests and deterministic delivery-intent fixtures |
| notification delivery | providers deliver email/in-app/push/webhook notifications with retry and dead-letter behavior | provider secrets are redacted; accepted, delivered, failed, bounced, suppressed, and viewed are distinct states | provider-adapter contract tests and replay-safe delivery tests |
| deletion / retention | requested content, derived embeddings, matches, and notification payloads follow explicit retention policy | retain only minimum redacted audit evidence allowed by policy | deletion receipt and post-delete lookup tests |
| observability | OTel/tracing exposes hot-index writes, page revision identity, candidate counts, latency, retries, and delivery state | never log page bodies, embedding values, authorization headers, provider credentials, or raw notification payloads | log-field allowlist tests/review plus exact-head CI |
| scale / cost | the initial 10,000-pages/day workload is sustainable with burst headroom | bounded queues, backpressure, per-host fairness, model-space sharding, and measurable embedding/provider spend | replay load test with throughput, p95/p99 latency, queue depth, failure rate, and cost report |

## Canonical redacted evidence envelope

Evidence uses `snake_case` wire names. The envelope intentionally describes provenance without storing page bodies or vectors.

```json
{
  "format": "embedded-alerts-evidence/v1",
  "tenant_id": "<opaque uuid>",
  "source_id": "<opaque uuid>",
  "page_revision_id": "<opaque uuid>",
  "content_sha256": "<sha256>",
  "parser_revision": "<immutable revision>",
  "embedding_model": "<model id>",
  "embedding_model_version": "<model revision>",
  "embedding_dimensions": 1536,
  "embedding_normalization": "unit_length",
  "match_mode": "reverse_alert_stream",
  "delivery_channel": "email",
  "delivery_result": "queued",
  "observed_at": "<rfc3339 timestamp>",
  "payload_redacted": true
}
```

Opaque IDs are authorization and correlation inputs, not search terms. Source content, embedding values, authorization material, provider headers, and recipient secrets are excluded from this envelope.

## Evidence already landed

The following implementation evidence exists in `embedded-alerts/eal-api`:

- PR #21: reverse-alert hot-path persistence and matcher. It added immutable active-alert embeddings, transient page-vector reverse matching, bounded candidate selection, deterministic immutable match evidence, and the active-search limit. Its exact-head PostgreSQL/pgvector CI also caught and repaired a first-page ingestion durability bug before merge.
- PR #22: DB-backed isolation hardening. It proves reverse matching does not cross tenant boundaries, applies source filters before candidate admission, and never compares incompatible embedding model versions.

These rows are still only part of the full product acceptance matrix. A green API hot path does not by itself prove crawler policy, provider delivery, deletion, cost, or sustained-load readiness.

## Required next evidence

- [ ] Authorized crawler discovery across an explicit source catalog, with SSRF and redirect-boundary tests.
- [ ] Deterministic change detection and idempotent enqueue for page revisions.
- [ ] Queue/backpressure replay proving burst recovery without duplicate matches.
- [ ] Certified ANN/shard plan for large alert populations; exact scoring remains the correctness oracle.
- [ ] Notification-intent deduplication and digest-window semantics.
- [ ] Email provider adapter with bounce/suppression/retry/dead-letter evidence.
- [ ] Deletion/retention receipt tests covering source content, derived embeddings, matches, and notification payloads.
- [ ] OTel field allowlist review proving no raw content/vector/secret leakage.
- [ ] Load replay at and above the initial 10,000-pages/day target with latency, queue-depth, error-rate, and cost evidence.

Every completed item should link its exact-head PR, test run, immutable artifact or fixture digest, and any relevant migration or roll-forward plan. Missing evidence keeps the corresponding production-readiness row open.
