import { apiRequest } from "./apiClient";

export interface DefinitionItem {
  text: string;
  source: "custom" | "strong" | "bdb" | string;
  language: "en" | "es" | string;
}

export interface WordAnalysis {
  strong_number: string;
  hebrew?: string;
  translit_en?: string;
  translit_es?: string;
  definitions: DefinitionItem[];
  root?: string;
  root_strong?: string;
  root_definitions?: DefinitionItem[];
  root_translit_en?: string;
  root_translit_es?: string;
  occurrences_count: number;
  instances?: Array<string | { verse: string; text: string }>;
}

export const getWordAnalysisByStrong = async (
  strong?: string,
  language?: "en" | "es",
  displayHebrew?: string,
): Promise<WordAnalysis | null> => {
  if (!strong) return null;
  const params = new URLSearchParams();
  if (language) params.set("language", language);
  if (displayHebrew) params.set("hebrew", displayHebrew);
  const query = params.toString();
  const url = query
    ? `/api/v1/lexicon/${strong}?${query}`
    : `/api/v1/lexicon/${strong}`;
  return apiRequest<WordAnalysis>(url);
};

export const searchWordAnalysis = async (
  query: string,
  options?: { limit?: number; offset?: number },
): Promise<WordAnalysis[]> => {
  const params = new URLSearchParams();
  params.set("q", query);
  if (options?.limit) params.set("limit", String(options.limit));
  if (options?.offset) params.set("offset", String(options.offset));
  return apiRequest<WordAnalysis[]>(`/api/v1/search?${params.toString()}`);
};
