import apiClient from "./client";

/**
 * Send a question to the RAG pipeline.
 * @param {string} question
 * @param {number} [topK]
 * @returns {Promise<{answer: string, citations: any[], retrieved_chunks: any[], confidence: number|null}>}
 */
export async function sendChat(question, topK) {
  const payload = { question };
  if (topK) payload.top_k = topK;
  const { data } = await apiClient.post("/api/v1/chat", payload);
  return data;
}
