"""Concrete conversation repository backed by DynamoDB."""
from __future__ import annotations

from typing import Optional

from feature.research_chat_py.data.datasources.dynamo_conversation_ds import (
    DynamoConversationDataSource,
)
from feature.research_chat_py.data.models.conversation_model import (
    conversation_to_item,
    item_to_conversation,
    message_to_map,
    map_to_message,
)
from feature.research_chat_py.domain.entities.conversation import Conversation, Message
from feature.research_chat_py.domain.repository.conversation_repository import (
    ConversationRepository,
)


class DynamoConversationRepository(ConversationRepository):
    def __init__(self, ds: DynamoConversationDataSource):
        self._ds = ds

    def get(self, user_id: str, conversation_id: str) -> Optional[Conversation]:
        item = self._ds.get_item(user_id, conversation_id)
        if not item:
            return None
        return item_to_conversation(item)

    def list_for_user(self, user_id: str) -> list[Conversation]:
        items = self._ds.query_by_user(user_id)
        return [item_to_conversation(i) for i in items]

    def create(self, conversation: Conversation) -> None:
        self._ds.put_item(conversation_to_item(conversation))

    def append_message(self, user_id: str, conversation_id: str, message: Message) -> None:
        self._ds.append_message(user_id, conversation_id, message_to_map(message))
