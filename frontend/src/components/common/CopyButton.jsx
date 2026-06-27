import { Check, Copy } from "lucide-react";
import { useState } from "react";

import { cn } from "../../lib/format";

/** A small button that copies `text` to the clipboard and shows a check. */
export default function CopyButton({ text, className, label = "Copy" }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard may be unavailable (e.g. insecure context); fail silently.
    }
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={cn(
        "inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs text-slate-500",
        "hover:bg-slate-100 hover:text-slate-700 transition-colors",
        className
      )}
      title={label}
    >
      {copied ? (
        <>
          <Check size={14} /> Copied
        </>
      ) : (
        <>
          <Copy size={14} /> {label}
        </>
      )}
    </button>
  );
}
