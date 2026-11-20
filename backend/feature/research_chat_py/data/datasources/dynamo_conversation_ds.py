"""DynamoDB datasource for conversation persistence."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key


class DynamoConversationDataSource:
    def __init__(self, ddb_resource, table_name: str):
        self._table = ddb_resource.Table(table_name)

    def get_item(self, user_id: str, conversation_id: str) -> Optional[dict]:
        resp = self._table.get_item(Key={"user_id": user_id, "conversation_id": conversation_id})
        return resp.get("Item")

    def query_by_user(self, user_id: str) -> list[dict]:
        resp = self._table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            ProjectionExpression="user_id, conversation_id, title, created_at, updated_at",
        )
        return resp.get("Items", [])

    def put_item(self, item: dict) -> None:
        self._table.put_item(Item=item)

    def append_message(self, user_id: str, conversation_id: str, message: dict) -> None:
        self._table.update_item(
            Key={"user_id": user_id, "conversation_id": conversation_id},
            UpdateExpression="SET messages = list_append(if_not_exists(messages, :empty), :msg), updated_at = :now",
            ExpressionAttributeValues={
                ":msg": [message],
                ":empty": [],
                ":now": datetime.now(timezone.utc).isoformat(),
            },
        )
