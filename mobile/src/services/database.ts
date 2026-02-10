import * as SQLite from "expo-sqlite";
import type { LexiconResponse } from "@/src/types/api";

type ExecResult = {
  rows: {
    _array: unknown[];
  };
};

export type TranslationRow = {
  chapter: number;
  verse: number;
  text: string;
  footnotes?: unknown[];
};

const db = SQLite.openDatabaseSync("davar.db");

const CURRENT_SCHEMA_VERSION = 2;

// ── Custom error for better debugging ──────────────────────────────────────

class DatabaseError extends Error {
  constructor(
    message: string,
    public query: string,
    public params: (string | number | null)[],
    public originalError: unknown,
  ) {
    super(message);
    this.name = "DatabaseError";
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      query: this.query.trim().replace(/\s+/g, " "),
      params: this.params,
      original:
        this.originalError instanceof Error
          ? this.originalError.message
          : String(this.originalError),
    };
  }
}

// ── Low-level executor with error context ──────────────────────────────────

const executeSql = async (
  query: string,
  params: (string | number | null)[] = [],
): Promise<ExecResult> => {
  try {
    // db.runAsync historically returned an array of rows in this codebase.
    // Accept both the raw array or objects and normalize to { rows: { _array } }.
    const raw: unknown = await (
      db as unknown as {
        runAsync: (...args: unknown[]) => Promise<unknown>;
      }
    ).runAsync(query, ...params);

    if (Array.isArray(raw)) {
      return { rows: { _array: raw } };
    }

    // If the runtime returned an object with a `rows` property, try to normalize
    // that too, otherwise fall back to an empty array for safety.
    const normalized =
      (raw as { rows?: { _array?: unknown[] } })?.rows?._array ?? [];
    return { rows: { _array: normalized } };
  } catch (error) {
    const wrappedError = new DatabaseError(
      `SQLite execution failed`,
      query,
      params,
      error,
    );
    throw wrappedError;
  }
};

// ── Initialization ──────────────────────────────────────────────────────────

export const initializeDatabase = async () => {
  const versionResult = await executeSql("PRAGMA user_version;");
  const currentVersion =
    Number(
      (versionResult.rows._array?.[0] as Record<string, unknown>)?.user_version,
    ) || 0;

  await executeSql(
    `CREATE TABLE IF NOT EXISTS verses (
      id TEXT PRIMARY KEY,
      book TEXT NOT NULL,
      chapter INTEGER NOT NULL,
      verse INTEGER NOT NULL,
      text TEXT NOT NULL,
      language TEXT NOT NULL,
      footnotes TEXT
    );`,
  );

  await executeSql(
    `CREATE INDEX IF NOT EXISTS idx_verses_book_chapter 
     ON verses(book, chapter);`,
  );

  if (currentVersion < 2) {
    const lexiconInfo = await executeSql("PRAGMA table_info(lexicon);");
    const lexiconExists = (lexiconInfo.rows._array.length ?? 0) > 0;

    if (lexiconExists) {
      await executeSql(
        `CREATE TABLE IF NOT EXISTS lexicon_new (
          strong TEXT PRIMARY KEY,
          hebrew TEXT,
          definitions TEXT NOT NULL,
          root TEXT,
          root_strong TEXT,
          occurrences TEXT
        );`,
      );

      await executeSql(
        `INSERT OR REPLACE INTO lexicon_new (
          strong, hebrew, definitions, root, root_strong, occurrences
        )
        SELECT strong, hebrew, definitions, root, root_strong, occurrences
        FROM lexicon;`,
      );

      await executeSql("DROP TABLE lexicon;");
      await executeSql("ALTER TABLE lexicon_new RENAME TO lexicon;");
    } else {
      await executeSql(
        `CREATE TABLE IF NOT EXISTS lexicon (
          strong TEXT PRIMARY KEY,
          hebrew TEXT,
          definitions TEXT NOT NULL,
          root TEXT,
          root_strong TEXT,
          occurrences TEXT
        );`,
      );
    }

    await executeSql(
      `CREATE INDEX IF NOT EXISTS idx_lexicon_hebrew 
       ON lexicon(hebrew);`,
    );

    await executeSql(`PRAGMA user_version = ${CURRENT_SCHEMA_VERSION};`);
  } else {
    await executeSql(
      `CREATE TABLE IF NOT EXISTS lexicon (
        strong TEXT PRIMARY KEY,
        hebrew TEXT,
        definitions TEXT NOT NULL,
        root TEXT,
        root_strong TEXT,
        occurrences TEXT
      );`,
    );

    await executeSql(
      `CREATE INDEX IF NOT EXISTS idx_lexicon_hebrew 
       ON lexicon(hebrew);`,
    );
  }
};

