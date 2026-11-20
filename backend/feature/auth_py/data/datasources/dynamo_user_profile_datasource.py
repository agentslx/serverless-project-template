"""Talks to the `user_profiles` DynamoDB table — auth feature scope only."""
from __future__ import annotations

import logging
from typing import Optional

from botocore.exceptions import ClientError

from shared.entities_py import AppError, AppErrorKind, UserProfile
from feature.auth_py.data.models import DynamoUserProfileModel

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

    def put_if_absent(self, profile: UserProfile) -> None:
        try:
            self.table.put_item(
                Item=DynamoUserProfileModel.to_item(profile),
                ConditionExpression="attribute_not_exists(user_id)",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return  # idempotent
            log.error("ddb put_item failed: %s", e)
            raise AppError(AppErrorKind.INTERNAL, "dynamodb put_item")
