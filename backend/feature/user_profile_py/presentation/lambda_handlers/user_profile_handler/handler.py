"""Lambda handler — GET/PATCH /profile/{user_id} (consolidated)."""
from __future__ import annotations

import json
import os

from shared.modules_py import build_dynamodb_resource
from shared.modules_py.common import init_logging, json_response, error_response
from shared.entities_py import AppError, UserProfilePatch

from feature.user_profile_py.data.datasources import DynamoUserProfileDataSource
from feature.user_profile_py.data.repository import DynamoUserProfileRepository
from feature.user_profile_py.domain.usecases import GetUserProfileUseCase, UpdateUserProfileUseCase

log = init_logging()
_GET_UC: GetUserProfileUseCase | None = None
_UPDATE_UC: UpdateUserProfileUseCase | None = None


def _init():
    global _GET_UC, _UPDATE_UC
    if _GET_UC is None:
        table = os.environ["USER_PROFILES_TABLE"]
        ddb = build_dynamodb_resource()
        repo = DynamoUserProfileRepository(DynamoUserProfileDataSource(ddb, table))
        _GET_UC = GetUserProfileUseCase(repo)
        _UPDATE_UC = UpdateUserProfileUseCase(repo)


def _build_patch(raw: dict) -> UserProfilePatch:
    return UserProfilePatch(
        display_name=raw.get("display_name"),
        avatar_url=raw.get("avatar_url"),
    )


def handler(event: dict, _context=None) -> dict:
    _init()
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    sub = headers.get("x-user-sub", "")
    target = (event.get("pathParameters") or {}).get("user_id") or sub

    if method == "GET":
        if target != sub:
            return json_response(403, {"error": "forbidden"})
        try:
            return json_response(200, _GET_UC.execute(target).to_dict())
        except AppError as e:
            return error_response(e)

    elif method == "PATCH":
        try:
            body = json.loads(event.get("body") or "{}")
        except json.JSONDecodeError:
            return json_response(400, {"error": "bad json"})
        try:
            out = _UPDATE_UC.execute(sub, target, _build_patch(body))
            return json_response(200, out.to_dict())
        except AppError as e:
            return error_response(e)

    return json_response(405, {"error": "method not allowed"})


def invoke(req: dict) -> dict:
    _init()
    method = req.get("method", "GET").upper()
    sub = req.get("headers", {}).get("x-user-sub", "")
    if not sub:
        return {"status": 401, "body": {"error": "missing x-user-sub"}}
    target = req.get("path_params", {}).get("user_id") or sub

    if method == "GET":
        if target != sub:
            return {"status": 403, "body": {"error": "forbidden"}}
        try:
            return {"status": 200, "body": _GET_UC.execute(target).to_dict()}
        except AppError as e:
            return {"status": e.http_status, "body": {"error": e.message}}

    elif method == "PATCH":
        body = req.get("json_body") or {}
        try:
            out = _UPDATE_UC.execute(sub, target, _build_patch(body))
            return {"status": 200, "body": out.to_dict()}
        except AppError as e:
            return {"status": e.http_status, "body": {"error": e.message}}

    return {"status": 405, "body": {"error": "method not allowed"}}
