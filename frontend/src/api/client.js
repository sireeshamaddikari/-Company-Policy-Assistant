import axios from "axios";

/**
 * Pre-configured Axios instance for talking to the backend API.
 *
 * The base URL is read from Vite's environment (`VITE_API_BASE_URL`) so it can
 * differ between local development and production.
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Normalize backend errors into a plain `Error` with a readable message.
 * The FastAPI app returns `{ error: { type, message } }` for domain errors and
 * `{ detail: [...] }` for validation errors.
 */
export function extractErrorMessage(error) {
  const data = error?.response?.data;
  if (data?.error?.message) return data.error.message;
  if (typeof data?.detail === "string") return data.detail;
  if (Array.isArray(data?.detail) && data.detail[0]?.msg) {
    return data.detail[0].msg;
  }
  if (error?.message) return error.message;
  return "An unexpected error occurred.";
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    error.friendlyMessage = extractErrorMessage(error);
    return Promise.reject(error);
  }
);

export default apiClient;
