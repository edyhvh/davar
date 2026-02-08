import { apiRequest } from "@/src/services/api";
import type { VerseResponse, TranslationFootnote } from "@/src/types/api";

export type DisplayWord = {
  position: number;
  text: string;
  strong?: string;
  prefixes?: string[];
  hasQumranVariant?: boolean;
  morph?: string;
  translit_en?: string;
  translit_es?: string;
  dss_translit_en?: string;
  dss_translit_es?: string;
  dssWord?: string;
  dssStrong?: string;
  dssCommentaryEn?: string;
  dssCommentaryEs?: string;
  dssCommentaryHe?: string;
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
  qumranVariants?: { position: number; dssWord: string }[];
  translation_footnotes?: TranslationFootnote[];
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
      position: Math.max(variant.position, 0),
      dssWord: variant.dss_word,
    }));

    const dssVariantMap = new Map(
      verse.dss?.map((variant) => [variant.position, variant]) ?? [],
    );

    const words = verse.words.map((word) => {
      const dssVariant = dssVariantMap.get(word.position);
      return {
        position: word.position,
        text: word.text,
        strong: word.strong,
        prefixes: word.prefixes,
        hasQumranVariant: word.has_dss_variant,
        morph: word.morph,
        translit_en: word.translit_en,
        translit_es: word.translit_es,
        dss_translit_en: dssVariant?.dss_translit_en,
        dss_translit_es: dssVariant?.dss_translit_es,
        dssWord: dssVariant?.dss_word,
        dssStrong: dssVariant?.dss_strong,
        dssCommentaryEn: dssVariant?.comment_v2_en,
        dssCommentaryEs: dssVariant?.comment_v2_es,
        dssCommentaryHe: dssVariant?.comment_v2_he,
      };
    });

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
      translation_footnotes: verse.translation_footnotes,
    };
  });
};
