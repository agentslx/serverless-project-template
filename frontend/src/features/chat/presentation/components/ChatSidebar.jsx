import React, { useEffect } from "react";
import { cn } from "@/lib/utils";
import { useChat } from "../state/ChatContext";

export default function ChatSidebar() {
  const {
    conversations,
    activeConversation,
    refreshConversations,
    loadConversation,
    startNewConversation,
  } = useChat();

  useEffect(() => {
    refreshConversations();
  }, [refreshConversations]);

  return (
    <aside className="flex h-full w-72 flex-col border-r border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900">
      <div className="flex items-center justify-between border-b border-gray-200 p-4 dark:border-gray-700">
        <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          Conversations
        </h2>
        <button
          onClick={startNewConversation}
          className="rounded-md bg-indigo-600 px-2.5 py-1 text-xs font-medium text-white hover:bg-indigo-700"
        >
          + New
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <p className="p-4 text-center text-xs text-gray-400">
            No conversations yet
          </p>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {conversations.map((conv) => (
              <li key={conv.conversation_id}>
                <button
                  onClick={() => loadConversation(conv.conversation_id)}
                  className={cn(
                    "w-full px-4 py-3 text-left transition-colors hover:bg-gray-100 dark:hover:bg-gray-800",
                    activeConversation?.conversation_id === conv.conversation_id &&
                      "bg-indigo-50 dark:bg-indigo-900/20"
                  )}
                >
                  <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
                    {conv.title || "Untitled"}
                  </p>
                  <p className="mt-0.5 text-xs text-gray-500">
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
