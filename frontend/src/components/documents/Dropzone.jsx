import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import { cn } from "../../lib/format";

const ACCEPTED = [".pdf", ".docx"];

function isAccepted(file) {
  const name = file.name.toLowerCase();
  return ACCEPTED.some((ext) => name.endsWith(ext));
}

/** Drag-and-drop + click-to-browse upload zone for PDF/DOCX files. */
export default function Dropzone({ onFiles, disabled }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const [rejected, setRejected] = useState(null);

  const handleFiles = (fileList) => {
    const files = Array.from(fileList);
    const ok = files.filter(isAccepted);
    const bad = files.filter((f) => !isAccepted(f));
    setRejected(bad.length ? bad.map((f) => f.name).join(", ") : null);
    if (ok.length) onFiles(ok);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    if (disabled) return;
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors",
          dragging
            ? "border-indigo-400 bg-indigo-50"
            : "border-slate-300 bg-white hover:border-indigo-300",
          disabled && "cursor-not-allowed opacity-60"
        )}
      >
        <UploadCloud
          size={32}
          className={dragging ? "text-indigo-500" : "text-slate-400"}
        />
        <p className="mt-3 text-sm font-medium text-slate-700">
          Drag &amp; drop files here, or click to browse
        </p>
        <p className="mt-1 text-xs text-slate-400">PDF or DOCX</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          multiple
          hidden
          onChange={(e) => {
            handleFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>
      {rejected && (
        <p className="mt-2 text-xs text-red-600">
          Skipped unsupported file(s): {rejected}
        </p>
      )}
    </div>
  );
}
