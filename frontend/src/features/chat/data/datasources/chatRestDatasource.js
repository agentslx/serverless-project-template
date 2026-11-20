/**
 * REST datasource for chat history (conversations list + single conversation).
 */
import { fetchAuthSession } from "aws-amplify/auth";

const API_BASE =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:9000";

async function authHeaders() {
  const session = await fetchAuthSession();
  const sub = session.tokens?.idToken?.payload?.sub || "";
  return {
    "Content-Type": "application/json",
    "x-user-sub": sub,
  };
}

export async function listConversations() {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/api/chat/conversations`, { headers });
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

export async function getConversation(conversationId) {
  const headers = await authHeaders();
  const res = await fetch(
    `${API_BASE}/api/chat/conversations/${conversationId}`,
    { headers }
  );
  if (!res.ok) throw new Error("Failed to fetch conversation");
  return res.json();
}
