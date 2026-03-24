type Env = {
  BACKEND_API_ORIGIN?: string;
};

type FunctionContext<TEnv> = {
  request: Request;
  env: TEnv;
};

type CacheStorageWithDefault = CacheStorage & {
  default?: Cache;
};

const CACHEABLE_READ_PATH_PREFIXES = [
  "/api/v1/verses/",
  "/api/v1/metadata/preload",
];

const EDGE_CACHE_MAX_AGE_SECONDS = 600;
const EDGE_CACHE_STALE_WHILE_REVALIDATE_SECONDS = 86400;
const EDGE_CACHE_NAME = "davar-edge-cache";
const DEFAULT_BACKEND_API_ORIGIN = "https://api.davar.bible";

const isCacheableReadRequest = (method: string, path: string): boolean => {
  if (method !== "GET" && method !== "HEAD") {
    return false;
  }

  return CACHEABLE_READ_PATH_PREFIXES.some((prefix) => path.startsWith(prefix));
};

const buildBackendUrl = (requestUrl: URL, backendOrigin: string): URL => {
  const target = new URL(
    requestUrl.pathname + requestUrl.search,
    backendOrigin,
  );
  return target;
};

const withEdgeHeaders = (
  response: Response,
  cacheStatus: "HIT" | "MISS",
): Response => {
  const headers = new Headers(response.headers);
  headers.set("X-Davar-Edge-Cache", cacheStatus);
  if (!headers.has("Cache-Control")) {
    headers.set(
      "Cache-Control",
      `public, s-maxage=${EDGE_CACHE_MAX_AGE_SECONDS}, stale-while-revalidate=${EDGE_CACHE_STALE_WHILE_REVALIDATE_SECONDS}`,
    );
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
};

const getEdgeCache = async (): Promise<Cache> => {
  const storage = caches as CacheStorageWithDefault;
  return storage.default ?? caches.open(EDGE_CACHE_NAME);
};

export const onRequest = async (
  context: FunctionContext<Env>,
): Promise<Response> => {
  const { request, env } = context;
  const incomingUrl = new URL(request.url);
  const backendOrigin =
    env.BACKEND_API_ORIGIN?.trim() || DEFAULT_BACKEND_API_ORIGIN;
  const targetUrl = buildBackendUrl(incomingUrl, backendOrigin);
  const cacheableReadRequest = isCacheableReadRequest(
    request.method,
    incomingUrl.pathname,
  );

  const cache = await getEdgeCache();
  const cacheKey = new Request(incomingUrl.toString(), {
    method: "GET",
    headers: request.headers,
  });

  if (cacheableReadRequest) {
    const cachedResponse = await cache.match(cacheKey);
    if (cachedResponse) {
      return withEdgeHeaders(cachedResponse, "HIT");
    }
  }

  const upstreamRequest = new Request(targetUrl.toString(), request);
  const upstreamResponse = await fetch(upstreamRequest);

  if (!cacheableReadRequest) {
    return upstreamResponse;
  }

  const responseForClient = withEdgeHeaders(upstreamResponse, "MISS");

  if (responseForClient.ok) {
    await cache.put(cacheKey, responseForClient.clone());
  }

  return responseForClient;
};
