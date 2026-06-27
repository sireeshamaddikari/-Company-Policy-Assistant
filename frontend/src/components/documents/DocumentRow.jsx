import { FileText, Loader2, Trash2 } from "lucide-react";
import { useState } from "react";

import { formatDate } from "../../lib/format";
import StatusBadge from "./StatusBadge";

/** A single document row in the list/table. */
export default function DocumentRow({ document, onDelete }) {
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!window.confirm(`Delete "${document.original_filename}"?`)) return;
    setDeleting(true);
    try {
      await onDelete(document.id);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <tr className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <FileText size={16} className="shrink-0 text-slate-400" />
          <span className="truncate font-medium text-slate-700">
            {document.original_filename}
          </span>
          <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-slate-500">
            {document.file_type}
          </span>
        </div>
      </td>
      <td className="whitespace-nowrap px-4 py-3 text-slate-500">
        {formatDate(document.upload_date)}
      </td>
      <td className="px-4 py-3 text-center text-slate-500">
        {document.pages ?? "—"}
      </td>
      <td className="px-4 py-3 text-center text-slate-500">
        {document.chunk_count}
      </td>
      <td className="px-4 py-3">
        <StatusBadge status={document.indexing_status} />
      </td>
      <td className="px-4 py-3 text-right">
        <button
          type="button"
          onClick={handleDelete}
          disabled={deleting}
          className="inline-flex items-center justify-center rounded-md p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 disabled:opacity-50"
          aria-label="Delete document"
        >
          {deleting ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Trash2 size={16} />
          )}
        </button>
      </td>
    </tr>
  );
}
