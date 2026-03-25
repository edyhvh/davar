import { createHash } from "crypto";
import { mkdir, readdir, readFile, rm, writeFile } from "fs/promises";
import { extname, join } from "path";
import {
  BUNDLE_VERSIONS,
  CANONICAL_BOOK_ORDER,
  DATA_ROOT,
  DELITZSCH_TO_ENGLISH,
  OE_TO_ENGLISH,
  WEB_PUBLIC_DATA_ROOT,
} from "./config";

type JsonValue =
  | null
  | boolean
  | number
  | string
  | JsonValue[]
  | { [k: string]: JsonValue };

type BookMetadata = {
  id: string;
  name: string;
  section: "torah" | "neviim" | "ketuvim" | "besorah";
  chapters: number;
  order: number;
  hebrew_name: string;
  hebrew_transliteration: string;
  spanish_name: string;
};

type CanonicalBookLabels = {
  hebrew_name: string;
  hebrew_transliteration: string;
  spanish_name: string;
};

const readJson = async <T>(path: string): Promise<T> => {
  const raw = await readFile(path, "utf-8");
  return JSON.parse(raw) as T;
};

const loadCanonicalBookLabels = async (): Promise<Record<string, CanonicalBookLabels>> => {
  const sourcePath = join(DATA_ROOT, "..", "scripts", "bes", "config.py");
  const source = await readFile(sourcePath, "utf-8");

  const mapping: Record<string, CanonicalBookLabels> = {};

  // Parse the mirrored backend BOOK_METADATA entries from scripts/bes/config.py.
  const entryPattern = /"([^"]+)":\s*\{[^}]*"hebrew_name":\s*"([^"]+)",\s*"hebrew_transliteration":\s*"([^"]+)",\s*"spanish_name":\s*"([^"]+)"[^}]*\}/g;

  for (const match of source.matchAll(entryPattern)) {
    const [, bookName, hebrewName, hebrewTransliteration, spanishName] = match;
    mapping[bookName] = {
      hebrew_name: hebrewName,
      hebrew_transliteration: hebrewTransliteration,
      spanish_name: spanishName,
    };
  }

  return mapping;
};

const sha256OfJson = (value: JsonValue): string => {
  const payload = JSON.stringify(value);
  const hash = createHash("sha256").update(payload).digest("hex");
  return `sha256:${hash}`;
};

const listJsonFiles = async (dir: string): Promise<string[]> => {
  const entries = await readdir(dir, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile() && extname(entry.name) === ".json")
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b, "en"));
};

const asSection = (order: number): BookMetadata["section"] => {
  if (order <= 5) return "torah";
  if (order <= 26) return "neviim";
  if (order <= 39) return "ketuvim";
  return "besorah";
};

const toCanonicalBook = (name: string, source: "oe" | "delitzsch"): string => {
  const lower = name.toLowerCase();
  if (source === "oe") return OE_TO_ENGLISH[lower] ?? name;
  return DELITZSCH_TO_ENGLISH[lower] ?? name;
};

const hasCanonicalBook = (name: string, source: "oe" | "delitzsch"): boolean => {
  const lower = name.toLowerCase();
  if (source === "oe") return Boolean(OE_TO_ENGLISH[lower]);
  return Boolean(DELITZSCH_TO_ENGLISH[lower]);
};

const bookOrderMap = CANONICAL_BOOK_ORDER.reduce<Record<string, number>>(
  (acc, name, index) => {
    acc[name] = index + 1;
    return acc;
  },
  {},
);

const generateHebrewChapters = async (
  sourceDir: string,
  outDir: string,
  source: "oe" | "delitzsch",
): Promise<{ bundle: { books: Record<string, { chapters: Record<string, JsonValue> }> }; counts: Record<string, Record<string, number>> }> => {
  const folderNames = (await readdir(sourceDir, { withFileTypes: true }))
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b, "en"));

  const booksBundle: Record<string, { chapters: Record<string, JsonValue> }> = {};
  const verseCounts: Record<string, Record<string, number>> = {};

  for (const folderName of folderNames) {
    if (!hasCanonicalBook(folderName, source)) {
      continue;
    }

    const canonical = toCanonicalBook(folderName, source);
    const bookId = canonical.toLowerCase();
    const chapterFiles = await listJsonFiles(join(sourceDir, folderName));

    const chapters: Record<string, JsonValue> = {};
    const chapterVerseCounts: Record<string, number> = {};

    for (const chapterFile of chapterFiles) {
      const chapterNum = chapterFile.replace(/\.json$/i, "");
      const inputPath = join(sourceDir, folderName, chapterFile);
      const data = await readJson<JsonValue>(inputPath);

      // Delitzsch parsed chapters are wrapped in an array with {chapter, verses}.
      const normalized =
        source === "delitzsch" && Array.isArray(data)
          ? (data as Array<{ verses?: JsonValue[] }>)[0]?.verses ?? []
          : data;

      chapters[chapterNum] = normalized;

      const versesLength = Array.isArray(normalized) ? normalized.length : 0;
      chapterVerseCounts[chapterNum] = versesLength;

      await mkdir(join(outDir, bookId), { recursive: true });
      await writeFile(
        join(outDir, bookId, `${chapterNum}.json`),
        JSON.stringify(normalized),
        "utf-8",
      );
    }

    booksBundle[bookId] = { chapters };
    verseCounts[canonical] = chapterVerseCounts;
  }

  return {
    bundle: { books: booksBundle },
    counts: verseCounts,
  };
};

