import { apiRequest } from "@/src/services/api";
import type { VerseResponse } from "@/src/types/api";

export type DisplayWord = {
  text: string;
  strong?: string;
  prefixes?: string[];
  hasQumranVariant?: boolean;
  morph?: string;
};

export type DisplayVerse = {
  id: string;
  book: string;
  bookId: string;
  chapter: number;
  verse: number;
  hebrew: string;
  translation: string;
  words: DisplayWord[];
  qumranVariants?: { wordIndex: number; variant: string }[];
};

const formatBookName = (bookId: string) =>
  bookId.charAt(0).toUpperCase() + bookId.slice(1);

export const fetchChapterVerses = async (
  bookId: string,
  chapter: number,
  options?: {
    language?: "en" | "es";
    showDss?: boolean;
    hebrewOnly?: boolean;
  },
): Promise<DisplayVerse[]> => {
  const params = new URLSearchParams();
  if (options?.language) params.set("language", options.language);
  if (options?.showDss) params.set("show_dss", "true");
  if (options?.hebrewOnly) params.set("hebrew_only", "true");

  const query = params.toString();
  const url = query
    ? `/api/v1/verses/${bookId}/${chapter}?${query}`
    : `/api/v1/verses/${bookId}/${chapter}`;

  const verses = await apiRequest<VerseResponse[]>(url);
  return verses.map((verse) => {
    const qumranVariants = verse.dss?.map((variant) => ({
      wordIndex: Math.max(variant.word_position - 1, 0),
      variant: variant.dss_text,
    }));

    const words = verse.words.map((word) => ({
      text: word.text,
      strong: word.strong,
      prefixes: word.prefixes,
      hasQumranVariant: word.has_dss_variant,
      morph: word.morph,
    }));

    return {
      id: `${bookId}-${verse.chapter}-${verse.verse}`,
      book: formatBookName(bookId),
      bookId,
      chapter: verse.chapter,
      verse: verse.verse,
      hebrew: verse.hebrew,
      translation: verse.translation ?? "",
      words,
      qumranVariants,
    };
  });
};
