import React, { createContext, useContext, useCallback, useEffect, useRef, useState } from "react";
import { ChatWebSocket } from "@/features/chat/data/datasources/chatWebSocketDatasource";
import {
  listConversations,
  getConversation,
} from "@/features/chat/data/datasources/chatRestDatasource";

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);

  const connect = useCallback(async () => {
    if (wsRef.current?.isConnected) return;

    const ws = new ChatWebSocket({
      onChunk: (chunk) => {
        setStreamingContent((prev) => prev + chunk);
      },
      onComplete: (message, conversationId) => {
        setStreamingContent("");
        setIsStreaming(false);
        setActiveConversation((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            messages: [...(prev.messages || []), message],
          };
        });
        refreshConversations();
      },
      onError: (err) => {
        setError(err);
        setIsStreaming(false);
        setStreamingContent("");
      },
      onClose: () => {
        setIsConnected(false);
      },
    });

    try {
      await ws.connect();
      wsRef.current = ws;
      setIsConnected(true);
      setError(null);
    } catch (e) {
      setError("Failed to connect to chat service");
    }
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.disconnect();
    wsRef.current = null;
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback(
    (content, generateReport = false) => {
      if (!wsRef.current?.isConnected) {
        setError("Not connected");
        return;
      }

      const userMessage = {
        message_id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: new Date().toISOString(),
        sources: [],
        report_url: null,
      };

      setActiveConversation((prev) => {
        if (!prev) {
          return {
            conversation_id: null,
            title: content.slice(0, 60),
            messages: [userMessage],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
        }
        return { ...prev, messages: [...(prev.messages || []), userMessage] };
      });

      setIsStreaming(true);
      setStreamingContent("");
      setError(null);

      wsRef.current.sendMessage(
        activeConversation?.conversation_id,
        content,
        generateReport
      );
    },
    [activeConversation]
  );

  const refreshConversations = useCallback(async () => {
    try {
      const list = await listConversations();
      setConversations(list);
    } catch (e) {
      // silent fail on refresh
    }
  }, []);

  const loadConversation = useCallback(async (conversationId) => {
    try {
      const conv = await getConversation(conversationId);
      setActiveConversation(conv);
    } catch (e) {
      setError("Failed to load conversation");
    }
  }, []);

  const startNewConversation = useCallback(() => {
    setActiveConversation(null);
    setStreamingContent("");
    setIsStreaming(false);
    setError(null);
  }, []);

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversation,
        streamingContent,
        isStreaming,
        isConnected,
        error,
        connect,
        disconnect,
        sendMessage,
        refreshConversations,
        loadConversation,
        startNewConversation,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within ChatProvider");
  return ctx;
}
