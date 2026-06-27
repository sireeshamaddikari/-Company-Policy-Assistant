import { Check, Copy } from "lucide-react";
import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

/** A fenced code block with a copy button (reads rendered text on click). */
function PreBlock({ children }) {
  const ref = useRef(null);
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(ref.current?.textContent || "");
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <div className="group relative my-3">
      <button
        type="button"
        onClick={copy}
        className="absolute right-2 top-2 z-10 inline-flex items-center gap-1 rounded-md bg-slate-700/80 px-2 py-1 text-xs text-slate-100 opacity-0 transition-opacity group-hover:opacity-100"
        title="Copy code"
      >
        {copied ? <Check size={13} /> : <Copy size={13} />}
        {copied ? "Copied" : "Copy"}
      </button>
      <pre
        ref={ref}
        className="overflow-x-auto rounded-lg bg-slate-900 p-4 text-sm text-slate-100"
      >
        {children}
      </pre>
    </div>
  );
}

/** Renders assistant markdown content with GFM + syntax highlighting. */
export default function Markdown({ children }) {
  return (
    <div className="markdown text-sm leading-relaxed text-slate-800">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          pre: PreBlock,
          // Drop the react-markdown `node` prop so it doesn't hit the DOM.
          a: ({ node, ...props }) => (
            // eslint-disable-next-line jsx-a11y/anchor-has-content
            <a
              target="_blank"
              rel="noreferrer"
              className="text-indigo-600 underline"
              {...props}
            />
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
