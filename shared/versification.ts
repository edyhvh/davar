import {
  type BookVersificationEntry,
  type VersificationType,
  VERSIFICATION_DATA,
} from "./versificationData";

export type VerseReference = {
  chapter: number;
  verse: number;
};

const APP_BOOK_TO_VERSIFICATION_CODE: Record<string, string> = {
  genesis: "GEN",
  exodus: "EXO",
  leviticus: "LEV",
  numbers: "NUM",
  deuteronomy: "DEU",
  samuel1: "1SA",
  samuel2: "2SA",
  kings1: "1KI",
  kings2: "2KI",
  chronicles1: "1CH",
  chronicles2: "2CH",
  nehemiah: "NEH",
  job: "JOB",
  psalms: "PSA",
  ecclesiastes: "ECC",
  songofsolomon: "SNG",
  isaiah: "ISA",
  jeremiah: "JER",
  ezekiel: "EZK",
  daniel: "DAN",
  hosea: "HOS",
  joel: "JOL",
  jonah: "JON",
  micah: "MIC",
  nahum: "NAM",
  malachi: "MAL",
  zechariah: "ZEC",
};

type ParsedVersificationEntry = {
  type: VersificationType;
  forward: Map<string, VerseReference>;
  reverse: Map<string, VerseReference>;
  // Chapters that appear in the simple_map (i.e., have versification shifts).
  // For superscription_shift books, verses in these chapters that have no
  // reverse mapping are superscriptions and should return null.
  mappedChapters: Set<number>;
};

const parsedVersificationByCode: Record<string, ParsedVersificationEntry> = {};

const makeRefKey = (chapter: number, verse: number): string => `${chapter}:${verse}`;

const parseRefValue = (value: string): VerseReference | null => {
  const [chapterToken, verseToken] = value.split(":");
  const chapter = Number(chapterToken);
  const verse = Number(verseToken);

  if (!Number.isFinite(chapter) || !Number.isFinite(verse)) {
    return null;
  }

  return { chapter, verse };
};

const normalizeBookToken = (value: string): string =>
  value.toLowerCase().replace(/[^a-z0-9]/g, "");

const parseVersificationEntry = (
  entry: BookVersificationEntry,
): ParsedVersificationEntry => {
  const forward = new Map<string, VerseReference>();
  const reverse = new Map<string, VerseReference>();

  for (const [sourceChapterToken, chapterMap] of Object.entries(entry.simple_map ?? {})) {
    const sourceChapter = Number(sourceChapterToken);
    if (!Number.isFinite(sourceChapter)) {
      continue;
    }

    for (const [sourceVerseToken, targetRefToken] of Object.entries(chapterMap ?? {})) {
      const sourceVerse = Number(sourceVerseToken);
      if (!Number.isFinite(sourceVerse)) {
        continue;
      }

      const targetRef = parseRefValue(targetRefToken);
      if (!targetRef) {
        continue;
      }

      const sourceRef: VerseReference = {
        chapter: sourceChapter,
        verse: sourceVerse,
      };

      forward.set(makeRefKey(sourceRef.chapter, sourceRef.verse), targetRef);

      const reverseKey = makeRefKey(targetRef.chapter, targetRef.verse);
      if (!reverse.has(reverseKey)) {
        reverse.set(reverseKey, sourceRef);
      }
    }
  }

  const mappedChapters = new Set<number>();
  for (const sourceChapterToken of Object.keys(entry.simple_map ?? {})) {
    const ch = Number(sourceChapterToken);
    if (Number.isFinite(ch)) mappedChapters.add(ch);
  }

  return {
    type: entry.type,
    forward,
    reverse,
    mappedChapters,
  };
};

const resolveVersificationBookCode = (bookId: string): string | undefined => {
  if (!bookId) return undefined;

  const normalized = normalizeBookToken(bookId);

  if (APP_BOOK_TO_VERSIFICATION_CODE[normalized]) {
    return APP_BOOK_TO_VERSIFICATION_CODE[normalized];
  }

  const upper = bookId.toUpperCase();
  if (VERSIFICATION_DATA[upper]) {
    return upper;
  }

  return undefined;
};

const getParsedVersificationForBook = (
  bookId: string,
): ParsedVersificationEntry | undefined => {
  const code = resolveVersificationBookCode(bookId);
  if (!code) {
    return undefined;
  }

  if (!parsedVersificationByCode[code]) {
    const entry = VERSIFICATION_DATA[code];
    if (!entry) {
      return undefined;
    }

    parsedVersificationByCode[code] = parseVersificationEntry(entry);
  }

  return parsedVersificationByCode[code];
};

export const mapHebrewVerseToTranslationReference = (
  bookId: string,
  chapter: number,
  verse: number,
): VerseReference | null => {
  if (!Number.isFinite(chapter) || !Number.isFinite(verse)) {
    return null;
  }

  if (chapter <= 0 || verse <= 0) {
    return { chapter, verse };
  }

  const versification = getParsedVersificationForBook(bookId);
  if (!versification) {
    return { chapter, verse };
  }

  const key = makeRefKey(chapter, verse);

  if (versification.type === "superscription_shift") {
    // Psalms superscriptions are represented as verse 0 in the mapping source system.
    const mappedSource = versification.reverse.get(key);

    if (!mappedSource) {
      // If this chapter is in the simple_map but has no reverse entry, the
      // verse is a superscription line (e.g. Psalms with 2 superscription
      // verses where only source key >= 1 appears in the map).
      if (versification.mappedChapters.has(chapter)) {
        return null;
      }
      return { chapter, verse };
    }

    if (mappedSource.verse <= 0) {
      return null;
    }

    return mappedSource;
  }

  return versification.forward.get(key) ?? { chapter, verse };
};

export const mapHebrewVerseToTranslationKey = (
  bookId: string,
  chapter: number,
  verse: number,
): string | null => {
  const mapped = mapHebrewVerseToTranslationReference(bookId, chapter, verse);
  if (!mapped) {
    return null;
  }

  return `${mapped.chapter}-${mapped.verse}`;
};
