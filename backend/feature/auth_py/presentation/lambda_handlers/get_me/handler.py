"""Lambda handler — GET /me (Python).

The actual Lambda runtime calls `handler(event, context)`. The local proxy
calls `invoke(req)` directly. Both paths share the same usecase wiring.
"""
from __future__ import annotations

import os

from shared.modules_py import build_dynamodb_resource
from shared.modules_py.common import init_logging, json_response, error_response
from shared.entities_py import AppError

from feature.auth_py.data.datasources import DynamoUserProfileDataSource
from feature.auth_py.data.repository import DynamoAuthRepository
from feature.auth_py.domain.usecases import GetMeUseCase

log = init_logging()


def _build_usecase() -> GetMeUseCase:
    table = os.environ["USER_PROFILES_TABLE"]
    ddb = build_dynamodb_resource()
    return GetMeUseCase(DynamoAuthRepository(DynamoUserProfileDataSource(ddb, table)))


# Pre-built at module import for warm-Lambda reuse.
_USECASE = None
def _usecase() -> GetMeUseCase:
    global _USECASE
    if _USECASE is None:
        _USECASE = _build_usecase()
    return _USECASE


def handler(event: dict, _context=None) -> dict:
    """AWS Lambda entrypoint."""
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    sub = headers.get("x-user-sub", "")
    email = headers.get("x-user-email", "")
    try:
        profile = _usecase().execute(sub, email)
        return json_response(200, profile.to_dict())
    except AppError as e:
        return error_response(e)


def invoke(req: dict) -> dict:
    """Local-proxy entrypoint. `req` is the canonical proxy request shape."""
    sub = req.get("headers", {}).get("x-user-sub", "")
    email = req.get("headers", {}).get("x-user-email", "")
    if not sub:
        return {"status": 401, "body": {"error": "missing x-user-sub"}}
    try:
        profile = _usecase().execute(sub, email)
        return {"status": 200, "body": profile.to_dict()}
    except AppError as e:
        return {"status": e.http_status, "body": {"error": e.message}}
