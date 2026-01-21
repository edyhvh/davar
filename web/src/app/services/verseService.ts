import { apiRequest } from "./apiClient";

export interface WordResponse {
  position: number;
  text: string;
  text_no_nikud: string;
  strong?: string;
  morph?: string;
  prefixes: string[];
  has_dss_variant: boolean;
}

export interface DssVariant {
  word_position: number;
  dss_text: string;
  manuscript: string;
  commentary?: string;
}

export interface TranslationFootnote {
  marker: string;
  number: string;
  word: string;
  explanation: string;
}

export interface VerseResponse {
  chapter: number;
  verse: number;
  hebrew: string;
  hebrew_no_nikud: string;
  words: WordResponse[];
  translation?: string;
  translation_language?: string;
  translation_footnotes?: TranslationFootnote[];
  dss?: DssVariant[];
}

export interface BookResponse {
  id: string;
  name: string;
  section: "torah" | "neviim" | "ketuvim" | "besorah";
  chapters: number;
  order: "tanaj" | "besorah";
  hebrew_name: string;
  hebrew_transliteration: string;
  spanish_name: string;
}

type ChapterResponse = { book: string; chapters: number[] };
type VerseCountResponse = {
  book: string;
  chapter: number;
  verse_count: number;
};

export const getBooks = async (): Promise<BookResponse[]> => {
  return apiRequest<BookResponse[]>("/api/v1/books");
};

export const getChapterCount = async (book: string): Promise<number> => {
  const response = await apiRequest<ChapterResponse>(
    `/api/v1/books/${book}/chapters`,
  );
  return response.chapters.length;
};

export const getVerseCount = async (
  book: string,
  chapter: number,
): Promise<number> => {
  const response = await apiRequest<VerseCountResponse>(
    `/api/v1/books/${book}/chapters/${chapter}/verses`,
  );
  return response.verse_count;
};

export const getChapterVerses = async (
  book: string,
  chapter: number,
  options?: {
    language?: "es" | "en";
    showDss?: boolean;
    hebrewOnly?: boolean;
  },
): Promise<VerseResponse[]> => {
  const params = new URLSearchParams();
  if (options?.language) params.set("language", options.language);
  if (options?.showDss) params.set("show_dss", "true");
  if (options?.hebrewOnly) params.set("hebrew_only", "true");

  const query = params.toString();
  const url = query
    ? `/api/v1/verses/${book}/${chapter}?${query}`
    : `/api/v1/verses/${book}/${chapter}`;
  return apiRequest<VerseResponse[]>(url);
};

export const getVerse = async (
  book: string,
  chapter: number,
  verse: number,
  options?: {
    language?: "es" | "en";
    showDss?: boolean;
    hebrewOnly?: boolean;
  },
): Promise<VerseResponse | null> => {
  const params = new URLSearchParams();
  if (options?.language) params.set("language", options.language);
  if (options?.showDss) params.set("show_dss", "true");
  if (options?.hebrewOnly) params.set("hebrew_only", "true");
  const query = params.toString();
  const url = query
    ? `/api/v1/verses/${book}/${chapter}/${verse}?${query}`
    : `/api/v1/verses/${book}/${chapter}/${verse}`;
  return apiRequest<VerseResponse>(url);
};
