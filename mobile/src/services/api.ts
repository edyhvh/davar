import type { BookResponse } from "@/src/types/api";
import { NativeModules, Platform } from "react-native";

const DEV_STATIC_DATA_BASE_URL = "http://127.0.0.1:3002/data";
const PROD_STATIC_DATA_BASE_URL = "https://davar.bible/data";

const staticDataCache = new Map<string, unknown>();

const normalizeBaseUrl = (url: string): string => url.replace(/\/+$/, "");

const LOOPBACK_HOSTS = new Set(["127.0.0.1", "localhost"]);

const getMetroHostCandidate = (): string | null => {
  if (!__DEV__) {
    return null;
  }

  const scriptUrl =
    typeof NativeModules?.SourceCode?.scriptURL === "string"
      ? NativeModules.SourceCode.scriptURL
      : "";

  if (!scriptUrl) {
    return null;
  }

  try {
    const parsed = new URL(scriptUrl);
    if (!parsed.hostname || LOOPBACK_HOSTS.has(parsed.hostname)) {
      return null;
    }
    return parsed.hostname;
  } catch {
    return null;
  }
};

const mapLoopbackForAndroidEmulator = (url: string): string => {
  if (!__DEV__ || Platform.OS !== "android") {
    return url;
  }

  try {
    const parsed = new URL(url);
    if (LOOPBACK_HOSTS.has(parsed.hostname)) {
      const metroHost = getMetroHostCandidate();
      if (metroHost) {
        parsed.hostname = metroHost;
        return parsed.toString();
      }

      parsed.hostname = "10.0.2.2";
      return parsed.toString();
    }
  } catch {
    return url;
  }

  return url;
};

const resolveStaticDataBaseUrl = (): string => {
  const configuredDataBase = process.env.EXPO_PUBLIC_STATIC_DATA_BASE_URL?.trim();
  if (configuredDataBase) {
    return normalizeBaseUrl(mapLoopbackForAndroidEmulator(configuredDataBase));
  }

  return __DEV__
    ? normalizeBaseUrl(mapLoopbackForAndroidEmulator(DEV_STATIC_DATA_BASE_URL))
    : normalizeBaseUrl(PROD_STATIC_DATA_BASE_URL);
};

const resolveStaticBundlesBaseUrl = (dataBaseUrl: string): string => {
  const configuredBundlesBase =
    process.env.EXPO_PUBLIC_STATIC_BUNDLES_BASE_URL?.trim();
  if (configuredBundlesBase) {
    return normalizeBaseUrl(mapLoopbackForAndroidEmulator(configuredBundlesBase));
  }

  return `${normalizeBaseUrl(dataBaseUrl)}/bundles`;
};

const STATIC_DATA_BASE_URL = resolveStaticDataBaseUrl();
const STATIC_BUNDLES_BASE_URL = resolveStaticBundlesBaseUrl(STATIC_DATA_BASE_URL);

let staticUrlDiagnosticsReported = false;

const truncateForError = (value: string, maxLength = 180): string => {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) {
    return normalized;
  }
  return `${normalized.slice(0, maxLength)}...`;
};

const looksLikeHtmlPayload = (payload: string): boolean => {
  const normalized = payload.trimStart().toLowerCase();
  return (
    normalized.startsWith("<!doctype") ||
    normalized.startsWith("<html") ||
    normalized.startsWith("<?xml")
  );
};

const buildNetworkHint = (requestUrl: string): string => {
  if (!__DEV__) {
    return "";
  }

  try {
    const parsed = new URL(requestUrl);
    const host = parsed.hostname;

    if (Platform.OS === "android" && (host === "10.0.2.2" || LOOPBACK_HOSTS.has(host))) {
      return " In Android dev builds on a physical device, set EXPO_PUBLIC_STATIC_DATA_BASE_URL and EXPO_PUBLIC_STATIC_BUNDLES_BASE_URL to your machine LAN IP (example: http://192.168.1.50:3002/data).";
    }
  } catch {
    return "";
  }

  return "";
};

const wrapFetchNetworkError = (
  requestUrl: string,
  resourceLabel: string,
  error: unknown,
): Error => {
  const message =
    error instanceof Error ? error.message : String(error ?? "unknown error");
  const hint = buildNetworkHint(requestUrl);
  return new Error(
    `Static ${resourceLabel} network request failed: ${requestUrl} (${message}).${hint}`,
  );
};

