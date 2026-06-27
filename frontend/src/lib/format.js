/** Tiny className combiner (filters falsy values). */
export function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

/** Format an ISO date string as a readable local date+time. */
export function formatDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Format a 0..1 confidence as a whole percentage, or null. */
export function formatConfidence(value) {
  if (value == null || Number.isNaN(value)) return null;
  return Math.round(value * 100);
}

/**
 * Display-only cleanup of an assistant answer.
 *
 * The backend prompt asks the model to cite sources, so answers sometimes end
 * with a trailing "Source: …" / "Sources: …" line. We keep that behavior on the
 * backend (it helps the model stay grounded) but hide it in the UI so the
 * message reads like a plain answer. Only trailing source lines are removed —
 * the body is never touched.
 */
export function stripTrailingSources(text) {
  if (!text) return text;
  const lines = text.split("\n");
  while (lines.length) {
    const last = lines[lines.length - 1].trim();
    if (last === "" || /^sources?\s*[:\-–]/i.test(last)) {
      lines.pop();
    } else {
      break;
    }
  }
  return lines.join("\n").trimEnd();
}
