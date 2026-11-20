"""WebSocket $connect/$disconnect handler — validates JWT and manages connections."""
from __future__ import annotations

import base64
import json
import os
import time

import boto3

_DDB = None
_TABLE_NAME = os.environ.get("CONNECTIONS_TABLE", "")


def _ddb():
    global _DDB
    if _DDB is None:
        _DDB = boto3.resource("dynamodb").Table(_TABLE_NAME)
    return _DDB


def _verify_token(token: str) -> dict | None:
    """Minimal JWT verification — decode payload and check expiry."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1] + "=" * (4 - len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        if claims.get("exp", 0) < time.time():
            return None
        return claims
    except Exception:
        return None


def _handle_connect(event):
    query_params = event.get("queryStringParameters") or {}
    token = query_params.get("token", "")

    if not token:
        return {"statusCode": 401, "body": "Missing token"}

    claims = _verify_token(token)
    if not claims:
        return {"statusCode": 401, "body": "Invalid token"}

    connection_id = event["requestContext"]["connectionId"]
    user_id = claims.get("sub", "")

    _ddb().put_item(
        Item={
            "connection_id": connection_id,
            "user_id": user_id,
            "ttl": int(time.time()) + 7200,
        }
    )

    return {"statusCode": 200, "body": "Connected"}


def _handle_disconnect(event):
    connection_id = event["requestContext"]["connectionId"]

    try:
        _ddb().delete_item(Key={"connection_id": connection_id})
    except Exception:
        pass

    return {"statusCode": 200, "body": "Disconnected"}


def handler(event, _context=None):
    route_key = event.get("requestContext", {}).get("routeKey", "")

    if route_key == "$connect":
        return _handle_connect(event)
    elif route_key == "$disconnect":
        return _handle_disconnect(event)

    return {"statusCode": 400, "body": "Unknown route"}
