import * as SQLite from "expo-sqlite";
import type { LexiconResponse } from "@/src/types/api";

export type TranslationRow = {
  chapter: number;
  verse: number;
  text: string;
  footnotes?: unknown[];
};

const db = SQLite.openDatabase("davar.db");

// ── Custom error for better debugging ──────────────────────────────────────

class DatabaseError extends Error {
  constructor(
    message: string,
    public query: string,
    public params: (string | number | null)[],
    public originalError: any,
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
      original: this.originalError?.message || String(this.originalError),
    };
  }
}

// ── Low-level executor with error context ──────────────────────────────────

const executeSql = (
  query: string,
  params: (string | number | null)[] = [],
): Promise<SQLite.SQLResultSet> =>
  new Promise((resolve, reject) => {
    db.transaction(
      (tx) => {
        tx.executeSql(
          query,
          params,
          (_, result) => resolve(result),
          (_, error) => {
            const wrappedError = new DatabaseError(
              `SQLite execution failed`,
              query,
              params,
              error,
            );
            reject(wrappedError);
            return false;
          },
        );
      },
      (error) => {
        // Transaction-level failure
        reject(
          new DatabaseError(`SQLite transaction failed`, query, params, error),
        );
      },
    );
  });

// ── Initialization ──────────────────────────────────────────────────────────

export const initializeDatabase = async () => {
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

  await executeSql(
    `CREATE TABLE IF NOT EXISTS lexicon (
      strong TEXT PRIMARY KEY,
      hebrew TEXT,
      transliteration TEXT,
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
};

// ── Bulk inserts with transaction safety ───────────────────────────────────

export const insertLexiconEntries = async (entries: LexiconResponse[]) => {
  await executeSql("BEGIN TRANSACTION;");

  try {
    for (const entry of entries) {
      await executeSql(
        `INSERT OR REPLACE INTO lexicon (
          strong, hebrew, transliteration, definitions, root, root_strong, occurrences
        ) VALUES (?, ?, ?, ?, ?, ?, ?);`,
        [
          entry.strong_number,
          entry.hebrew ?? null,
          entry.transliteration ?? null,
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
  await executeSql(
    "DELETE FROM verses WHERE book = ? AND language = ?;",
    [bookId, language],
  );
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

  // Parse footnotes back to array
  return result.rows._array.map((row: any) => ({
    ...row,
    footnotes: row.footnotes ? JSON.parse(row.footnotes) : undefined,
  }));
};

export const fetchLexiconEntry = async (strong: string) => {
  const result = await executeSql(
    `SELECT * FROM lexicon WHERE strong = ? LIMIT 1;`,
    [strong],
  );

  const row = result.rows._array[0];
  if (!row) return null;

  return {
    ...row,
    definitions: row.definitions ? JSON.parse(row.definitions) : [],
    occurrences: row.occurrences ? JSON.parse(row.occurrences) : [],
  };
};
