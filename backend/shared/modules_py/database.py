"""Boto3 DynamoDB resource bootstrap.

Reads `AWS_REGION` (default `ap-southeast-2`) and the optional
`DYNAMODB_ENDPOINT` override (used for `amazon/dynamodb-local`).
"""
from __future__ import annotations

import os
import boto3


def build_dynamodb_resource():
    kwargs = {"region_name": os.environ.get("AWS_REGION", "ap-southeast-2")}
    endpoint = os.environ.get("DYNAMODB_ENDPOINT")
    if endpoint:
        kwargs["endpoint_url"] = endpoint
    return boto3.resource("dynamodb", **kwargs)
