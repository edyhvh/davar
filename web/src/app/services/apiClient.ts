/**
 * API Client for Davar Backend
 * Handles authenticated requests with API key validation and better error reporting.
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:2220";

// Load API key once at module level
const RAW_API_KEY = import.meta.env.VITE_API_KEY;
const API_KEY = RAW_API_KEY?.trim();

// Early validation in development to catch missing key immediately
if (import.meta.env.DEV && !API_KEY) {
  console.error(
    "[Davar API Client] Missing VITE_API_KEY in .env file or environment.\n" +
      "All API requests will fail until this is configured.",
  );
}

interface ApiError extends Error {
  status?: number;
  code?: string;
  details?: unknown;
}

export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> => {
  // Runtime check: prevent requests with missing/invalid key
  if (!API_KEY || API_KEY.trim() === "") {
    const error: ApiError = new Error(
      "API key is missing or empty. Cannot make authenticated request.\n" +
        "Please set VITE_API_KEY in your .env file or environment variables.",
    );
    error.name = "MissingApiKeyError";
    throw error;
  }

  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const headers = new Headers({
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "Cache-Control": "no-store",
    ...options.headers,
  });

  const fetchOptions: RequestInit = {
    ...options,
    headers,
    credentials: "omit", // no cookies needed for API key auth
    cache: "no-store",
  };

  try {
    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      let errorBody: any = null;
      try {
        errorBody = await response.json();
      } catch {
        // non-JSON error response (rare)
      }

      const error: ApiError = new Error(
        errorBody?.detail ||
          errorBody?.message ||
          `API request failed with status ${response.status}`,
      );

      error.status = response.status;
      error.code = errorBody?.code;
      error.details = errorBody?.details || errorBody;

      throw error;
    }

    const data = await response.json();
    return data as T;
  } catch (err) {
    // Re-throw with better context if it's a network error
    if (err instanceof TypeError && err.message.includes("fetch")) {
      const networkError: ApiError = new Error(
        `Network error connecting to ${API_BASE_URL}: ${err.message}`,
      );
      networkError.name = "NetworkError";
      throw networkError;
    }

    throw err;
  }
};

// Optional: convenience wrappers (can be removed if not needed)
export const get = <T>(endpoint: string, options: RequestInit = {}) =>
  apiRequest<T>(endpoint, { ...options, method: "GET" });

export const post = <T>(
  endpoint: string,
  body: any,
  options: RequestInit = {},
) =>
  apiRequest<T>(endpoint, {
    ...options,
    method: "POST",
    body: JSON.stringify(body),
  });

export default apiRequest;
