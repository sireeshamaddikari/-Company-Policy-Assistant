import { useCallback, useEffect, useState } from "react";

import {
  deleteDocument,
  listDocuments,
  uploadDocument,
} from "../api/documents";

/**
 * Manages the documents list plus upload/delete/refresh operations.
 */
export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  // Per-file upload state: { name, percent, status: 'uploading'|'done'|'error', error? }
  const [uploads, setUploads] = useState([]);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setDocuments(await listDocuments());
    } catch (err) {
      setError(err.friendlyMessage || "Failed to load documents.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const upload = useCallback(
    async (files) => {
      const fileArray = Array.from(files);
      for (const file of fileArray) {
        const key = `${file.name}-${Date.now()}`;
        setUploads((prev) => [
          ...prev,
          { key, name: file.name, percent: 0, status: "uploading" },
        ]);

        try {
          await uploadDocument(file, (percent) => {
            setUploads((prev) =>
              prev.map((u) => (u.key === key ? { ...u, percent } : u))
            );
          });
          setUploads((prev) =>
            prev.map((u) =>
              u.key === key ? { ...u, percent: 100, status: "done" } : u
            )
          );
        } catch (err) {
          setUploads((prev) =>
            prev.map((u) =>
              u.key === key
                ? {
                    ...u,
                    status: "error",
                    error: err.friendlyMessage || "Upload failed.",
                  }
                : u
            )
          );
        }
      }
      // Refresh the list once all uploads settle.
      await refresh();
    },
    [refresh]
  );

  const remove = useCallback(async (id) => {
    await deleteDocument(id);
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  }, []);

  const clearFinishedUploads = useCallback(() => {
    setUploads((prev) => prev.filter((u) => u.status === "uploading"));
  }, []);

  return {
    documents,
    isLoading,
    error,
    uploads,
    refresh,
    upload,
    remove,
    clearFinishedUploads,
  };
}
