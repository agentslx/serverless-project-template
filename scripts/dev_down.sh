#!/usr/bin/env bash
# scripts/dev_down.sh — stop everything started by `scripts/dev_up.sh`.
#
# Reads .run/dev_pids and SIGTERMs each process. Falls back to fuser/pkill
# for the ports + binaries in case the pid file is stale.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$REPO_ROOT/.run/dev_pids"

if [ -t 1 ]; then
    C_HEAD=$'\033[1;36m'; C_OK=$'\033[1;32m'; C_END=$'\033[0m'
else
    C_HEAD=""; C_OK=""; C_END=""
fi
log() { printf '%s[dev_down]%s %s\n' "$C_HEAD" "$C_END" "$*"; }
ok()  { printf '  %s✓%s %s\n'        "$C_OK"   "$C_END" "$*"; }

if [ -f "$PID_FILE" ]; then
    while IFS=: read -r pid name; do
        [ -z "${pid:-}" ] && continue
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null && ok "killed ${name} (pid ${pid})"
        fi
    done < "$PID_FILE"
fi

# Belt-and-braces: free our ports + matching processes.
for port in 8000 9000 9001; do
    if command -v fuser >/dev/null 2>&1; then
        fuser -k "${port}/tcp" 2>/dev/null && ok "freed :${port}" || true
    fi
done
pkill -9 -f "moto_server" 2>/dev/null || true
pkill -9 -f "local_proxy_py/main.py" 2>/dev/null || true
pkill -9 -f "target/debug/local_proxy" 2>/dev/null || true

rm -f "$PID_FILE"
log "done."
