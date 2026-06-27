import { FileText, MessageSquarePlus, MessagesSquare, Bot } from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";

import { useChatContext } from "../../context/ChatContext";
import { cn } from "../../lib/format";

const navLinkClass = ({ isActive }) =>
  cn(
    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
    isActive
      ? "bg-slate-800 text-white"
      : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
  );

export default function Sidebar({ onNavigate }) {
  const { newChat } = useChatContext();
  const navigate = useNavigate();

  const handleNewChat = () => {
    newChat();
    navigate("/");
    onNavigate?.();
  };

  return (
    <div className="flex h-full w-64 flex-col bg-slate-900 text-slate-100">
      <div className="flex items-center gap-2 px-4 py-4">
        <div className="rounded-lg bg-indigo-600 p-1.5">
          <Bot size={20} />
        </div>
        <span className="text-sm font-semibold">Company RAG</span>
      </div>

      <div className="px-3">
        <button
          type="button"
          onClick={handleNewChat}
          className="flex w-full items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm font-medium text-slate-100 hover:bg-slate-800 transition-colors"
        >
          <MessageSquarePlus size={18} />
          New Chat
        </button>
      </div>

      <nav className="mt-4 flex flex-col gap-1 px-3">
        <NavLink to="/" end className={navLinkClass} onClick={onNavigate}>
          <MessagesSquare size={18} />
          Chat
        </NavLink>
        <NavLink to="/documents" className={navLinkClass} onClick={onNavigate}>
          <FileText size={18} />
          Documents
        </NavLink>
      </nav>

      <div className="mt-auto px-4 py-4 text-xs text-slate-500">
        Answers are grounded in your uploaded documents.
      </div>
    </div>
  );
}
