"""Use case: retrieve a single conversation with full message history."""
from __future__ import annotations

from typing import Optional

from feature.research_chat_py.domain.entities.conversation import Conversation
from feature.research_chat_py.domain.repository.conversation_repository import (
    ConversationRepository,
)


class GetConversationUseCase:
    def __init__(self, repo: ConversationRepository):
        self._repo = repo

    def execute(self, user_id: str, conversation_id: str) -> Optional[Conversation]:
        return self._repo.get(user_id, conversation_id)
