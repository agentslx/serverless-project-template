"""Health-check Lambda — sample Python-only feature.

Wired into routes.json as `language: "python"` so calls to GET /api/health
go through the Rust proxy → Python sub-server → here.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone


def handler(_event: dict, _context=None) -> dict:
    payload = {
        "status": "ok",
        "ts": datetime.now(timezone.utc).isoformat(),
        "flavour": os.environ.get("FLAVOR", "dev"),
        "language": "python",
    }
    import json
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload),
    }


def invoke(_req: dict) -> dict:
    return {
        "status": 200,
        "body": {
            "status": "ok",
            "ts": datetime.now(timezone.utc).isoformat(),
            "flavour": os.environ.get("FLAVOR", "dev"),
            "language": "python",
        },
    }