const reportStaticUrlDiagnostics = (): void => {
  if (!__DEV__ || staticUrlDiagnosticsReported) {
    return;
  }

  staticUrlDiagnosticsReported = true;
  const metroHost = getMetroHostCandidate() ?? "unknown";
  console.info(
    `[static-data] base=${STATIC_DATA_BASE_URL} bundles=${STATIC_BUNDLES_BASE_URL} platform=${Platform.OS} metroHost=${metroHost}`,
  );
};

const parseStaticJsonPayload = <T>(
  payload: string,
  requestUrl: string,
  contentType: string,
  resourceLabel: string,
): T => {
  if (looksLikeHtmlPayload(payload)) {
    const preview = truncateForError(payload) || "[empty]";
    throw new Error(
      `Static ${resourceLabel} returned HTML instead of JSON: ${requestUrl} (preview: ${preview})`,
    );
  }

  try {
    return JSON.parse(payload) as T;
  } catch {
    const contentTypeLabel = contentType || "unknown";
    const preview = truncateForError(payload) || "[empty]";
    throw new Error(
      `Invalid JSON for static ${resourceLabel}: ${requestUrl} (content-type: ${contentTypeLabel}, preview: ${preview})`,
    );
  }
};

export const getBooks = async (): Promise<BookResponse[]> => {
  const metadata = await staticDataRequest<{ books: BookResponse[] }>(
    "metadata.json",
  );
  return metadata.books;
};

export const staticDataRequest = async <T>(
  relativePath: string,
): Promise<T> => {
  reportStaticUrlDiagnostics();

  const normalizedPath = relativePath.replace(/^\/+/, "");
  const cacheKey = normalizedPath;

  if (staticDataCache.has(cacheKey)) {
    return staticDataCache.get(cacheKey) as T;
  }

  const requestUrl = `${STATIC_DATA_BASE_URL}/${encodeURIComponent(normalizedPath).replace(/%2F/g, "/")}`;
  let response: Response;
  try {
    response = await fetch(requestUrl);
  } catch (error) {
    throw wrapFetchNetworkError(requestUrl, `data ${normalizedPath}`, error);
  }
  const contentType = response.headers.get("content-type") || "";
  const payload = await response.text();

  if (!response.ok) {
    const contentTypeLabel = contentType || "unknown";
    const preview = truncateForError(payload) || "[empty]";
    throw new Error(
      `Static data request failed for ${normalizedPath} with status ${response.status} (url: ${requestUrl}, content-type: ${contentTypeLabel}, preview: ${preview})`,
    );
  }

  const parsed = parseStaticJsonPayload<T>(
    payload,
    requestUrl,
    contentType,
    `data ${normalizedPath}`,
  );
  staticDataCache.set(cacheKey, parsed as unknown);
  return parsed;
};

export const staticBundleRequest = async <T>(
  bundleName: string,
): Promise<T> => {
  return staticBundlePathRequest<T>(`${bundleName}.json`);
};

export const staticBundlePathRequest = async <T>(
  relativePath: string,
): Promise<T> => {
  reportStaticUrlDiagnostics();

  const normalizedPath = relativePath.replace(/^\/+/, "");
  const requestUrl = `${STATIC_BUNDLES_BASE_URL}/${encodeURIComponent(normalizedPath).replace(/%2F/g, "/")}`;
  let response: Response;
  try {
    response = await fetch(requestUrl);
  } catch (error) {
    throw wrapFetchNetworkError(requestUrl, `bundle ${normalizedPath}`, error);
  }
  const contentType = response.headers.get("content-type") || "";
  const payload = await response.text();

  if (!response.ok) {
    const contentTypeLabel = contentType || "unknown";
    const preview = truncateForError(payload) || "[empty]";
    throw new Error(
      `Static bundle request failed for ${normalizedPath} with status ${response.status} (url: ${requestUrl}, content-type: ${contentTypeLabel}, preview: ${preview})`,
    );
  }

  return parseStaticJsonPayload<T>(
    payload,
    requestUrl,
    contentType,
    `bundle ${normalizedPath}`,
  );
};
