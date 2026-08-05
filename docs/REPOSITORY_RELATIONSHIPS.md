<!-- ore-org-baseline:begin -->
# Repository relationships for `embedded-alerts`

This file is rendered from `repository-relationships.json`. The JSON registry is authoritative.

- Audience: `public`
- Repositories represented: **16**
- Relationships represented: **20**
- Inventory digest: `sha256:edf621080b3231ec798f1b9f7c0834ae7bb36aa2f13a216dd23c12d6cb5c3bd0`

## Immutable routing identity

| Field | Value |
|---|---|
| Mapping ID | `context:embedded-alerts` |
| GitHub owner ID | `313129319` |
| Linear project ID | `fa527793-877f-4d09-8331-682df0684915` |
| Linear team ID | `eb8ab169-5afe-4b6f-9cab-3f2aa3e887dc` |

## Repositories

| Repository | Visibility | Roles | Archived |
|---|---|---|---|
| `embedded-alerts/.github` | `public` | `community-health`, `governance`, `relationship-registry` | no |
| `embedded-alerts/eal-api` | `public` | `api-server` | no |
| `embedded-alerts/eal-cli` | `public` | `repository` | no |
| `embedded-alerts/eal-clients` | `public` | `clients` | no |
| `embedded-alerts/eal-dioxus-web` | `public` | `repository` | no |
| `embedded-alerts/eal-infra` | `public` | `infrastructure` | no |
| `embedded-alerts/eal-interfaces` | `public` | `interfaces` | no |
| `embedded-alerts/eal-leptos-web` | `public` | `repository` | no |
| `embedded-alerts/eal-libs` | `public` | `repository` | no |
| `embedded-alerts/eal-mash-web` | `public` | `repository` | no |
| `embedded-alerts/eal-monorepo` | `public` | `monorepo` | no |
| `embedded-alerts/eal-sync` | `public` | `sync` | no |
| `embedded-alerts/embedded-alerts-clients` | `public` | `clients` | no |
| `embedded-alerts/embedded-alerts-libs` | `public` | `repository` | no |
| `embedded-alerts/embedded-alerts-monorepo` | `public` | `monorepo` | no |
| `embedded-alerts/embedded-alerts.github.io` | `public` | `documentation-site` | no |

## Relationships

| From | Type | To | Status | Required |
|---|---|---|---|---|
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-api` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-cli` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-clients` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-dioxus-web` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-infra` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-interfaces` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-leptos-web` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-libs` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-mash-web` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-monorepo` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/eal-sync` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts-clients` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts-libs` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts-monorepo` | `declared` | yes |
| `embedded-alerts/.github` | `governs` | `embedded-alerts/embedded-alerts.github.io` | `declared` | yes |
| `embedded-alerts/eal-api` | `depends_on` | `embedded-alerts/eal-interfaces` | `inferred` | no |
| `embedded-alerts/eal-clients` | `depends_on` | `embedded-alerts/eal-interfaces` | `inferred` | no |
| `embedded-alerts/eal-infra` | `deploys` | `embedded-alerts/eal-monorepo` | `inferred` | no |
| `embedded-alerts/eal-sync` | `depends_on` | `embedded-alerts/eal-interfaces` | `inferred` | no |
| `embedded-alerts/embedded-alerts.github.io` | `documents` | `embedded-alerts/.github` | `inferred` | no |

## Editing relationships

Put reviewed public declarations in `repository-relationships.manual.json`; do not edit the generated registry directly.
Private repository names and private-only relationships belong in the private `approved-private-registry` mirror.
Inferred edges are advisory and must remain visibly labeled until reviewed.
<!-- ore-org-baseline:end -->
