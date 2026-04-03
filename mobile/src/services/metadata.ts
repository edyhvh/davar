import { staticDataRequest } from "@/src/services/api";
import type { BookResponse } from "@/src/types/api";

type MetadataResponse = {
  books: BookResponse[];
  chapter_counts: Record<string, number[]>;
  verse_counts: Record<string, Record<string, number>>;
};

const normalizeBookKey = (value: string): string =>
  value.toLowerCase().replace(/[^a-z0-9]/g, "");

const resolveBookId = (
  key: string,
  books: BookResponse[],
): string | undefined => {
  const normalizedKey = normalizeBookKey(key);
  const match = books.find((book) => {
    const normalizedId = normalizeBookKey(book.id);
    const normalizedName = normalizeBookKey(book.name);
    return normalizedKey === normalizedId || normalizedKey === normalizedName;
  });
  return match?.id;
};

export const fetchMetadata = async (): Promise<MetadataResponse> => {
  let raw: MetadataResponse;
  try {
    raw = await staticDataRequest<MetadataResponse>("metadata.json");
  } catch (error) {
    const message =
      error instanceof Error ? error.message : String(error ?? "unknown error");
    throw new Error(`Failed to fetch metadata.json (${message})`);
  }

  const chapterCounts: Record<string, number[]> = {};
  const verseCounts: Record<string, Record<string, number>> = {};

  for (const [key, chapters] of Object.entries(raw.chapter_counts ?? {})) {
    const bookId = resolveBookId(key, raw.books);
    if (!bookId) continue;
    chapterCounts[bookId] = chapters;
  }

  for (const [key, verses] of Object.entries(raw.verse_counts ?? {})) {
    const bookId = resolveBookId(key, raw.books);
    if (!bookId) continue;
    verseCounts[bookId] = verses;
  }

  return {
    books: raw.books,
    chapter_counts: chapterCounts,
    verse_counts: verseCounts,
  };
};
