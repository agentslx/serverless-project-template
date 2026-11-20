#!/usr/bin/env bash
# scripts/dev_up.sh — bring up the full local dev stack in the background.
#
# Pieces:
#   moto_server        :8000   DynamoDB stand-in (no Docker)
#   local_proxy_py     :9001   Python sub-server (FastAPI)
#   local_proxy (Rust) :9000   single FE entrypoint
#   user-app           :3000   (managed by Emergent supervisor — not (re)started here)
#   admin-app          :3001   (separate React app — start manually with `yarn start`)
#
# Logs in /tmp/est-*.log, PIDs in .run/dev_pids.
# `scripts/dev_down.sh` tears the whole thing down.
#
# Idempotent — re-running will free busy ports first.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$REPO_ROOT/.run"
mkdir -p "$RUN_DIR"
PID_FILE="$RUN_DIR/dev_pids"
: > "$PID_FILE"

if [ -t 1 ]; then
    C_HEAD=$'\033[1;36m'; C_OK=$'\033[1;32m'; C_END=$'\033[0m'
else
    C_HEAD=""; C_OK=""; C_END=""
fi
log() { printf '%s[dev_up]%s %s\n' "$C_HEAD" "$C_END" "$*"; }
ok()  { printf '  %s✓%s %s\n'      "$C_OK"   "$C_END" "$*"; }

# Source rust env (may not be on PATH in non-interactive shells).
# shellcheck disable=SC1091
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"

# Free any port that's already in use so we don't end up with dual processes.
free_port() {
    local port="$1"
    if command -v fuser >/dev/null 2>&1; then
        fuser -k "${port}/tcp" >/dev/null 2>&1 || true
    fi
}

start_bg() {
    local name="$1"; shift
    local logfile="/tmp/est-${name}.log"
    log "starting ${name} … (log: ${logfile})"
    ( "$@" >"$logfile" 2>&1 & echo "$!:${name}" >> "$PID_FILE" ) &
    wait $!  # let the subshell finish writing the PID line
}

wait_port() {
    local host="$1" port="$2" name="$3"
    for _ in $(seq 1 40); do
        if (echo > "/dev/tcp/${host}/${port}") 2>/dev/null; then
            ok "${name} on ${host}:${port}"
            return 0
        fi
        sleep 0.25
    done
    echo "ERROR: ${name} failed to come up on ${host}:${port}; tail of its log:" >&2
    tail -n 20 "/tmp/est-${name}.log" >&2 || true
    return 1
}

# ── 1. moto_server (DynamoDB stand-in) ───────────────────────────────────────
free_port 8000
start_bg moto moto_server -p 8000
wait_port 127.0.0.1 8000 moto

# ── 2. create the user_profiles table ────────────────────────────────────────
log "ensuring user_profiles table exists…"
DYNAMODB_ENDPOINT=http://localhost:8000 \
USER_PROFILES_TABLE=est-dev-user-profiles \
AWS_REGION=ap-southeast-2 \
AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
python "$REPO_ROOT/backend/scripts/create_table.py"

# ── 3. local_proxy_py (FastAPI :9001) ────────────────────────────────────────
free_port 9001
( cd "$REPO_ROOT/backend/local_proxy_py" && \
  USER_PROFILES_TABLE=est-dev-user-profiles \
  DYNAMODB_ENDPOINT=http://localhost:8000 \
  AWS_REGION=ap-southeast-2 \
  AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
  PORT=9001 \
  nohup python main.py >/tmp/est-local_proxy_py.log 2>&1 & echo "$!:local_proxy_py" >> "$PID_FILE"
)
wait_port 127.0.0.1 9001 local_proxy_py

# ── 4. local_proxy (Rust :9000) ──────────────────────────────────────────────
log "ensuring local_proxy is built…"
( cd "$REPO_ROOT/backend" && cargo build --quiet -p local_proxy )
free_port 9000
( cd "$REPO_ROOT/backend" && \
  USER_PROFILES_TABLE=est-dev-user-profiles \
  DYNAMODB_ENDPOINT=http://localhost:8000 \
  AWS_REGION=ap-southeast-2 \
  AWS_ACCESS_KEY_ID=dummy AWS_SECRET_ACCESS_KEY=dummy \
  ROUTES_JSON="$REPO_ROOT/backend/local_proxy/routes.json" \
  nohup target/debug/local_proxy >/tmp/est-local_proxy.log 2>&1 & echo "$!:local_proxy" >> "$PID_FILE"
)
wait_port 127.0.0.1 9000 local_proxy

cat <<EOF

${C_OK}────────────────────────────────────────────────────────────────${C_END}
 ${C_OK}✓${C_END}  Dev stack up.

   moto              :8000   /tmp/est-moto.log
   local_proxy_py    :9001   /tmp/est-local_proxy_py.log
   local_proxy (Rust):9000   /tmp/est-local_proxy.log

 PIDs in ${PID_FILE}.

 Smoke-test:
   curl http://localhost:9000/api/health
   curl -H 'x-user-sub: u-1' -H 'x-user-email: a@b.c' http://localhost:9000/api/me

 Tear it all down:
   scripts/dev_down.sh
${C_OK}────────────────────────────────────────────────────────────────${C_END}
EOF
