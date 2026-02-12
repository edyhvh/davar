import { apiRequest } from "@/src/services/api";
import type {
  VerseResponse,
  TranslationFootnote,
  WordResponse,
  DssVariant,
} from "@/src/types/api";
import {
  fetchHebrewVerses,
  fetchTranslationVerses,
  fetchDssVariants,
  type HebrewVerseRow,
  type TranslationRow,
  type DssVariantRow,
} from "@/src/services/database";

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

// ── Shared mapping: API response → DisplayVerse[] ──────────────────────────

const mapApiVersesToDisplay = (
  bookId: string,
  verses: VerseResponse[],
): DisplayVerse[] => {
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

// ── Offline mapping: SQLite rows → DisplayVerse[] ──────────────────────────

const mapOfflineDataToDisplay = (
  bookId: string,
  hebrewRows: HebrewVerseRow[],
  translationRows: TranslationRow[],
  dssRows: DssVariantRow[],
): DisplayVerse[] => {
  // Index translations by verse number
  const translationMap = new Map<string, TranslationRow>();
  for (const tr of translationRows) {
    translationMap.set(`${tr.chapter}-${tr.verse}`, tr);
  }

  // Group DSS variants by chapter-verse
  const dssMap = new Map<string, DssVariantRow[]>();
  for (const dss of dssRows) {
    const key = `${dss.chapter}-${dss.verse}`;
    const existing = dssMap.get(key) ?? [];
    existing.push(dss);
    dssMap.set(key, existing);
  }

  return hebrewRows.map((hv) => {
    const verseKey = `${hv.chapter}-${hv.verse}`;
    const translation = translationMap.get(verseKey);
    const dssVariants = dssMap.get(verseKey) ?? [];

    // Build DSS variant lookup by position
    const dssPositionMap = new Map<number, DssVariantRow>();
    for (const dss of dssVariants) {
      dssPositionMap.set(dss.position, dss);
    }

    const wordObjects = Array.isArray(hv.words) ? hv.words : [];
    const words: DisplayWord[] = wordObjects
      .filter((word) => word && typeof word === "object")
      .map((word, index) => {
        const typedWord = word as WordResponse;
        const position = typedWord.position ?? index;
        const dssVariant = dssPositionMap.get(position);
        const dssData = dssVariant?.data as
          | Record<string, string | undefined>
          | undefined;

        return {
          position,
          text: typedWord.text ?? "",
          strong: typedWord.strong,
          prefixes: typedWord.prefixes ?? [],
          hasQumranVariant: Boolean(dssVariant),
          morph: typedWord.morph,
          translit_en: typedWord.translit_en,
          translit_es: typedWord.translit_es,
          dssWord: dssData?.dss_word,
          dssStrong: dssData?.dss_strong,
          dssCommentaryEn: dssData?.comment_v2_en,
          dssCommentaryEs: dssData?.comment_v2_es,
          dssCommentaryHe: dssData?.comment_v2_he,
        };
      });

    const qumranVariants = dssVariants.map((dss) => ({
      position: Math.max(dss.position, 0),
      dssWord: (dss.data as Record<string, string>)?.dss_word ?? "",
    }));

    // Reconstruct hebrew text from words if not stored directly
    const hebrew = words.map((w) => w.text).join(" ");

    // Parse footnotes from translation row
    let translationFootnotes: TranslationFootnote[] | undefined;
    if (translation?.footnotes && Array.isArray(translation.footnotes)) {
      translationFootnotes = translation.footnotes as TranslationFootnote[];
    }

    return {
      id: `${bookId}-${hv.chapter}-${hv.verse}`,
      book: formatBookName(bookId),
      bookId,
      chapter: hv.chapter,
      verse: hv.verse,
      hebrew,
      translation: translation?.text ?? "",
      words,
      qumranVariants: qumranVariants.length > 0 ? qumranVariants : undefined,
      translation_footnotes: translationFootnotes,
    };
  });
};

// ── Offline fetch from SQLite ──────────────────────────────────────────────

const fetchChapterVersesOffline = async (
  bookId: string,
  chapter: number,
  options?: {
    language?: "en" | "es";
    showDss?: boolean;
  },
): Promise<DisplayVerse[]> => {
  const hebrewRows = await fetchHebrewVerses(bookId, chapter);
  if (hebrewRows.length === 0) {
    throw new Error(`No offline Hebrew data for ${bookId} chapter ${chapter}`);
  }

  const translationRows = options?.language
    ? await fetchTranslationVerses(bookId, chapter, options.language)
    : [];

  const dssRows = options?.showDss
    ? await fetchDssVariants(bookId, chapter)
    : [];

  return mapOfflineDataToDisplay(bookId, hebrewRows, translationRows, dssRows);
};

export const fetchChapterVerses = async (
  bookId: string,
  chapter: number,
  options?: {
    language?: "en" | "es";
    showDss?: boolean;
    hebrewOnly?: boolean;
    isConnected?: boolean;
  },
): Promise<DisplayVerse[]> => {
  // If explicitly offline, go straight to SQLite
  if (options?.isConnected === false) {
    return fetchChapterVersesOffline(bookId, chapter, options);
  }

  // Try API first, fall back to SQLite on failure
  try {
    const params = new URLSearchParams();
    if (options?.language) params.set("language", options.language);
    if (options?.showDss) params.set("show_dss", "true");
    if (options?.hebrewOnly) params.set("hebrew_only", "true");

    const query = params.toString();
    const url = query
      ? `/api/v1/verses/${bookId}/${chapter}?${query}`
      : `/api/v1/verses/${bookId}/${chapter}`;

    const verses = await apiRequest<VerseResponse[]>(url);
    return mapApiVersesToDisplay(bookId, verses);
  } catch (apiError) {
    // API failed — try offline data as fallback
    console.debug(
      `API fetch failed for ${bookId}/${chapter}, trying offline:`,
      apiError,
    );
    try {
      return await fetchChapterVersesOffline(bookId, chapter, options);
    } catch {
      // Neither API nor offline worked — re-throw original API error
      throw apiError;
    }
  }
};