// ── Bulk inserts with transaction safety ───────────────────────────────────

export const insertLexiconEntries = async (entries: LexiconResponse[]) => {
  await executeSql("BEGIN TRANSACTION;");

  try {
    for (const entry of entries) {
      await executeSql(
        `INSERT OR REPLACE INTO lexicon (
          strong, hebrew, definitions, root, root_strong, occurrences
        ) VALUES (?, ?, ?, ?, ?, ?);`,
        [
          entry.strong_number,
          entry.hebrew ?? null,
          JSON.stringify(entry.definitions ?? []),
          entry.root ?? null,
          entry.root_strong ?? null,
          JSON.stringify(entry.root_definitions ?? []),
        ],
      );
    }
    await executeSql("COMMIT;");
  } catch (error) {
    await executeSql("ROLLBACK;");
    throw error; // Already wrapped as DatabaseError
  }
};

export const insertTranslationVerses = async (
  verses: TranslationRow[],
  language: "en" | "es",
  bookId: string,
) => {
  await executeSql("BEGIN TRANSACTION;");

  try {
    for (const verse of verses) {
      const id = `${bookId}-${verse.chapter}-${verse.verse}`;
      await executeSql(
        `INSERT OR REPLACE INTO verses (
          id, book, chapter, verse, text, language, footnotes
        ) VALUES (?, ?, ?, ?, ?, ?, ?);`,
        [
          id,
          bookId,
          verse.chapter,
          verse.verse,
          verse.text,
          language,
          JSON.stringify(verse.footnotes ?? []),
        ],
      );
    }
    await executeSql("COMMIT;");
  } catch (error) {
    await executeSql("ROLLBACK;");
    throw error;
  }
};

export const deleteTranslationBookEntries = async (
  bookId: string,
  language: "en" | "es",
) => {
  await executeSql("DELETE FROM verses WHERE book = ? AND language = ?;", [
    bookId,
    language,
  ]);
};

// ── Queries ────────────────────────────────────────────────────────────────

export const fetchTranslationVerses = async (
  bookId: string,
  chapter: number,
  language: "en" | "es",
): Promise<TranslationRow[]> => {
  const result = await executeSql(
    `SELECT chapter, verse, text, footnotes 
     FROM verses 
     WHERE book = ? AND chapter = ? AND language = ? 
     ORDER BY verse ASC;`,
    [bookId, chapter, language],
  );

  // Parse footnotes back to TranslationRow array
  return result.rows._array.map((row) => {
    const r = row as Record<string, unknown>;
    return {
      chapter: Number(r.chapter ?? 0),
      verse: Number(r.verse ?? 0),
      text: String(r.text ?? ""),
      footnotes: r.footnotes ? JSON.parse(String(r.footnotes)) : undefined,
    } as TranslationRow;
  });
};

export const fetchLexiconEntry = async (strong: string) => {
  const result = await executeSql(
    `SELECT * FROM lexicon WHERE strong = ? LIMIT 1;`,
    [strong],
  );

  const row = result.rows._array[0] as Record<string, unknown> | undefined;
  if (!row) return null;

  return {
    ...row,
    definitions: row.definitions ? JSON.parse(String(row.definitions)) : [],
    occurrences: row.occurrences ? JSON.parse(String(row.occurrences)) : [],
  };
};
