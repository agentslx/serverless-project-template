"""Use case: send a chat message and get a streamed agent response."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Callable, Optional

from strands import Agent

from feature.research_chat_py.domain.entities.conversation import (
    ChatSource,
    Conversation,
    Message,
)
from feature.research_chat_py.domain.repository.conversation_repository import (
    ConversationRepository,
)


class SendMessageUseCase:
    def __init__(
        self,
        repo: ConversationRepository,
        s3_report_ds,
        orchestrator: Agent,
    ):
        self._repo = repo
        self._s3 = s3_report_ds
        self._orchestrator = orchestrator

    def execute(
        self,
        user_id: str,
        content: str,
        conversation_id: Optional[str] = None,
        generate_report: bool = False,
        on_chunk: Optional[Callable[[str], None]] = None,
    ) -> Message:
        """Run the agent pipeline and return the assistant message.

        Args:
            user_id: Cognito sub of the caller.
            content: User's message text.
            conversation_id: Existing conversation ID, or None to start new.
            generate_report: If True, upload a markdown report to S3.
            on_chunk: Optional callback invoked with each text chunk for streaming.
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conversation = Conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                title=content[:60],
            )
            self._repo.create(conversation)

        user_msg = Message.new_user_message(content)
        self._repo.append_message(user_id, conversation_id, user_msg)

        prompt = content
        if generate_report:
            prompt += "\n\n[Please generate a comprehensive markdown report for this query.]"

        collected_chunks: list[str] = []

        def _streaming_callback(chunk: str):
            collected_chunks.append(chunk)
            if on_chunk:
                on_chunk(chunk)

        # Run the orchestrator agent
        response = self._orchestrator(prompt)
        full_text = str(response)

        # Extract sources if available from the response metadata
        sources: list[ChatSource] = []
        if hasattr(response, "tool_results"):
            for result in getattr(response, "tool_results", []):
                if isinstance(result, dict) and "url" in result:
                    sources.append(ChatSource(url=result["url"], title=result.get("title")))

        report_url: Optional[str] = None
        if generate_report and full_text:
            report_url = self._s3.upload_report(
                user_id=user_id,
                conversation_id=conversation_id,
                content=full_text,
            )

        assistant_msg = Message.new_assistant_message(
            content=full_text,
            sources=sources,
            report_url=report_url,
        )
        self._repo.append_message(user_id, conversation_id, assistant_msg)

        return assistant_msg
