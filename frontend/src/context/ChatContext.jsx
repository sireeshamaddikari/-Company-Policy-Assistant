import { createContext, useContext } from "react";

import { useChat } from "../hooks/useChat";

const ChatContext = createContext(null);

/** Provides a single shared chat session to the app (so the sidebar's New
 *  Chat button and the chat page operate on the same state). */
export function ChatProvider({ children }) {
  const chat = useChat();
  return <ChatContext.Provider value={chat}>{children}</ChatContext.Provider>;
}

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return ctx;
}
