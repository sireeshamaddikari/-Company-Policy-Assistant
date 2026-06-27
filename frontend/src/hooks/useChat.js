import { useCallback, useState } from "react";

import { sendChat } from "../api/chat";

let idCounter = 0;
const nextId = () => `${Date.now()}-${idCounter++}`;

/**
 * Manages a single chat session's message list and the request lifecycle.
 *
 * Messages: { id, role: 'user'|'assistant', content, citations?, confidence?,
 *             retrievedChunks?, isError? }
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const newChat = useCallback(() => {
    setMessages([]);
    setIsLoading(false);
  }, []);

  const send = useCallback(
    async (question) => {
      const trimmed = question.trim();
      if (!trimmed || isLoading) return;

      const userMessage = {
        id: nextId(),
        role: "user",
        content: trimmed,
      };
      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const data = await sendChat(trimmed);
        setMessages((prev) => [
          ...prev,
          {
            id: nextId(),
            role: "assistant",
            content: data.answer,
            citations: data.citations || [],
            retrievedChunks: data.retrieved_chunks || [],
            confidence: data.confidence,
          },
        ]);
      } catch (error) {
        setMessages((prev) => [
          ...prev,
          {
            id: nextId(),
            role: "assistant",
            content:
              error.friendlyMessage ||
              "Sorry, something went wrong while answering your question.",
            isError: true,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading]
  );

  return { messages, isLoading, send, newChat };
}
