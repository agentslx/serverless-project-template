"""Abstract repository for conversation persistence."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from feature.research_chat_py.domain.entities.conversation import Conversation, Message


class ConversationRepository(ABC):
    @abstractmethod
    def get(self, user_id: str, conversation_id: str) -> Optional[Conversation]:
        ...

    @abstractmethod
    def list_for_user(self, user_id: str) -> list[Conversation]:
        ...

    @abstractmethod
    def create(self, conversation: Conversation) -> None:
        ...

    @abstractmethod
    def append_message(self, user_id: str, conversation_id: str, message: Message) -> None:
        ...
