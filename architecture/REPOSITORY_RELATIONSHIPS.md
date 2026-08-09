# `embedded-alerts` repository relationships

Generated from reviewed policy and the current **public** repository inventory.

- Public repositories declared: **17**
- Private repository names withheld: **0**
- Relationship edges: **63**

## Repository roles

| Repository | Role | Lifecycle |
|---|---|---|
| [`.github`](https://github.com/embedded-alerts/.github) | `organization_governance` | `active` |
| [`eal-interfaces`](https://github.com/embedded-alerts/eal-interfaces) | `interfaces` | `active` |
| [`eal-clients`](https://github.com/embedded-alerts/eal-clients) | `client_sdk` | `active` |
| [`embedded-alerts-clients`](https://github.com/embedded-alerts/embedded-alerts-clients) | `client_sdk` | `active` |
| [`eal-api`](https://github.com/embedded-alerts/eal-api) | `api_service` | `active` |
| [`eal-sync`](https://github.com/embedded-alerts/eal-sync) | `sync_service` | `active` |
| [`eal-mcp-server.rs`](https://github.com/embedded-alerts/eal-mcp-server.rs) | `mcp_server` | `active` |
| [`eal-cli`](https://github.com/embedded-alerts/eal-cli) | `cli` | `active` |
| [`embedded-alerts.github.io`](https://github.com/embedded-alerts/embedded-alerts.github.io) | `site` | `active` |
| [`eal-infra`](https://github.com/embedded-alerts/eal-infra) | `infrastructure` | `active` |
| [`eal-monorepo`](https://github.com/embedded-alerts/eal-monorepo) | `composition_workspace` | `active` |
| [`embedded-alerts-monorepo`](https://github.com/embedded-alerts/embedded-alerts-monorepo) | `composition_workspace` | `active` |
| [`eal-dioxus-web`](https://github.com/embedded-alerts/eal-dioxus-web) | `uncategorized` | `active` |
| [`eal-leptos-web`](https://github.com/embedded-alerts/eal-leptos-web) | `uncategorized` | `active` |
| [`eal-libs`](https://github.com/embedded-alerts/eal-libs) | `uncategorized` | `active` |
| [`eal-mash-web`](https://github.com/embedded-alerts/eal-mash-web) | `uncategorized` | `active` |
| [`embedded-alerts-libs`](https://github.com/embedded-alerts/embedded-alerts-libs) | `uncategorized` | `active` |

## Declared edges

| From | Relationship | To | Status/basis |
|---|---|---|---|
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-api` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-cli` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-clients` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-dioxus-web` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-infra` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-interfaces` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-leptos-web` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-libs` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-mash-web` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-mcp-server.rs` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-monorepo` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-sync` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts-clients` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts-libs` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts-monorepo` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts.github.io` | `inferred` / `role-convention`: organization defaults, safety, and relationship declarations |
| `embedded-alerts/eal-api` | `implements_contracts_from` | `embedded-alerts/eal-interfaces` | `inferred` / `role-convention`: service boundary implements canonical contracts |
| `embedded-alerts/eal-cli` | `calls` | `embedded-alerts/eal-api` | `inferred` / `role-convention`: client uses the product service boundary |
| `embedded-alerts/eal-clients` | `generated_from` | `embedded-alerts/eal-interfaces` | `inferred` / `role-convention`: SDK bindings derive from canonical contracts |
| `embedded-alerts/eal-infra` | `deploys` | `embedded-alerts/eal-api` | `inferred` / `role-convention`: product infrastructure declares runtime resources |
| `embedded-alerts/eal-infra` | `deploys` | `embedded-alerts/eal-cli` | `inferred` / `role-convention`: product infrastructure declares runtime resources |
| `embedded-alerts/eal-infra` | `deploys` | `embedded-alerts/eal-mcp-server.rs` | `inferred` / `role-convention`: product infrastructure declares runtime resources |
| `embedded-alerts/eal-infra` | `deploys` | `embedded-alerts/eal-sync` | `inferred` / `role-convention`: product infrastructure declares runtime resources |
| `embedded-alerts/eal-mcp-server.rs` | `calls` | `embedded-alerts/eal-api` | `inferred` / `role-convention`: agent tools use the authenticated product API |
| `embedded-alerts/eal-mcp-server.rs` | `uses_sdk` | `embedded-alerts/eal-clients` | `inferred` / `role-convention`: agent adapter reuses the typed product SDK |
| `embedded-alerts/eal-mcp-server.rs` | `uses_sdk` | `embedded-alerts/embedded-alerts-clients` | `inferred` / `role-convention`: agent adapter reuses the typed product SDK |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-api` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-cli` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-clients` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-dioxus-web` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-infra` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-interfaces` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-leptos-web` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-libs` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-mash-web` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-mcp-server.rs` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/eal-sync` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/embedded-alerts-clients` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/embedded-alerts-libs` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/embedded-alerts-monorepo` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-monorepo` | `composes` | `embedded-alerts/embedded-alerts.github.io` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/eal-sync` | `synchronizes_with` | `embedded-alerts/eal-api` | `inferred` / `role-convention`: sync exchanges state through the product service boundary |
| `embedded-alerts/eal-sync` | `uses_contracts_from` | `embedded-alerts/eal-interfaces` | `inferred` / `role-convention`: sync payloads follow canonical schemas |
| `embedded-alerts/embedded-alerts-clients` | `generated_from` | `embedded-alerts/eal-interfaces` | `inferred` / `role-convention`: SDK bindings derive from canonical contracts |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-api` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-cli` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-clients` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-dioxus-web` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-infra` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-interfaces` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-leptos-web` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-libs` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-mash-web` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-mcp-server.rs` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-monorepo` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/eal-sync` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/embedded-alerts-clients` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/embedded-alerts-libs` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `embedded-alerts/embedded-alerts-monorepo` | `composes` | `embedded-alerts/embedded-alerts.github.io` | `inferred` / `role-convention`: development workspace and release bill of materials |
| `organization://embedded-alerts` | `reconciles_via` | `platform://opto-sync` | `platform-default` / `platform-policy`: product sync wraps the generic reconciliation engine |
| `organization://embedded-alerts` | `deployed_via` | `platform://ORESoftware/k8s-cluster` | `platform-default` / `platform-policy`: immutable artifacts are promoted by digest through GitOps |
| `organization://embedded-alerts` | `uses_transport_library` | `platform://ORESoftware/mcp-rust-libs` | `platform-default` / `platform-policy`: shared MCP transport and protocol hardening |
| `organization://embedded-alerts` | `packaged_via` | `platform://zed-pkg` | `platform-default` / `platform-policy`: Zed resolves artifacts while submodules compose editable source |

## Composition, service, and observability contract

Git submodules compose editable source; Zed packages resolve packages/artifacts; dual-managed commits must match. Production deploys immutable image digests, not runtime source builds. Cross-service access uses APIs/SDKs/events rather than another service database. MCP uses the product API/SDK. Services emit OpenTelemetry traces, bounded metrics, and correlated structured logs.

## Privacy boundary

This public registry deliberately omits private repository names and edges; the count above makes the boundary explicit.
