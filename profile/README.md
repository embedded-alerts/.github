# Embedded Alerts

Embedded Alerts is a Google Alerts-style platform that discovers new or materially changed web content and matches it to users' saved concepts with **embeddings and semantic similarity**, rather than relying only on literal keyword search.

The core scaling model is reverse semantic search: active user alert vectors form the hot ANN index, while newly discovered webpages are streamed through extraction, deduplication, compact embedding, candidate matching, exact scoring, optional richer reranking, and a durable delivery state machine. Page vectors are transient by default; persistent historical page vectors are a separate **Embedded Search** capability rather than a prerequisite for real-time alerts.

- [Semantic alert architecture and cost guardrails](../docs/SEMANTIC_ALERT_ARCHITECTURE.md)
- [Canonical Linear project](https://linear.app/denman/project/githubcomembedded-alerts-2fb7392497ab)
- [DEN-3461: source ingestion and model-versioned embedding search](https://linear.app/denman/issue/DEN-3461/embedded-alerts-implement-source-ingestion-and-model-versioned)

<!-- org-project-routing:start -->
## Planning and delivery

- [GitHub Project: embedded-alerts-project](https://github.com/orgs/embedded-alerts/projects/1)
- [Linear planning project](https://linear.app/denman/project/githubcomembedded-alerts-2fb7392497ab)
- [Detailed project-routing contract](../docs/PROJECTS.md)

GitHub owns code and delivery evidence; Linear owns planning and dependencies. The linked organization Project provides the cross-repository execution view.
<!-- org-project-routing:end -->

<!-- ore-org-baseline:begin -->
## Planning and governance

- Canonical Linear project: https://linear.app/denman/project/githubcomembedded-alerts-2fb7392497ab
- Organization defaults: https://github.com/embedded-alerts/.github
- Canonical agent policy: https://github.com/embedded-alerts/.github/blob/main/agents.md
- Security policy: https://github.com/embedded-alerts/.github/security/policy

Repositories in this organization use semantic conflict resolution with 3–10 relevant prior commits when useful, full cross-repository context, pull-request delivery, and a hard automated-agent denylist for destructive or history-rewriting operations.
<!-- ore-org-baseline:end -->

<!-- BEGIN MANAGED REPOSITORY RELATIONSHIPS v1 -->
## Repository relationship registry

`embedded-alerts` declares repository roles, dependency edges, cross-organization capabilities, deployment ownership, and the git-submodule/Zed-package contract:

- [Human-readable map](architecture/REPOSITORY_RELATIONSHIPS.md)
- [Machine-readable manifest](architecture/repository-relationships.json)
- [JSON Schema](architecture/repository-relationships.schema.json)

The public registry withholds private repository names and edges.
<!-- END MANAGED REPOSITORY RELATIONSHIPS v1 -->
