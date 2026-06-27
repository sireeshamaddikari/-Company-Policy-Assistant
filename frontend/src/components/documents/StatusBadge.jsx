import { cn } from "../../lib/format";

const STYLES = {
  indexed: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  processing: "bg-amber-50 text-amber-700 ring-amber-600/20",
  failed: "bg-red-50 text-red-700 ring-red-600/20",
};

export default function StatusBadge({ status }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium capitalize ring-1 ring-inset",
        STYLES[status] || "bg-slate-50 text-slate-600 ring-slate-500/20"
      )}
    >
      {status}
    </span>
  );
}
