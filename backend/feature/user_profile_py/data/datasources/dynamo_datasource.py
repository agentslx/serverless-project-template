from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from botocore.exceptions import ClientError

from shared.entities_py import AppError, AppErrorKind, UserProfile, UserProfilePatch
from feature.user_profile_py.data.models import DynamoUserProfileModel

log = logging.getLogger(__name__)


class DynamoUserProfileDataSource:
    def __init__(self, ddb_resource, table_name: str):
        self.table = ddb_resource.Table(table_name)

    def get(self, user_id: str) -> Optional[UserProfile]:
        try:
            resp = self.table.get_item(Key={"user_id": user_id})
        except ClientError as e:
            log.error("ddb get_item failed: %s", e)
            raise AppError(AppErrorKind.INTERNAL, "dynamodb get_item")
        return DynamoUserProfileModel.from_item(resp.get("Item"))

    def update(self, user_id: str, patch: UserProfilePatch) -> UserProfile:
        now = datetime.now(timezone.utc).isoformat()
        expr_parts = ["#updated_at = :u"]
        expr_names = {"#updated_at": "updated_at"}
        expr_values = {":u": now}
        if patch.display_name is not None:
            expr_parts.append("#display_name = :d")
            expr_names["#display_name"] = "display_name"
            expr_values[":d"] = patch.display_name
        if patch.avatar_url is not None:
            expr_parts.append("#avatar_url = :a")
            expr_names["#avatar_url"] = "avatar_url"
            expr_values[":a"] = patch.avatar_url

        try:
            resp = self.table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET " + ", ".join(expr_parts),
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
                ConditionExpression="attribute_exists(user_id)",
                ReturnValues="ALL_NEW",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise AppError(AppErrorKind.NOT_FOUND)
            log.error("ddb update_item failed: %s", e)
            raise AppError(AppErrorKind.INTERNAL, "dynamodb update_item")
        item = resp.get("Attributes") or {}
        out = DynamoUserProfileModel.from_item(item)
        if out is None:
            raise AppError(AppErrorKind.NOT_FOUND)
        return out
