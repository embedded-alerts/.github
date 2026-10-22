# Contributing to `embedded-alerts` repositories

## Durable engineering policy

- This repository defines public organization-wide defaults for `embedded-alerts`.
- Never commit credentials, private keys, access tokens, customer data, or private-repository inventories.
- Resolve Git conflicts semantically: inspect both sides, the merge base, nearby tests and contracts, and normally 3–10 relevant prior commits. Never blindly select all of `ours` or all of `theirs`.
- Prefer focused pull requests, explicit validation, non-destructive Git operations, and documented tradeoffs.
- Cross-repository integration uses versioned interfaces, APIs, SDKs, events, or explicitly owned replicated read models. Services do not reach into another service's database by default.
- `*-infra` repositories and `*-monorepo` application source remain separate. A `*-infra` repository must never appear as a Git submodule under `*-monorepo/apps`.
- Git submodules are reserved for explicitly coordinated editable source composition. Zed packages or immutable artifacts are preferred for package dependencies. Production deploys immutable artifacts or OCI digests, not source clones.

## Pull requests

Keep pull requests focused and reviewable. Describe motivation, changed behavior, interface or migration impact, security considerations, validation performed, and rollback or compatibility plans where relevant.

<!-- ore-org-baseline:begin -->
Thank you for contributing to repositories owned by [`embedded-alerts`](https://github.com/embedded-alerts). Repository-local instructions take precedence when they are stricter.

## Before proposing a change

1. Read the repository README, contribution notes, lowercase `agents.md`, architecture documentation, linked issues, and relevant [Linear project](https://linear.app/denman/project/githubcomembedded-alerts-2fb7392497ab).
2. Confirm the authoritative source repository and whether files are generated, vendored, mirrored, or owned by another repository.
3. Fetch current remote state and preserve concurrent work. Avoid git rebase in favor of git merge.
4. Do not use `git stash`, `git reset`, `git clean`, `git filter-repo`, force-push, destructive worktree/submodule operations, or broad deletion/rewrite commands without exact authorization.
5. Never include secrets, credentials, customer data, legal records, or other private information in issues, commits, test fixtures, screenshots, or logs.

## Pull requests

Use a focused feature branch and a draft pull request. Link the relevant issue or Linear work; explain behavior, risk, security impact, migration and rollback considerations, tests, and cross-repository dependencies. Resolve conflicts semantically with full context—normally including the merge base and 3–10 relevant commits—rather than selecting one side wholesale. Run all affected checks and scan the complete worktree for conflict markers.

External GitHub Actions must be pinned to full commit SHAs. Workflows must use explicit least-privilege permissions, explicit timeouts, and non-persisted checkout credentials.
<!-- ore-org-baseline:end -->

## Rust-first scripts and automation

**No new Python scripts.** Use Rust for first-party CI, builds, tests, codegen, migrations, deployments, releases, audits, and developer/repository maintenance. Prefer Rust CLIs or `cargo xtask`; shell/YAML wrappers should stay small.

Existing Python automation is migration debt. Inventory each script and its callers and migrate only after proving equivalent Rust CLI flags, exit codes, errors, output contracts, security checks, and supported platforms. Run positive, negative and end-to-end tests on the actual PR head before removing Python or redirecting workflow calls. An organizational policy change does not prove a script migration.

**Python application/product code is permitted only as an explicitly documented special exception**, with an owner, actual app purpose, scope, justification and review criteria. App-specific tests may be in scope; CI scripts, generators, migrations and maintenance automation are not application code merely by renaming them.

New Rust tools should document reproducible Cargo builds/runs and carry applicable `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test` and true backend/CLI smoke checks. Source-free canaries do not establish source-level execution.

The canonical organization `.github` repo provides contributor guidance but GitHub does not automatically distribute arbitrary agent instructions or CI workflows to sibling repositories; explicitly synchronize local `AGENTS.md` and enable enforcement separately.

