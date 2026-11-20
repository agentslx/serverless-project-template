#!/usr/bin/env bash
# scripts/package_py_lambdas.sh — bundle each Python Lambda handler into a zip
# that AWS Lambda can run.
#
# Layout produced (mirrors `cargo lambda build` output for symmetry):
#   backend/target/python_lambda/<handler_name>/
#       handler.py
#       feature/...
#       shared/...
#
# Pulumi (`iac/application/lambdas.py`) reads from this directory.
#
# Re-run after any code change touching feature/*_py or shared/*_py.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$REPO_ROOT/backend"
OUT_DIR="$BACKEND/target/python_lambda"

if [ -t 1 ]; then
    C_HEAD=$'\033[1;36m'; C_OK=$'\033[1;32m'; C_END=$'\033[0m'
else
    C_HEAD=""; C_OK=""; C_END=""
fi
log() { printf '%s[pkg_py]%s %s\n' "$C_HEAD" "$C_END" "$*"; }
ok()  { printf '  %s✓%s %s\n'      "$C_OK"   "$C_END" "$*"; }

# Discover all Python Lambda handlers: feature/*_py/presentation/lambda_handlers/<name>/handler.py
mapfile -t HANDLERS < <(find "$BACKEND/feature" \
    -path "*/presentation/lambda_handlers/*/handler.py" \
    -mindepth 5 -maxdepth 6 2>/dev/null)

if [ "${#HANDLERS[@]}" -eq 0 ]; then
    log "no python handlers found — nothing to do"
    exit 0
fi

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

for handler_path in "${HANDLERS[@]}"; do
    handler_dir="$(dirname "$handler_path")"
    handler_name="$(basename "$handler_dir")"
    feature_dir="$(echo "$handler_path" | sed -E 's#(.*/feature/[^/]+)/.*#\1#')"
    feature_name="$(basename "$feature_dir")"   # e.g. user_profile_py

    pkg_dir="$OUT_DIR/${handler_name}"
    log "packaging ${feature_name}::${handler_name} → ${pkg_dir##*/}"
    mkdir -p "$pkg_dir/feature/${feature_name}" "$pkg_dir/shared"

    # Copy the handler.py to the package root (Lambda runtime expects it there).
    cp "$handler_path" "$pkg_dir/handler.py"

    # Copy the rest of the feature module (preserving import paths) and shared/.
    rsync -a --exclude='__pycache__' --exclude='tests' \
          --exclude='presentation/lambda_handlers' \
          "$feature_dir/" "$pkg_dir/feature/${feature_name}/"
    # Re-add only the handler module's package files (not other handlers).
    mkdir -p "$pkg_dir/feature/${feature_name}/presentation/lambda_handlers/${handler_name}"
    rsync -a --exclude='__pycache__' \
          "$handler_dir/" "$pkg_dir/feature/${feature_name}/presentation/lambda_handlers/${handler_name}/"
    # Make the intermediate dirs proper python packages.
    touch "$pkg_dir/feature/__init__.py"
    touch "$pkg_dir/feature/${feature_name}/presentation/__init__.py" 2>/dev/null || true
    touch "$pkg_dir/feature/${feature_name}/presentation/lambda_handlers/__init__.py" 2>/dev/null || true

    # Shared modules.
    rsync -a --exclude='__pycache__' "$BACKEND/shared/entities_py" "$pkg_dir/shared/"
    rsync -a --exclude='__pycache__' "$BACKEND/shared/modules_py"  "$pkg_dir/shared/"
    touch "$pkg_dir/shared/__init__.py"

    ok "${handler_name}: $(du -sh "$pkg_dir" | cut -f1)"
done

log "all python handlers packaged at $OUT_DIR"
