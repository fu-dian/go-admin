import http from "./http";

/**
 * @param {{ role: string, content: string }[]} messages
 * @param {string} [problemId]
 */
export function postAgentChat(messages) {
  return http.post("/agent/chat", { messages });
}
