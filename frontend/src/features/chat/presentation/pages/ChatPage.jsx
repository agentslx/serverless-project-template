import React, { useEffect } from "react";
import { ChatProvider, useChat } from "../state/ChatContext";
import ChatSidebar from "../components/ChatSidebar";
import MessageList from "../components/MessageList";
import MessageInput from "../components/MessageInput";

function ChatContent() {
  const { connect, isConnected, error } = useChat();

  useEffect(() => {
    connect();
  }, [connect]);

  return (
    <div className="flex h-[calc(100vh-4rem)] overflow-hidden">
      <ChatSidebar />

      <main className="flex flex-1 flex-col">
        {error && (
          <div className="border-b border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
            {error}
          </div>
        )}

        {!isConnected && !error && (
          <div className="border-b border-yellow-200 bg-yellow-50 px-4 py-2 text-sm text-yellow-700 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">
            Connecting to chat service...
          </div>
        )}

        <div className="flex flex-1 flex-col overflow-hidden">
          <MessageList />
          <MessageInput />
        </div>
      </main>
    </div>
  );
}

export default function ChatPage() {
  return (
    <ChatProvider>
      <ChatContent />
    </ChatProvider>
  );
}
