# Embedded Alerts semantic alert architecture

Embedded Alerts is a Google Alerts-style platform built around **semantic similarity** rather than only literal keyword matching. A user saves a concept; when the platform discovers a new or materially changed webpage that is semantically relevant, the match enters a durable notification pipeline.

This document describes the public architecture direction. The canonical implementation plan is tracked in the [Embedded Alerts Linear project](https://linear.app/denman/project/githubcomembedded-alerts-2fb7392497ab), especially [DEN-3461](https://linear.app/denman/issue/DEN-3461/embedded-alerts-implement-source-ingestion-and-model-versioned).

## Core scaling principle

The alerting service is a **streaming reverse-search system**.

Do not require a multi-billion-document vector index just to send real-time alerts. Keep users' **active saved alert embeddings** in the hot ANN index and stream newly discovered pages through that index.

```text
saved-alert creation/update
        |
        v
 embed saved concept
        |
        v
 ACTIVE ALERT ANN INDEX
        ^
        |
 new/changed web page
        |
        v
 fetch -> extract -> dedupe -> compact embedding
        |
        v
 ANN candidate alerts
        |
        v
 exact score / optional richer rerank
        |
        v
 durable match + notification state machine
```

Similarity is only valid within the same embedding model space. Model identity, version, dimensions, normalization strategy, and generation provenance are part of the vector contract.

## Planning scale

Capacity planning currently considers a deliberately large scenario:

- 100 million newly discovered or materially changed pages/day;
- roughly 1,157 page events/second on a 24-hour average;
- 3 billion page events/month;
- 9 billion page events across 90 days;
- up to 10 active semantic alerts per user.

At one million users, the hot side is at most ten million saved-alert vectors. With 512-dimensional float16 vectors, those vector payloads are roughly 10 GB before ANN graph/index overhead. That is fundamentally different from forcing all nine billion recent pages into the real-time alert index.

## Discovery

Use multiple discovery channels rather than relying on recursive crawling alone:

- incremental HTTP crawler/frontier;
- RSS and Atom feeds;
- XML sitemaps;
- IndexNow-style added/changed/deleted URL notifications;
- external indexes such as Common Crawl for bootstrap/backfill;
- user-registered feeds, domains, and sources.

Common Crawl's September 2026 archive contains 2.17 billion pages and 361.4 TiB of uncompressed content, demonstrating that the overall crawl scale is large but established: <https://www.commoncrawl.org/blog>.

## Fetch and extract

The default path is:

```text
HTTP GET -> HTML parsing -> main-content extraction
```

Headless browser rendering is a bounded fallback for pages that cannot be meaningfully extracted otherwise. Rendering every discovered page with Chromium/Playwright/Selenium is intentionally not the default at web scale.

Normalize canonical URLs, remove boilerplate, detect language, compute stable content hashes, and use near-duplicate fingerprints such as SimHash/MinHash **before** generating embeddings.

## Compact first-pass embeddings

The first-pass representation should emphasize high-signal content rather than blindly embedding an entire webpage:

- title and description;
- primary headings;
- article metadata;
- a bounded main-text excerpt;
- selected named entities or structured metadata.

The goal is cheap candidate generation. Full-content embeddings, cross-encoders, or LLM relevance checks can be used for the small candidate fraction that survives ANN and exact-score thresholds.

## Matching stages

1. Route the page to compatible alert partitions by model space and inexpensive filters.
2. ANN search for a bounded `top_k` candidate set.
3. Recompute exact similarity using the original vectors.
4. Apply model-calibrated thresholds.
5. Optionally use richer reranking for borderline/high-value candidates.
6. Apply alert exclusions, dedupe, cooldown, and delivery policy.
7. Persist match evidence and delivery receipts.

The ANN score is candidate-generation evidence, not a notification by itself.

## Storage tiers

### Hot

- active saved-alert vectors and ANN indexes;
- alert routing/filter metadata;
- recent content hashes and dedupe state;
- recent candidate state.

### Warm

- matched page revisions;
- notification history;
- match/rerank evidence;
- bounded recent fingerprints used for deterministic re-evaluation.

### Cold

- optional compressed WARC/Parquet/Iceberg-style crawl shards;
- URL/revision manifests and checksums;
- reproducibility/model provenance.

Archive pages in large batches rather than one object-store object per page.

## Embedded Alerts vs Embedded Search

These are separate product capabilities.

**Embedded Alerts:**

> Notify me when newly discovered or changed content semantically matches my saved concepts.

This requires the active-alert index and streaming page evaluation. It does **not** require persistent vectors for every page.

**Embedded Search:**

> Let me semantically search the historical corpus Embedded Alerts has crawled.

This does require persistent document vectors, historical ANN lifecycle management, model migration/re-embedding, and a much larger serving fleet. It may reuse the ingestion pipeline, but it should be separately budgeted and operated.

## Cost guardrails

Provider pricing is time-sensitive. The following is a planning snapshot dated **2026-09-27**, not a permanent pricing promise.

OpenAI's embedding documentation currently implies roughly $0.02 per million input tokens for `text-embedding-3-small` and roughly $0.13 per million for `text-embedding-3-large`: <https://developers.openai.com/api/docs/guides/embeddings>.

At 100M pages/day for a 30-day month:

| Embedded input/page | small model | large model |
| ---: | ---: | ---: |
| 200 tokens | ~$12K/month | ~$78K/month |
| 800 tokens | ~$48K/month | ~$312K/month |
| 2,000 tokens | ~$120K/month | ~$780K/month |

If dedupe/filtering reduces actual new embeddings to 30% of discovered pages and the first-pass fingerprint averages 200 tokens, small-model API embedding cost is roughly $3.6K/month.

Cloudflare R2 Standard currently lists $0.015/GB-month and $4.50/million Class A operations: <https://developers.cloudflare.com/r2/pricing/>. A page-per-object archival layout at 3B pages/month would therefore create roughly $13.5K/month of Class A writes before storage, which is why the design uses batched crawl shards.

## Non-negotiable architecture invariants

1. Do not embed content that deterministic change detection proves is unchanged.
2. Do not headlessly render every page by default.
3. Do not require persistent vectors for every crawled page to deliver real-time alerts.
4. Do not compare incompatible embedding model spaces.
5. Do not store one object-store object per page at web scale.
6. Do not use ANN score alone as notification state.
7. Do not run expensive reranking across the entire crawl stream.
8. Do not conflate real-time alerting with historical semantic search.
9. Keep enough provenance to reproduce or re-evaluate delivered matches.
10. Treat exact provider prices as dated capacity inputs.

## Repository responsibilities

The existing repository family provides the primary implementation boundaries:

- [`eal-sync`](https://github.com/embedded-alerts/eal-sync): source ingestion, discovery/fetch orchestration, and durable crawl flow.
- [`eal-api`](https://github.com/embedded-alerts/eal-api) / [`eal-api-server.rs`](https://github.com/embedded-alerts/eal-api-server.rs): authenticated source, alert, match, and search APIs.
- [`eal-lib-core`](https://github.com/embedded-alerts/eal-lib-core): persistence, vector provenance, migrations, and durable state.
- [`eal-libs`](https://github.com/embedded-alerts/eal-libs): shared matching/ranking logic.
- [`eal-interfaces`](https://github.com/embedded-alerts/eal-interfaces): cross-language API and data contracts.
- [`eal-infra`](https://github.com/embedded-alerts/eal-infra): deployment, vector-serving, object-storage, and observability infrastructure.
- [`eal-e2e`](https://github.com/embedded-alerts/eal-e2e): end-to-end evidence.

Create additional crawler/embedder/match service repositories only when operational scaling proves that a separate deployable boundary is needed; do not create service fragmentation merely to mirror conceptual pipeline stages.

## Related work

- [DEN-3461 — source ingestion and model-versioned embedding search](https://linear.app/denman/issue/DEN-3461/embedded-alerts-implement-source-ingestion-and-model-versioned)
- [DEN-3485 — page and query embeddings with model-space isolation](https://linear.app/denman/issue/DEN-3485/persist-multi-view-page-and-query-embeddings-with-model-space)
- [DEN-3487 — bounded external-index discovery adapters](https://linear.app/denman/issue/DEN-3487/implement-bounded-external-index-discovery-adapters)
- [DEN-3460 — match dedupe/cooldown/retry/delivery receipts](https://linear.app/denman/issue/DEN-3460/embedded-alerts-implement-match-dedupe-cooldown-retry-and-delivery)
- [DEN-3462 — deterministic re-evaluation and model/threshold migrations](https://linear.app/denman/issue/DEN-3462/embedded-alerts-add-deterministic-rule-re-evaluation-and)
