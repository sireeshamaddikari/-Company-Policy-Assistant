import ChatInput from "../components/chat/ChatInput";
import ChatMessages from "../components/chat/ChatMessages";
import { useChatContext } from "../context/ChatContext";

/** The ChatGPT-style chat page. */
export default function ChatPage() {
  const { messages, isLoading, send } = useChatContext();

  return (
    <div className="flex h-full flex-col">
      <div className="min-h-0 flex-1">
        <ChatMessages
          messages={messages}
          isLoading={isLoading}
          onSuggestion={send}
        />
      </div>
      <ChatInput onSend={send} disabled={isLoading} />
    </div>
  );
}