const generateDictionary = async (): Promise<{
  dictionaryBundle: JsonValue;
  prefixesById: JsonValue;
}> => {
  const customDefinitions = await readJson<JsonValue>(
    join(DATA_ROOT, "dict", "lexicon", "custom_definitions.json"),
  );
  const roots = await readJson<JsonValue>(
    join(DATA_ROOT, "dict", "lexicon", "roots.json"),
  );
  const words = await readJson<JsonValue>(
    join(DATA_ROOT, "dict", "lexicon", "words.json"),
  );

  const prefixEntriesDir = join(DATA_ROOT, "dict", "prefixes", "entries");
  const prefixFiles = await listJsonFiles(prefixEntriesDir);
  const prefixes: Record<string, JsonValue> = {};

  for (const file of prefixFiles) {
    const id = file.replace(/\.json$/i, "");
    prefixes[id] = await readJson<JsonValue>(join(prefixEntriesDir, file));
  }

  const dictOutDir = join(WEB_PUBLIC_DATA_ROOT, "dict");
  await mkdir(dictOutDir, { recursive: true });
  await writeFile(
    join(dictOutDir, "custom_definitions.json"),
    JSON.stringify(customDefinitions),
    "utf-8",
  );
  await writeFile(join(dictOutDir, "roots.json"), JSON.stringify(roots), "utf-8");
  await writeFile(join(dictOutDir, "words.json"), JSON.stringify(words), "utf-8");

  const prefixesById = prefixes as JsonValue;
  await writeFile(
    join(WEB_PUBLIC_DATA_ROOT, "prefixes.json"),
    JSON.stringify(prefixesById),
    "utf-8",
  );

  return {
    dictionaryBundle: {
      custom_definitions: customDefinitions,
      roots,
      prefixes,
    },
    prefixesById,
  };
};

const copyFolderJsonFiles = async (sourceDir: string, outDir: string): Promise<{ books: Record<string, JsonValue> }> => {
  await mkdir(outDir, { recursive: true });
  const files = await listJsonFiles(sourceDir);
  const books: Record<string, JsonValue> = {};

  for (const file of files) {
    const data = await readJson<JsonValue>(join(sourceDir, file));
    const stem = file.replace(/\.json$/i, "");
    books[stem] = data;
    await writeFile(join(outDir, file), JSON.stringify(data), "utf-8");
  }

  return { books };
};

const generateMetadata = (
  tanajVerseCounts: Record<string, Record<string, number>>,
  besorahVerseCounts: Record<string, Record<string, number>>,
  bookLabels: Record<string, CanonicalBookLabels>,
): { books: BookMetadata[]; chapter_counts: Record<string, number[]>; verse_counts: Record<string, Record<string, number>> } => {
  const verseCounts = { ...tanajVerseCounts, ...besorahVerseCounts };

  const books = Object.keys(verseCounts)
    .map((bookName) => {
      const order = bookOrderMap[bookName] ?? 999;
      const chapterCount = Object.keys(verseCounts[bookName] ?? {}).length;
      const section = asSection(order);
      const id = bookName.toLowerCase();
      const canonicalLabels = bookLabels[bookName];

      return {
        id,
        name: bookName,
        section,
        chapters: chapterCount,
        order,
        hebrew_name: canonicalLabels?.hebrew_name ?? bookName,
        hebrew_transliteration: canonicalLabels?.hebrew_transliteration ?? bookName,
        spanish_name: canonicalLabels?.spanish_name ?? bookName,
      } satisfies BookMetadata;
    })
    .sort((a, b) => a.order - b.order);

  const chapterCounts: Record<string, number[]> = {};
  for (const [bookName, perChapter] of Object.entries(verseCounts)) {
    chapterCounts[bookName] = Object.keys(perChapter)
      .map((n) => Number(n))
      .sort((a, b) => a - b);
  }

  return {
    books,
    chapter_counts: chapterCounts,
    verse_counts: verseCounts,
  };
};

const getJsonSize = (value: JsonValue): number => Buffer.byteLength(JSON.stringify(value), "utf-8");

