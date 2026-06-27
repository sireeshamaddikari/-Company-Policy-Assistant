import apiClient from "./client";

/**
 * Document API calls. Each returns the parsed response data (or throws an
 * Axios error carrying `friendlyMessage`).
 */

export async function listDocuments() {
  const { data } = await apiClient.get("/api/v1/documents");
  return data;
}

export async function getDocument(id) {
  const { data } = await apiClient.get(`/api/v1/documents/${id}`);
  return data;
}

/**
 * Upload a file with progress reporting.
 * @param {File} file
 * @param {(percent: number) => void} [onProgress]
 */
export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post("/api/v1/documents", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded * 100) / event.total));
      }
    },
  });
  return data;
}

export async function deleteDocument(id) {
  const { data } = await apiClient.delete(`/api/v1/documents/${id}`);
  return data;
}
