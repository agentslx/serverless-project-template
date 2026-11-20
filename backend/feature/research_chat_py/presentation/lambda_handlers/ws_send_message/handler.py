"""WebSocket sendMessage handler — runs agent pipeline, streams chunks back."""
from __future__ import annotations

import json
import os
import traceback

import boto3

from feature.research_chat_py.data.datasources.dynamo_conversation_ds import (
    DynamoConversationDataSource,
)
from feature.research_chat_py.data.datasources.s3_report_ds import S3ReportDataSource
from feature.research_chat_py.data.repository.conversation_repository_impl import (
    DynamoConversationRepository,
)
from feature.research_chat_py.domain.agents.orchestrator import create_orchestrator
from feature.research_chat_py.domain.usecases.send_message import SendMessageUseCase

_UC: SendMessageUseCase | None = None

CONVERSATIONS_TABLE = os.environ.get("CONVERSATIONS_TABLE", "")
CONNECTIONS_TABLE = os.environ.get("CONNECTIONS_TABLE", "")
REPORTS_BUCKET = os.environ.get("REPORTS_BUCKET", "")
WEBSOCKET_ENDPOINT = os.environ.get("WEBSOCKET_ENDPOINT", "")


def _uc() -> SendMessageUseCase:
    global _UC
    if _UC is None:
        ddb = boto3.resource("dynamodb")
        s3 = boto3.client("s3")
        conv_ds = DynamoConversationDataSource(ddb, CONVERSATIONS_TABLE)
        repo = DynamoConversationRepository(conv_ds)
        report_ds = S3ReportDataSource(s3, REPORTS_BUCKET)
        orchestrator = create_orchestrator()
        _UC = SendMessageUseCase(repo, report_ds, orchestrator)
    return _UC


def _post_to_connection(connection_id: str, data: dict) -> None:
    """Send a message back to the WebSocket client."""
    apigw = boto3.client(
        "apigatewaymanagementapi",
        endpoint_url=WEBSOCKET_ENDPOINT,
    )
    try:
        apigw.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data).encode("utf-8"),
        )
    except apigw.exceptions.GoneException:
        pass


def _get_user_id(connection_id: str) -> str:
    """Look up user_id from connections table."""
    ddb = boto3.resource("dynamodb")
    table = ddb.Table(CONNECTIONS_TABLE)
    resp = table.get_item(Key={"connection_id": connection_id})
    item = resp.get("Item", {})
    return item.get("user_id", "")


def handler(event, _context=None):
    connection_id = event["requestContext"]["connectionId"]
    body = json.loads(event.get("body", "{}"))

    content = body.get("content", "")
    conversation_id = body.get("conversation_id")
    generate_report = body.get("generate_report", False)

    if not content:
        _post_to_connection(connection_id, {"type": "error", "error": "Empty message"})
        return {"statusCode": 400}

    user_id = _get_user_id(connection_id)
    if not user_id:
        _post_to_connection(connection_id, {"type": "error", "error": "Unauthorized"})
        return {"statusCode": 401}

    def on_chunk(chunk: str):
        _post_to_connection(connection_id, {"type": "chunk", "content": chunk})

    try:
        message = _uc().execute(
            user_id=user_id,
            content=content,
            conversation_id=conversation_id,
            generate_report=generate_report,
            on_chunk=on_chunk,
        )

        _post_to_connection(connection_id, {
            "type": "complete",
            "message": message.to_dict(),
            "conversation_id": conversation_id or message.message_id,
        })

    except Exception as e:
        traceback.print_exc()
        _post_to_connection(connection_id, {
            "type": "error",
            "error": str(e),
        })

    return {"statusCode": 200}
