import { FileX2 } from "lucide-react";

import Spinner from "../common/Spinner";
import EmptyState from "../common/EmptyState";
import DocumentRow from "./DocumentRow";

/** Table of documents (responsive: scrolls horizontally on small screens). */
export default function DocumentList({ documents, isLoading, error, onDelete }) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-400">
        <Spinner className="h-6 w-6" />
      </div>
    );
  }

  if (error) {
    return (
      <EmptyState
        icon={FileX2}
        title="Couldn't load documents"
        description={error}
      />
    );
  }

  if (documents.length === 0) {
    return (
      <EmptyState
        icon={FileX2}
        title="No documents yet"
        description="Upload a PDF or DOCX above to get started."
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3 font-medium">Filename</th>
            <th className="px-4 py-3 font-medium">Uploaded</th>
            <th className="px-4 py-3 text-center font-medium">Pages</th>
            <th className="px-4 py-3 text-center font-medium">Chunks</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <DocumentRow key={doc.id} document={doc} onDelete={onDelete} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
