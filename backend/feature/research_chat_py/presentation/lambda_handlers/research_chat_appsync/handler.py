"""Lambda handler — consolidated AppSync resolver for research chat queries."""
from __future__ import annotations

import json
import os

import boto3

from feature.research_chat_py.data.datasources.dynamo_conversation_ds import (
    DynamoConversationDataSource,
)
from feature.research_chat_py.data.repository.conversation_repository_impl import (
    DynamoConversationRepository,
)
from feature.research_chat_py.domain.usecases.get_conversation import (
    GetConversationUseCase,
)
from feature.research_chat_py.domain.usecases.list_conversations import (
    ListConversationsUseCase,
)

_GET_UC: GetConversationUseCase | None = None
_LIST_UC: ListConversationsUseCase | None = None
CONVERSATIONS_TABLE = os.environ.get("CONVERSATIONS_TABLE", "")


def _init():
    global _GET_UC, _LIST_UC
    if _GET_UC is None:
        ddb = boto3.resource("dynamodb")
        ds = DynamoConversationDataSource(ddb, CONVERSATIONS_TABLE)
        repo = DynamoConversationRepository(ds)
        _GET_UC = GetConversationUseCase(repo)
        _LIST_UC = ListConversationsUseCase(repo)


def _handle_get_conversation(event):
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    sub = headers.get("x-user-sub", "")
    conversation_id = (event.get("pathParameters") or {}).get("conversation_id", "")

    if not sub or not conversation_id:
        return {"statusCode": 400, "body": json.dumps({"error": "missing params"})}

    conv = _GET_UC.execute(sub, conversation_id)
    if not conv:
        return {"statusCode": 404, "body": json.dumps({"error": "not found"})}

    return {"statusCode": 200, "body": json.dumps(conv.to_dict())}


def _handle_list_conversations(event):
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    sub = headers.get("x-user-sub", "")

    if not sub:
        return {"statusCode": 401, "body": json.dumps({"error": "unauthorized"})}

    conversations = _LIST_UC.execute(sub)
    return {
        "statusCode": 200,
        "body": json.dumps([c.to_dict() for c in conversations]),
    }


_ROUTES = {
    "getConversation": _handle_get_conversation,
    "listConversations": _handle_list_conversations,
}


def handler(event, _context=None):
    _init()
    action = event.get("action", "")

    route_fn = _ROUTES.get(action)
    if route_fn:
        return route_fn(event)

    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("path", "")

    if "conversations" in path and method == "GET":
        conversation_id = (event.get("pathParameters") or {}).get("conversation_id")
        if conversation_id:
            return _handle_get_conversation(event)
        return _handle_list_conversations(event)

    return {"statusCode": 400, "body": json.dumps({"error": f"unknown action: {action}"})}


def invoke(req: dict) -> dict:
    _init()
    sub = req.get("headers", {}).get("x-user-sub", "")
    if not sub:
        return {"status": 401, "body": {"error": "missing x-user-sub"}}

    action = req.get("action", "")
    if action == "getConversation":
        conversation_id = req.get("path_params", {}).get("conversation_id", "")
        if not conversation_id:
            return {"status": 400, "body": {"error": "missing conversation_id"}}
        conv = _GET_UC.execute(sub, conversation_id)
        if not conv:
            return {"status": 404, "body": {"error": "not found"}}
        return {"status": 200, "body": conv.to_dict()}

    elif action == "listConversations":
        conversations = _LIST_UC.execute(sub)
        return {"status": 200, "body": [c.to_dict() for c in conversations]}

    return {"status": 400, "body": {"error": f"unknown action: {action}"}}
