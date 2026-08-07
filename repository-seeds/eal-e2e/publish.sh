#!/usr/bin/env bash
set -euo pipefail

repository="embedded-alerts/eal-e2e"
seed_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT

command -v gh >/dev/null 2>&1 || { echo "GitHub CLI is required" >&2; exit 127; }
command -v npm >/dev/null 2>&1 || { echo "npm is required" >&2; exit 127; }
gh auth status --hostname github.com >/dev/null
if gh repo view "$repository" >/dev/null 2>&1; then
  echo "$repository already exists; refusing to overwrite it" >&2
  exit 17
fi

cp -R "$seed_dir"/. "$work_dir"/
rm -f "$work_dir/publish.sh"
npm --prefix "$work_dir" install --package-lock-only --ignore-scripts --no-audit --no-fund
node "$work_dir/scripts/validate-structure.mjs"

git -C "$work_dir" init --initial-branch=main
git -C "$work_dir" config user.name "ORESoftware automation"
git -C "$work_dir" config user.email "11139560+ORESoftware@users.noreply.github.com"
git -C "$work_dir" add --all
git -C "$work_dir" commit -m "bootstrap canonical eal-e2e harness"
gh repo create "$repository" --public \
  --description "Canonical Embedded Alerts end-to-end and contract test harness" \
  --source "$work_dir" --remote origin --push
echo "published https://github.com/$repository"
