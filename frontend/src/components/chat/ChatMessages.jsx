import { Bot } from "lucide-react";
import { useEffect, useRef } from "react";

import EmptyState from "../common/EmptyState";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

const SUGGESTIONS = [
  "What is our leave policy?",
  "Summarize the onboarding process.",
  "What are the security guidelines?",
];

/** Scrollable message list with auto-scroll and an empty/welcome state. */
export default function ChatMessages({ messages, isLoading, onSuggestion }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          icon={Bot}
          title="Ask anything about your documents"
          description="I answer using only the documents you've uploaded, and I cite my sources."
          action={
            <div className="flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => onSuggestion?.(s)}
                  className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-600 hover:border-indigo-300 hover:text-indigo-600"
                >
                  {s}
                </button>
              ))}
            </div>
          }
        />
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-6">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