const main = async (): Promise<void> => {
  await rm(WEB_PUBLIC_DATA_ROOT, { recursive: true, force: true });
  await mkdir(WEB_PUBLIC_DATA_ROOT, { recursive: true });

  const tanaj = await generateHebrewChapters(
    join(DATA_ROOT, "oe"),
    join(WEB_PUBLIC_DATA_ROOT, "oe"),
    "oe",
  );

  const besorah = await generateHebrewChapters(
    join(DATA_ROOT, "delitzsch_parsed"),
    join(WEB_PUBLIC_DATA_ROOT, "besorah"),
    "delitzsch",
  );

  const tthBundle = await copyFolderJsonFiles(
    join(DATA_ROOT, "tth_2", "json"),
    join(WEB_PUBLIC_DATA_ROOT, "tth"),
  );

  const besBundle = await copyFolderJsonFiles(
    join(DATA_ROOT, "bes", "json"),
    join(WEB_PUBLIC_DATA_ROOT, "bes"),
  );

  const translitBundle = await copyFolderJsonFiles(
    join(DATA_ROOT, "translit"),
    join(WEB_PUBLIC_DATA_ROOT, "translit"),
  );

  const { dictionaryBundle } = await generateDictionary();

  const booksDir = join(DATA_ROOT, "dss", "books");
  const dssFiles = await listJsonFiles(booksDir);
  const dssBooks: Record<string, JsonValue> = {};
  await mkdir(join(WEB_PUBLIC_DATA_ROOT, "dss"), { recursive: true });
  for (const file of dssFiles) {
    const stem = file.replace(/\.json$/i, "");
    dssBooks[stem] = await readJson<JsonValue>(join(booksDir, file));
    await writeFile(
      join(WEB_PUBLIC_DATA_ROOT, "dss", file),
      JSON.stringify(dssBooks[stem]),
      "utf-8",
    );
  }
  const dssBundle = dssBooks as JsonValue;

  const canonicalBookLabels = await loadCanonicalBookLabels();
  const metadata = generateMetadata(tanaj.counts, besorah.counts, canonicalBookLabels);
  await writeFile(
    join(WEB_PUBLIC_DATA_ROOT, "metadata.json"),
    JSON.stringify(metadata),
    "utf-8",
  );

  const bundlesDir = join(WEB_PUBLIC_DATA_ROOT, "bundles");
  await mkdir(bundlesDir, { recursive: true });

  await writeFile(join(bundlesDir, "tanaj.json"), JSON.stringify(tanaj.bundle), "utf-8");
  await writeFile(
    join(bundlesDir, "besorah.json"),
    JSON.stringify(besorah.bundle),
    "utf-8",
  );
  await writeFile(join(bundlesDir, "tth.json"), JSON.stringify(tthBundle), "utf-8");
  await writeFile(
    join(bundlesDir, "dictionary.json"),
    JSON.stringify(dictionaryBundle),
    "utf-8",
  );
  await writeFile(join(bundlesDir, "dss.json"), JSON.stringify(dssBundle), "utf-8");
  await writeFile(
    join(bundlesDir, "versions.json"),
    JSON.stringify(BUNDLE_VERSIONS),
    "utf-8",
  );

  const manifest = {
    version: `${new Date().toISOString().slice(0, 10).replace(/-/g, ".")}-1`,
    generated_at: new Date().toISOString(),
    bundles: {
      metadata: {
        size: getJsonSize(metadata),
        checksum: sha256OfJson(metadata),
      },
      tanaj: {
        size: getJsonSize(tanaj.bundle),
        checksum: sha256OfJson(tanaj.bundle),
      },
      besorah: {
        size: getJsonSize(besorah.bundle),
        checksum: sha256OfJson(besorah.bundle),
      },
      tth: {
        size: getJsonSize(tthBundle as unknown as JsonValue),
        checksum: sha256OfJson(tthBundle as unknown as JsonValue),
      },
      bes: {
        size: getJsonSize(besBundle as unknown as JsonValue),
        checksum: sha256OfJson(besBundle as unknown as JsonValue),
      },
      translit: {
        size: getJsonSize(translitBundle as unknown as JsonValue),
        checksum: sha256OfJson(translitBundle as unknown as JsonValue),
      },
      dictionary: {
        size: getJsonSize(dictionaryBundle),
        checksum: sha256OfJson(dictionaryBundle),
      },
      dss: {
        size: getJsonSize(dssBundle),
        checksum: sha256OfJson(dssBundle),
      },
      versions: {
        size: getJsonSize(BUNDLE_VERSIONS as unknown as JsonValue),
        checksum: sha256OfJson(BUNDLE_VERSIONS as unknown as JsonValue),
      },
    },
  };

  await writeFile(
    join(WEB_PUBLIC_DATA_ROOT, "manifest.json"),
    JSON.stringify(manifest),
    "utf-8",
  );

  console.log("Generated static data in web/public/data");
  console.log(`books: tanaj=${Object.keys(tanaj.bundle.books).length}, besorah=${Object.keys(besorah.bundle.books).length}`);
  console.log(`bundles: ${Object.keys(manifest.bundles).join(", ")}`);
};

main().catch((error) => {
  console.error("generate-static-data failed", error);
  process.exit(1);
});
