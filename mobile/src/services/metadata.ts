import { apiRequest } from "@/src/services/api";
import type { BookResponse } from "@/src/types/api";

type MetadataResponse = {
  books: BookResponse[];
  chapter_counts: Record<string, number[]>;
  verse_counts: Record<string, Record<string, number>>;
};

export const fetchMetadata = async (): Promise<MetadataResponse> => {
  return apiRequest<MetadataResponse>("/api/v1/metadata/preload");
};
