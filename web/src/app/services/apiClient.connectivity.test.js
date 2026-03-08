import { describe, expect, test } from "bun:test";

import { resolveApiClientConfig } from "./apiClient";

describe("apiClient connectivity safeguards", () => {
  test("uses production backend fallback when production API base URL is missing", () => {
    const config = resolveApiClientConfig({
      env: { PUBLIC_NODE_ENV: "production" },
      processEnv: {},
    });

    expect(config.apiBaseUrl).toBe("https://davar.onrender.com");
    expect(config.apiBaseUrl.includes("localhost")).toBe(false);
    expect(config.usedFallbackApiBaseUrl).toBe(true);
  });

  test("keeps localhost fallback in development", () => {
    const config = resolveApiClientConfig({
      env: { PUBLIC_NODE_ENV: "development" },
      processEnv: {},
    });

    expect(config.apiBaseUrl).toBe("http://localhost:2220");
    expect(config.isDev).toBe(true);
  });
});

const runLiveConnectivity = Bun.env.RUN_LIVE_CONNECTIVITY_TEST === "1";

describe.if(runLiveConnectivity)("live backend connectivity", () => {
  test("health endpoint is reachable", async () => {
    const baseUrl = Bun.env.PUBLIC_API_BASE_URL || "https://davar.onrender.com";
    const response = await fetch(`${baseUrl}/health`);

    expect(response.ok).toBe(true);

    const body = await response.json();
    expect(body.status).toBe("healthy");
  });

  test("books endpoint responds with authenticated payload", async () => {
    const baseUrl = Bun.env.PUBLIC_API_BASE_URL || "https://davar.onrender.com";
    const apiKey = Bun.env.PUBLIC_API_KEY;

    if (!apiKey) {
      throw new Error(
        "PUBLIC_API_KEY is required when RUN_LIVE_CONNECTIVITY_TEST=1",
      );
    }

    const response = await fetch(`${baseUrl}/api/v1/books`, {
      headers: {
        "X-API-Key": apiKey,
      },
    });

    expect(response.ok).toBe(true);

    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length > 0).toBe(true);
  });
});
