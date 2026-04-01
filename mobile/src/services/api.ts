import type { BookResponse } from "@/src/types/api";
import { Platform } from "react-native";

const DEV_STATIC_DATA_BASE_URL = "http://127.0.0.1:3002/data";
const PROD_STATIC_DATA_BASE_URL = "https://davar.bible/data";

const staticDataCache = new Map<string, unknown>();

const normalizeBaseUrl = (url: string): string => url.replace(/\/+$/, "");

const mapLoopbackForAndroidEmulator = (url: string): string => {
  if (!__DEV__ || Platform.OS !== "android") {
    return url;
  }

  try {
    const parsed = new URL(url);
    if (parsed.hostname === "127.0.0.1" || parsed.hostname === "localhost") {
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
  const normalizedPath = relativePath.replace(/^\/+/, "");
  const cacheKey = normalizedPath;

  if (staticDataCache.has(cacheKey)) {
    return staticDataCache.get(cacheKey) as T;
  }

  const requestUrl = `${STATIC_DATA_BASE_URL}/${encodeURIComponent(normalizedPath).replace(/%2F/g, "/")}`;
  const response = await fetch(requestUrl);
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
  const normalizedPath = relativePath.replace(/^\/+/, "");
  const requestUrl = `${STATIC_BUNDLES_BASE_URL}/${encodeURIComponent(normalizedPath).replace(/%2F/g, "/")}`;
  const response = await fetch(requestUrl);
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
