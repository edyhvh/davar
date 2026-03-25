import type { BookResponse } from "@/src/types/api";

const STATIC_BUNDLES_BASE_URL =
  process.env.EXPO_PUBLIC_STATIC_BUNDLES_BASE_URL ||
  "https://davar.bible/data/bundles";
const STATIC_DATA_BASE_URL =
  process.env.EXPO_PUBLIC_STATIC_DATA_BASE_URL || "https://davar.bible/data";

const staticDataCache = new Map<string, unknown>();

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

  const response = await fetch(
    `${STATIC_DATA_BASE_URL}/${encodeURIComponent(normalizedPath).replace(/%2F/g, "/")}`,
  );

  if (!response.ok) {
    throw new Error(
      `Static data request failed for ${normalizedPath} with status ${response.status}`,
    );
  }

  const parsed = (await response.json()) as T;
  staticDataCache.set(cacheKey, parsed as unknown);
  return parsed;
};

export const staticBundleRequest = async <T>(
  bundleName: string,
): Promise<T> => {
  const response = await fetch(
    `${STATIC_BUNDLES_BASE_URL}/${encodeURIComponent(bundleName)}.json`,
  );

  if (!response.ok) {
    throw new Error(
      `Static bundle request failed for ${bundleName} with status ${response.status}`,
    );
  }

  return response.json() as Promise<T>;
};
