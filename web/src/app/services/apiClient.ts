/**
 * API Client for Davar Backend
 * Handles authenticated requests with API key validation and better error reporting.
 */

type ApiClientConfigInput = {
  env?: Record<string, string | undefined>;
  processEnv?: Record<string, string | undefined>;
};

type ApiClientResolvedConfig = {
  apiBaseUrl: string;
  apiKey: string;
  publicNodeEnv: string;
  isDev: boolean;
  usedFallbackApiBaseUrl: boolean;
};

export const resolveApiClientConfig = ({
  env = {},
  processEnv = {},
}: ApiClientConfigInput = {}): ApiClientResolvedConfig => {
  const publicNodeEnv =
    env.PUBLIC_NODE_ENV || processEnv.PUBLIC_NODE_ENV || "production";
  const isDev = publicNodeEnv === "development";

  const fallbackApiUrl = isDev
    ? "http://localhost:2220"
    : "https://davar.onrender.com";

  const configuredApiBaseUrl =
    env.PUBLIC_API_BASE_URL || processEnv.PUBLIC_API_BASE_URL;
  const apiBaseUrl = configuredApiBaseUrl || fallbackApiUrl;

  const rawApiKey = env.PUBLIC_API_KEY || processEnv.PUBLIC_API_KEY || "";

  return {
    apiBaseUrl,
    apiKey: rawApiKey.trim(),
    publicNodeEnv,
    isDev,
    usedFallbackApiBaseUrl: !configuredApiBaseUrl,
  };
};

// Use direct process.env.PUBLIC_* references so Bun can statically
// replace them at build time. Bun only inlines process.env — NOT
// import.meta.env — during Bun.build().
const resolvedConfig = resolveApiClientConfig({
  env: {
    PUBLIC_NODE_ENV: process.env.PUBLIC_NODE_ENV,
    PUBLIC_API_BASE_URL: process.env.PUBLIC_API_BASE_URL,
    PUBLIC_API_KEY: process.env.PUBLIC_API_KEY,
  },
});

const {
  apiBaseUrl: API_BASE_URL,
  apiKey: API_KEY,
  publicNodeEnv,
  isDev,
} = resolvedConfig;

console.log("[Davar] API Config:", {
  url: API_BASE_URL,
  hasKey: !!API_KEY,
  env: publicNodeEnv,
});

if (!isDev && resolvedConfig.usedFallbackApiBaseUrl) {
  console.warn(
    "[Davar API Client] PUBLIC_API_BASE_URL is missing in production build. " +
      "Using fallback https://davar.onrender.com. Set PUBLIC_API_BASE_URL at build time.",
  );
}

// Validate API key presence in both environments
if (!API_KEY) {
  if (isDev) {
    console.error(
      "[Davar API Client] Missing PUBLIC_API_KEY in .env file or environment.\n" +
        "All API requests will fail until this is configured.",
    );
  } else {
    console.warn(
      "[Davar API Client] PUBLIC_API_KEY is missing in production build. " +
        "All authenticated API requests will fail. Set PUBLIC_API_KEY at build time.",
    );
  }
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
        "Please set PUBLIC_API_KEY in your .env file or environment variables.",
    );
    error.name = "MissingApiKeyError";
    throw error;
  }

  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const method = (options.method || "GET").toUpperCase();
  const isReadOnlyRequest = method === "GET" || method === "HEAD";

  const headers = new Headers({
    "X-API-Key": API_KEY,
    ...options.headers,
  });

  if (!headers.has("Content-Type") && options.body != null) {
    headers.set("Content-Type", "application/json");
  }

  // Let cacheable read endpoints use browser/CDN caching by default.
  if (!headers.has("Cache-Control") && !isReadOnlyRequest) {
    headers.set("Cache-Control", "no-store");
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
    credentials: "omit", // no cookies needed for API key auth
    cache: options.cache ?? (isReadOnlyRequest ? "default" : "no-store"),
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
