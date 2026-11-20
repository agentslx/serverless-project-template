/**
 * WebSocket datasource for real-time chat with the research agent team.
 */
import { fetchAuthSession } from "aws-amplify/auth";

const WS_URL =
  process.env.REACT_APP_CHAT_WS_URL || "ws://localhost:9001/ws/chat";

export class ChatWebSocket {
  constructor({ onChunk, onComplete, onError, onClose }) {
    this.wsUrl = WS_URL;
    this.onChunk = onChunk;
    this.onComplete = onComplete;
    this.onError = onError;
    this.onClose = onClose;
    this.ws = null;
  }

  async connect() {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString() || "";
    const url = `${this.wsUrl}?token=${token}`;

    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => resolve();

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          switch (data.type) {
            case "chunk":
              this.onChunk?.(data.content);
              break;
            case "complete":
              this.onComplete?.(data.message, data.conversation_id);
              break;
            case "error":
              this.onError?.(data.error);
              break;
            default:
              break;
          }
        } catch (e) {
          this.onError?.("Failed to parse message");
        }
      };

      this.ws.onerror = (err) => {
        this.onError?.("WebSocket error");
        reject(err);
      };

      this.ws.onclose = () => {
        this.onClose?.();
      };
    });
  }

  sendMessage(conversationId, content, generateReport = false) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.onError?.("WebSocket not connected");
      return;
    }

    this.ws.send(
      JSON.stringify({
        action: "sendMessage",
        conversation_id: conversationId,
        content,
        generate_report: generateReport,
      })
    );
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  get isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
