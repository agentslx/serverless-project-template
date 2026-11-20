"""Tiny logging + JSON helpers used by every Python Lambda handler."""
from __future__ import annotations

import json
import logging
import os
from typing import Any


def init_logging() -> logging.Logger:
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
    return logging.getLogger("est")


def json_response(status: int, body: Any) -> dict:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def error_response(err) -> dict:
    status = getattr(err, "http_status", 500)
    return json_response(status, {"error": str(err)})
