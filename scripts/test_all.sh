#!/usr/bin/env bash
# scripts/test_all.sh — run every test the template ships with.
#   • cargo test  --workspace             (Rust unit + integration)
#   • pytest      backend/feature/*_py    (Python unit)
#   • check_routes.sh                     (validates routes.json)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -t 1 ]; then
    C_HEAD=$'\033[1;36m'; C_OK=$'\033[1;32m'; C_END=$'\033[0m'
else
    C_HEAD=""; C_OK=""; C_END=""
fi
log()  { printf '%s[test_all]%s %s\n' "$C_HEAD" "$C_END" "$*"; }
ok()   { printf '  %s✓%s %s\n'        "$C_OK"   "$C_END" "$*"; }

# shellcheck disable=SC1091
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"

log "1/3  cargo test --workspace"
( cd "$REPO_ROOT/backend" && cargo test --workspace )
ok "rust tests pass"

log "2/3  pytest backend/feature/*_py"
( cd "$REPO_ROOT/backend" && python -m pytest -q feature/auth_py feature/user_profile_py )
ok "python tests pass"

log "3/3  routes.json validation"
"$REPO_ROOT/scripts/check_routes.sh"
ok "routes.json clean"

log "all green."
