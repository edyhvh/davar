import { Platform } from "react-native";
import type { BookResponse } from "@/src/types/api";

const resolveApiBaseUrl = (): string => {
  const envUrl = process.env.EXPO_PUBLIC_API_BASE_URL;
  if (!envUrl) return "http://localhost:2220";
  // Android emulator needs 10.0.2.2 to reach host, iOS uses localhost
  if (Platform.OS === "ios") {
    return envUrl.replace("10.0.2.2", "localhost");
  }
  return envUrl;
};

const API_BASE_URL = resolveApiBaseUrl();
const API_KEY = process.env.EXPO_PUBLIC_API_KEY;

export const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> => {
  if (!API_KEY) {
    console.warn(
      "EXPO_PUBLIC_API_KEY is not set; sending request without X-API-Key header.",
    );
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
};

export const getBooks = async (): Promise<BookResponse[]> => {
  return apiRequest<BookResponse[]>("/api/v1/books");
};
