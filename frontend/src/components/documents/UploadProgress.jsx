import { CheckCircle2, Loader2, XCircle } from "lucide-react";

/** Shows per-file upload progress / result. */
export default function UploadProgress({ uploads }) {
  if (!uploads || uploads.length === 0) return null;

  return (
    <ul className="mt-3 space-y-2">
      {uploads.map((u) => (
        <li
          key={u.key}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2"
        >
          <div className="flex items-center justify-between gap-2 text-sm">
            <span className="min-w-0 truncate text-slate-700">{u.name}</span>
            {u.status === "uploading" && (
              <span className="flex items-center gap-1 text-xs text-slate-500">
                <Loader2 size={14} className="animate-spin" />
                {u.percent}%
              </span>
            )}
            {u.status === "done" && (
              <CheckCircle2 size={16} className="text-emerald-600" />
            )}
            {u.status === "error" && (
              <XCircle size={16} className="text-red-600" />
            )}
          </div>
          {u.status !== "error" && (
            <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all"
                style={{ width: `${u.percent}%` }}
              />
            </div>
          )}
          {u.status === "error" && (
            <p className="mt-1 text-xs text-red-600">{u.error}</p>
          )}
        </li>
      ))}
    </ul>
  );
}
