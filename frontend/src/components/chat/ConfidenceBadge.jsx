import { Gauge } from "lucide-react";

import { cn, formatConfidence } from "../../lib/format";

/** Colored badge showing retrieval confidence as a percentage. */
export default function ConfidenceBadge({ value }) {
  const pct = formatConfidence(value);
  if (pct == null) return null;

  const tone =
    pct >= 70
      ? "bg-emerald-50 text-emerald-700 ring-emerald-600/20"
      : pct >= 40
        ? "bg-amber-50 text-amber-700 ring-amber-600/20"
        : "bg-red-50 text-red-700 ring-red-600/20";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset",
        tone
      )}
      title="Retrieval confidence (top similarity score)"
    >
      <Gauge size={12} />
      {pct}% confidence
    </span>
  );
}
