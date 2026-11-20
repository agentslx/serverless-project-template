"""Domain entities for the research chat feature."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class ChatSource:
    url: str
    title: Optional[str] = None

    def to_dict(self) -> dict:
        return {"url": self.url, "title": self.title}

    @classmethod
    def from_dict(cls, d: dict) -> ChatSource:
        return cls(url=d["url"], title=d.get("title"))


@dataclass
class Message:
    message_id: str
    role: str
    content: str
    timestamp: str
    sources: list[ChatSource] = field(default_factory=list)
    report_url: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "sources": [s.to_dict() for s in self.sources],
            "report_url": self.report_url,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Message:
        return cls(
            message_id=d["message_id"],
            role=d["role"],
            content=d["content"],
            timestamp=d["timestamp"],
            sources=[ChatSource.from_dict(s) for s in d.get("sources", [])],
            report_url=d.get("report_url"),
        )

    @classmethod
    def new_user_message(cls, content: str) -> Message:
        return cls(
            message_id=str(uuid.uuid4()),
            role="user",
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @classmethod
    def new_assistant_message(
        cls,
        content: str,
        sources: list[ChatSource] | None = None,
        report_url: str | None = None,
    ) -> Message:
        return cls(
            message_id=str(uuid.uuid4()),
            role="assistant",
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            sources=sources or [],
            report_url=report_url,
        )


@dataclass
class Conversation:
    user_id: str
    conversation_id: str
    title: Optional[str] = None
    messages: list[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "title": self.title,
            "messages": [m.to_dict() for m in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Conversation:
        return cls(
            user_id=d["user_id"],
            conversation_id=d["conversation_id"],
            title=d.get("title"),
            messages=[Message.from_dict(m) for m in d.get("messages", [])],
            created_at=d.get("created_at", ""),
            updated_at=d.get("updated_at", ""),
        )
