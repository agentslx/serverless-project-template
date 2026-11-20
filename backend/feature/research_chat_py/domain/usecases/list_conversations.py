"""Use case: list all conversations for a user (metadata only, no messages)."""
from __future__ import annotations

from feature.research_chat_py.domain.entities.conversation import Conversation
from feature.research_chat_py.domain.repository.conversation_repository import (
    ConversationRepository,
)


class ListConversationsUseCase:
    def __init__(self, repo: ConversationRepository):
        self._repo = repo

    def execute(self, user_id: str) -> list[Conversation]:
        return self._repo.list_for_user(user_id)
