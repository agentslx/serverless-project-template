"""Mapping between DynamoDB items and domain entities."""
from __future__ import annotations

from feature.research_chat_py.domain.entities.conversation import (
    ChatSource,
    Conversation,
    Message,
)


def conversation_to_item(conv: Conversation) -> dict:
    return {
        "user_id": conv.user_id,
        "conversation_id": conv.conversation_id,
        "title": conv.title or "",
        "messages": [message_to_map(m) for m in conv.messages],
        "created_at": conv.created_at,
        "updated_at": conv.updated_at,
    }


def item_to_conversation(item: dict) -> Conversation:
    return Conversation(
        user_id=item["user_id"],
        conversation_id=item["conversation_id"],
        title=item.get("title") or None,
        messages=[map_to_message(m) for m in item.get("messages", [])],
        created_at=item.get("created_at", ""),
        updated_at=item.get("updated_at", ""),
    )


def message_to_map(msg: Message) -> dict:
    return {
        "message_id": msg.message_id,
        "role": msg.role,
        "content": msg.content,
        "timestamp": msg.timestamp,
        "sources": [{"url": s.url, "title": s.title} for s in msg.sources],
        "report_url": msg.report_url,
    }


def map_to_message(m: dict) -> Message:
    return Message(
        message_id=m["message_id"],
        role=m["role"],
        content=m["content"],
        timestamp=m["timestamp"],
        sources=[ChatSource(url=s["url"], title=s.get("title")) for s in m.get("sources", [])],
        report_url=m.get("report_url"),
    )
