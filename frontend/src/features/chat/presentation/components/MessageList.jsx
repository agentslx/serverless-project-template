import React, { useEffect, useRef } from "react";
import { useChat } from "../state/ChatContext";
import MessageBubble from "./MessageBubble";
import StreamingIndicator from "./StreamingIndicator";

export default function MessageList() {
  const { activeConversation, streamingContent, isStreaming } = useChat();
  const bottomRef = useRef(null);

  const messages = activeConversation?.messages || [];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-center">
        <div className="rounded-full bg-indigo-50 p-4 dark:bg-indigo-900/30">
          <svg className="h-8 w-8 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
          Research Agent Team
        </h3>
        <p className="mt-1 max-w-sm text-sm text-gray-500 dark:text-gray-400">
          Ask a question and our team of AI agents will research the web and compose a thorough answer for you.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-4 overflow-y-auto p-4">
      {messages.map((msg) => (
        <MessageBubble key={msg.message_id} message={msg} />
      ))}
      {isStreaming && <StreamingIndicator content={streamingContent} />}
      <div ref={bottomRef} />
    </div>
  );
}
