import { RefreshCw, Search } from "lucide-react";
import { useMemo, useState } from "react";

import Button from "../components/common/Button";
import DocumentList from "../components/documents/DocumentList";
import Dropzone from "../components/documents/Dropzone";
import UploadProgress from "../components/documents/UploadProgress";
import { useDocuments } from "../hooks/useDocuments";

/** Document management page: upload, list, search, delete, refresh. */
export default function DocumentsPage() {
  const {
    documents,
    isLoading,
    error,
    uploads,
    refresh,
    upload,
    remove,
  } = useDocuments();
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return documents;
    return documents.filter((d) =>
      d.original_filename.toLowerCase().includes(q)
    );
  }, [documents, query]);

  const isUploading = uploads.some((u) => u.status === "uploading");

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-4xl px-4 py-6">
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-slate-800">Documents</h1>
          <p className="mt-1 text-sm text-slate-500">
            Upload PDFs and Word documents to make them searchable in chat.
          </p>
        </div>

        {/* Upload */}
        <Dropzone onFiles={upload} disabled={isUploading} />
        <UploadProgress uploads={uploads} />

        {/* Toolbar */}
        <div className="mt-8 mb-3 flex items-center gap-3">
          <div className="relative flex-1">
            <Search
              size={16}
              className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search documents…"
              className="w-full rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <Button
            variant="secondary"
            onClick={refresh}
            disabled={isLoading}
            title="Refresh list"
          >
            <RefreshCw size={16} className={isLoading ? "animate-spin" : ""} />
            Refresh
          </Button>
        </div>

        {!isLoading && !error && (
          <p className="mb-2 text-xs text-slate-400">
            {filtered.length} of {documents.length} document
            {documents.length === 1 ? "" : "s"}
          </p>
        )}

        <DocumentList
          documents={filtered}
          isLoading={isLoading}
          error={error}
          onDelete={remove}
        />
      </div>
    </div>
  );
}
