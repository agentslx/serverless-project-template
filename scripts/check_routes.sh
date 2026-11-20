#!/usr/bin/env bash
# scripts/check_routes.sh — validate backend/local_proxy/routes.json.
#
# Catches the two most common "added a route, forgot to wire it up" bugs:
#   1. A `language: "rust"`  entry whose handler isn't in `dispatch_rs.rs::dispatch`.
#   2. A `language: "python"` entry whose handler isn't in `local_proxy_py/main.py::HANDLERS`.
#   3. Duplicate {method,path} pairs.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROUTES_JSON="$REPO_ROOT/backend/local_proxy/routes.json"
DISPATCH_RS="$REPO_ROOT/backend/local_proxy/src/dispatch_rs.rs"
HANDLERS_PY="$REPO_ROOT/backend/local_proxy_py/main.py"

python - "$ROUTES_JSON" "$DISPATCH_RS" "$HANDLERS_PY" <<'PY'
import json, re, sys
from pathlib import Path

routes_json = Path(sys.argv[1])
dispatch_rs = Path(sys.argv[2])
handlers_py = Path(sys.argv[3])

cfg = json.loads(routes_json.read_text())
routes = cfg.get("routes", [])

# 1. Rust handlers registered in dispatch_rs.rs (one match arm per name)
rs_src = dispatch_rs.read_text()
rust_registered = set(re.findall(r'"\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*"\s*=>', rs_src))

# 2. Python handlers registered in HANDLERS dict in main.py
py_src = handlers_py.read_text()
py_registered = set(re.findall(r'"\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*"\s*:\s*\w+', py_src))

errors = []
seen = set()

for r in routes:
    key = (r["method"].upper(), r["path"])
    if key in seen:
        errors.append(f"duplicate route: {r['method']} {r['path']}")
    seen.add(key)

    if r["language"] == "rust" and r["handler"] not in rust_registered:
        errors.append(
            f"rust handler {r['handler']!r} is in routes.json "
            f"but missing from dispatch_rs.rs::dispatch"
        )
    if r["language"] == "python" and r["handler"] not in py_registered:
        errors.append(
            f"python handler {r['handler']!r} is in routes.json "
            f"but missing from local_proxy_py/main.py::HANDLERS"
        )

if errors:
    print("routes.json validation FAILED:")
    for e in errors:
        print(f"  • {e}")
    sys.exit(1)

print(f"routes.json OK — {len(routes)} routes "
      f"({sum(1 for r in routes if r['language']=='rust')} rust, "
      f"{sum(1 for r in routes if r['language']=='python')} python)")
PY
