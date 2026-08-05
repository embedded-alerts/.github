# embedded-alerts organization handbook

> Shared operating defaults for repositories maintained under **embedded-alerts**. Repository-local policy may strengthen these rules but should not silently weaken them.

## Mission

embedded-alerts maintains embeddable alerting, notification, escalation, and integration components. This `.github` repository is the canonical home for shared policy, reusable templates, community health files, and planning links.

## Repository contract

Each active repository must document purpose, ownership, maturity, supported platforms and providers, development and test commands, authoritative event and configuration formats, release and rollback procedures, compatibility policy, and GitHub Project/Linear links. Alerting components should also document severity and state semantics, deduplication, grouping, suppression, routing, retries, idempotency, escalation, acknowledgement, rate limits, quiet hours, accessibility, retention, and degraded modes.

## Change workflow

1. Anchor work in an issue, Linear item, or documented maintenance objective.
2. Keep branches and pull requests focused.
3. Explain motivation, scope, notification and user impact, validation, compatibility, migration, and rollback.
4. Test duplicate, storm, suppression, acknowledgement, escalation, provider failure, rate limit, timeout, retry, and accessibility paths as relevant.
5. Resolve conflicts semantically by reconstructing both sides' intent.
6. Prefer squash merges for focused work unless commit structure materially improves auditability.

## Evidence, security, and documentation

Pull requests should include reproducible commands, synthetic events, expected and observed routing and state transitions, negative-path and volume evidence, documentation updates, and CI or local-equivalent results. Never commit credentials, provider tokens, private incident data, production contact details, or sensitive logs. Follow `SECURITY.md` for private reporting. Keep notification semantics, limits, privacy, accessibility, compatibility, and important operational decisions explicit.

## Planning ownership

GitHub owns code, reviews, checks, releases, and delivery evidence. Linear owns priority, dependencies, sequencing, and cross-project planning. The organization GitHub Project is the cross-repository execution view; see `PROJECTS.md` for routing details.

## Organization health

- [ ] Profiles, descriptions, topics, and READMEs are current.
- [ ] Community health files and reusable issue/PR guidance are present.
- [ ] Severity, deduplication, routing, retries, escalation, acknowledgement, limits, and retention are documented.
- [ ] Required checks cover alert storms, duplicate delivery, provider failure, accessibility, compatibility, and supply-chain risk.
- [ ] Stale repositories are archived or clearly marked.
- [ ] GitHub Project and Linear links resolve and reflect completed work.
