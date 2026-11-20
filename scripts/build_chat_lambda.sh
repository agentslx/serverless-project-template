#!/usr/bin/env bash
# scripts/build_chat_lambda.sh — build the Docker image for the chat agent Lambda.
#
# Produces a container image tagged `chat-agent-lambda:latest`.
# In CI/CD this is pushed to ECR; locally it's used for testing.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FEATURE_DIR="$REPO_ROOT/backend/feature/research_chat_py"

if [ -t 1 ]; then
    C_HEAD=$'\033[1;36m'; C_OK=$'\033[1;32m'; C_END=$'\033[0m'
else
    C_HEAD=""; C_OK=""; C_END=""
fi
log() { printf '%s[build_chat]%s %s\n' "$C_HEAD" "$C_END" "$*"; }

log "Building chat agent Lambda Docker image..."

docker build \
    --platform linux/arm64 \
    -t chat-agent-lambda:latest \
    -f "$FEATURE_DIR/Dockerfile" \
    "$FEATURE_DIR"

log "Done. Image: chat-agent-lambda:latest"
printf '  %s✓%s To push: docker tag chat-agent-lambda:latest <ECR_URI>:latest && docker push <ECR_URI>:latest\n' "$C_OK" "$C_END"
