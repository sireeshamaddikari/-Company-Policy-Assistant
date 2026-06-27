import { AlertTriangle, Bot, User } from "lucide-react";

import { cn, stripTrailingSources } from "../../lib/format";
import CopyButton from "../common/CopyButton";
import ConfidenceBadge from "./ConfidenceBadge";
import Markdown from "./Markdown";

/** A single chat message — user (right) or assistant (left). */
export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end gap-3">
        <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-indigo-600 px-4 py-2.5 text-sm text-white">
          {message.content}
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600">
          <User size={18} />
        </div>
      </div>
    );
  }

  // Show only the answer text — citations/retrieval details are intentionally
  // not rendered. Any trailing "Source: …" line the model appended is hidden
  // (display only; the backend still returns citations).
  const answer = message.isError
    ? message.content
    : stripTrailingSources(message.content);

  return (
    <div className="flex gap-3">
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          message.isError
            ? "bg-red-100 text-red-600"
            : "bg-indigo-100 text-indigo-600"
        )}
      >
        {message.isError ? <AlertTriangle size={18} /> : <Bot size={18} />}
      </div>

      <div className="min-w-0 max-w-[85%] flex-1">
        <div
          className={cn(
            "rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm ring-1",
            message.isError
              ? "bg-red-50 text-red-700 ring-red-100"
              : "bg-white ring-slate-100"
          )}
        >
          {message.isError ? (
            <p className="text-sm">{answer}</p>
          ) : (
            <Markdown>{answer}</Markdown>
          )}
        </div>

        {!message.isError && (
          <div className="mt-1.5 flex items-center gap-2 pl-1">
            <CopyButton text={answer} label="Copy" />
            <ConfidenceBadge value={message.confidence} />
          </div>
        )}
      </div>
    </div>
  );
}
