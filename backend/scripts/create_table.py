"""One-shot helper: create the `user_profiles` DynamoDB table on the local
stand-in (`moto_server` or `amazon/dynamodb-local`).

Usage:
    DYNAMODB_ENDPOINT=http://localhost:8000 \\
    USER_PROFILES_TABLE=est-dev-user-profiles \\
    python backend/scripts/create_table.py

Idempotent: skips if the table already exists.
"""
from __future__ import annotations

import os
import sys

import boto3
from botocore.exceptions import ClientError


def main() -> int:
    endpoint = os.environ.get("DYNAMODB_ENDPOINT", "http://localhost:8000")
    table_name = os.environ.get("USER_PROFILES_TABLE", "est-dev-user-profiles")
    region = os.environ.get("AWS_REGION", "ap-southeast-2")

    ddb = boto3.client(
        "dynamodb",
        endpoint_url=endpoint,
        region_name=region,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "dummy"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "dummy"),
    )

    try:
        ddb.create_table(
            TableName=table_name,
            AttributeDefinitions=[{"AttributeName": "user_id", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            BillingMode="PAY_PER_REQUEST",
        )
        print(f"created table: {table_name} on {endpoint}")
        return 0
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print(f"table already exists: {table_name}")
            return 0
        print(f"create_table failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
