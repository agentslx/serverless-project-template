"""Lambda handler — Cognito PostConfirmation_ConfirmSignUp trigger (Python).

Cognito invokes this synchronously; we MUST return the original event back.
"""
from __future__ import annotations

import logging
import os

from shared.modules_py import build_dynamodb_resource
from shared.modules_py.common import init_logging

from feature.auth_py.data.datasources import DynamoUserProfileDataSource
from feature.auth_py.data.repository import DynamoAuthRepository
from feature.auth_py.domain.usecases import PostConfirmationUseCase

log = init_logging()
_USECASE: PostConfirmationUseCase | None = None


def _usecase() -> PostConfirmationUseCase:
    global _USECASE
    if _USECASE is None:
        table = os.environ["USER_PROFILES_TABLE"]
        ddb = build_dynamodb_resource()
        _USECASE = PostConfirmationUseCase(
            DynamoAuthRepository(DynamoUserProfileDataSource(ddb, table))
        )
    return _USECASE


def handler(event: dict, _context=None) -> dict:
    attrs = (event.get("request") or {}).get("userAttributes") or {}
    sub = attrs.get("sub", "")
    email = attrs.get("email", "")
    log.info("post-confirmation trigger sub=%s email=%s", sub, email)
    if sub:
        try:
            _usecase().execute(sub, email)
        except Exception as e:  # noqa: BLE001 — must never fail the Cognito flow
            logging.warning("seed user_profile failed: %s", e)
    return event
