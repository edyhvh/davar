import * as FileSystem from "expo-file-system";
import { apiRequest } from "@/src/services/api";
import type { LexiconResponse } from "@/src/types/api";
import {
  insertLexiconEntries,
  insertTranslationVerses,
  initializeDatabase,
} from "@/src/services/database";

const OFFLINE_DIR = `${FileSystem.documentDirectory}offline`;

const ensureOfflineDir = async () => {
  const info = await FileSystem.getInfoAsync(OFFLINE_DIR);
  if (!info.exists) {
    await FileSystem.makeDirectoryAsync(OFFLINE_DIR, { intermediates: true });
  }
};

// ── Dictionary Bundle Types ────────────────────────────────────────────────

interface DefinitionItem {
  text_en?: string;
  text_es?: string;
  source?: string;
}

interface CustomDefinitionEntry {
  strong_number: string;
  hebrew?: string;
  transliteration_en?: string;
  transliteration_es?: string;
  definitions: DefinitionItem[];
  root?: string;
  root_strong?: string;
}

interface RootEntry {
  strong_number: string;
  lemma: string;
  transliteration: string;
  definitions: DefinitionItem[];
  root?: string;
  root_strong?: string;
  occurrences_count?: number;
}

interface DictionaryBundle {
  custom_definitions: Record<string, CustomDefinitionEntry>;
  roots: Record<string, RootEntry>;
  prefixes: Record<string, any>; // can be refined later if needed
}

// ── Translation Bundle Types ───────────────────────────────────────────────

interface TthVerse {
  verse: number;
  tth: string;
  footnotes?: unknown[];
}

interface TthChapter {
  chapter: number;
  verses: TthVerse[];
}

interface TthBookData {
  chapters: TthChapter[];
}

interface Ts2009Verse {
  chapter: number;
  verse: number;
  text: string;
}

interface Ts2009BookData {
  verses: Ts2009Verse[];
}

interface TranslationBundle {
  books: Record<string, TthBookData | Ts2009BookData>;
}

// ── Lexicon builder ────────────────────────────────────────────────────────

const buildLexiconEntries = (bundle: DictionaryBundle): LexiconResponse[] => {
  const entries: LexiconResponse[] = [];

  // Custom definitions
  Object.values(bundle.custom_definitions ?? {}).forEach(
    (entry: CustomDefinitionEntry) => {
      const definitions = (entry.definitions ?? []).flatMap(
        (item: DefinitionItem) => {
          const defs: LexiconResponse["definitions"] = [];
          if (item.text_en) {
            defs.push({
              text: item.text_en,
              source: item.source ?? "custom",
              language: "en",
            });
          }
          if (item.text_es) {
            defs.push({
              text: item.text_es,
              source: item.source ?? "custom",
              language: "es",
            });
          }
          return defs;
        },
      );

      entries.push({
        strong_number: entry.strong_number,
        hebrew: entry.hebrew ?? null,
        transliteration:
          entry.transliteration_en ?? entry.transliteration_es ?? null,
        definitions,
        root: entry.root ?? null,
        root_strong: entry.root_strong ?? null,
        root_definitions: [],
        occurrences_count: 0,
      });
    },
  );

  // Roots lexicon
  Object.values(bundle.roots ?? {}).forEach((entry: RootEntry) => {
    const definitions = (entry.definitions ?? []).flatMap(
      (item: DefinitionItem) => {
        const defs: LexiconResponse["definitions"] = [];
        if (item.text_en) {
          defs.push({
            text: item.text_en,
            source: item.source ?? "bdb",
            language: "en",
          });
        }
        if (item.text_es) {
          defs.push({
            text: item.text_es,
            source: item.source ?? "bdb",
            language: "es",
          });
        }
        return defs;
      },
    );

    entries.push({
      strong_number: entry.strong_number,
      hebrew: entry.lemma,
      transliteration: entry.transliteration ?? null,
      definitions,
      root: entry.root ?? null,
      root_strong: entry.root_strong ?? null,
      root_definitions: [],
      occurrences_count: entry.occurrences_count ?? 0,
    });
  });

  return entries;
};

export const downloadDictionaryBundle = async () => {
  await initializeDatabase();
  const bundle = await apiRequest<DictionaryBundle>(
    "/api/v1/export/bundle/dictionary",
  );
  const entries = buildLexiconEntries(bundle);
  await insertLexiconEntries(entries);

  await ensureOfflineDir();
  await FileSystem.writeAsStringAsync(
    `${OFFLINE_DIR}/dictionary.json`,
    JSON.stringify({ downloadedAt: new Date().toISOString() }),
  );
};

// ── Translation extractors ─────────────────────────────────────────────────

const extractTthVerses = (bookData: TthBookData): TranslationRow[] => {
  const rows: TranslationRow[] = [];
  for (const chapter of bookData.chapters ?? []) {
    for (const verse of chapter.verses ?? []) {
      rows.push({
        chapter: chapter.chapter,
        verse: verse.verse,
        text: verse.tth ?? "",
        footnotes: verse.footnotes ?? [],
      });
    }
  }
  return rows;
};

const extractTs2009Verses = (bookData: Ts2009BookData): TranslationRow[] => {
  const rows: TranslationRow[] = [];
  for (const verse of bookData.verses ?? []) {
    rows.push({
      chapter: verse.chapter,
      verse: verse.verse,
      text: verse.text ?? "",
      footnotes: [], // ts2009 apparently has no footnotes in current bundle
    });
  }
  return rows;
};

export const downloadTranslationBundle = async (language: "es" | "en") => {
  await initializeDatabase();

  const dataset = language === "es" ? "tth" : "ts2009";
  const bundle = await apiRequest<TranslationBundle>(
    `/api/v1/export/bundle/${dataset}`,
  );

  for (const [bookId, bookData] of Object.entries(bundle.books ?? {})) {
    const rows =
      language === "es"
        ? extractTthVerses(bookData as TthBookData)
        : extractTs2009Verses(bookData as Ts2009BookData);

    await insertTranslationVerses(rows, language, bookId);
  }

  await ensureOfflineDir();
  await FileSystem.writeAsStringAsync(
    `${OFFLINE_DIR}/translations-${language}.json`,
    JSON.stringify({ downloadedAt: new Date().toISOString() }),
  );
};
