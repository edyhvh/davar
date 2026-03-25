import { describe, expect, test } from "bun:test";

const readJson = async (relativePath) => {
  const filePath = new URL(`../../../public/${relativePath}`, import.meta.url);
  const file = Bun.file(filePath);
  return file.json();
};

describe("static data integrity", () => {
  test("core metadata has books and chapter map", async () => {
    const metadata = await readJson("data/metadata.json");

    expect(Array.isArray(metadata.books)).toBe(true);
    expect(metadata.books.length > 0).toBe(true);
    expect(typeof metadata.verse_counts).toBe("object");
    expect(metadata.verse_counts).not.toBeNull();
    expect(metadata.verse_counts.Genesis?.["1"] > 0).toBe(true);
  });

  test("versions bundle is available", async () => {
    const versions = await readJson("data/bundles/versions.json");

    expect(typeof versions).toBe("object");
    expect(versions).not.toBeNull();
    expect(typeof versions.tanaj).toBe("number");
    expect(typeof versions.dictionary).toBe("number");
  });

  test("chapter content exists for Torah and Besorah samples", async () => {
    const genesisChapter = await readJson("data/oe/genesis/1.json");
    const matthewChapter = await readJson("data/besorah/matthew/1.json");

    expect(Array.isArray(genesisChapter)).toBe(true);
    expect(genesisChapter.length > 0).toBe(true);
    expect(Array.isArray(matthewChapter)).toBe(true);
    expect(matthewChapter.length > 0).toBe(true);
  });

  test("dictionary assets are available", async () => {
    const words = await readJson("data/dict/words.json");
    const roots = await readJson("data/dict/roots.json");

    expect(typeof words).toBe("object");
    expect(words).not.toBeNull();
    expect(Object.keys(words).length > 0).toBe(true);
    expect(typeof roots).toBe("object");
    expect(roots).not.toBeNull();
    expect(Object.keys(roots).length > 0).toBe(true);
  });

  test("Genesis 1:2 keeps H7363 transliteration in translit dataset", async () => {
    const chapter = await readJson("data/oe/genesis/1.json");
    const translit = await readJson("data/translit/genesis.json");

    const verse = chapter.find((item) => item.chapter === 1 && item.verse === 2);
    expect(verse).toBeDefined();

    const verseWord = verse.words.find((word) => word.strong === "H7363");
    expect(verseWord).toBeDefined();
    expect(verseWord.translit_en).toBeUndefined();
    expect(verseWord.translit_es).toBeUndefined();

    const translitVerse = translit.verses.find(
      (item) => item.chapter === 1 && item.verse === 2,
    );
    expect(translitVerse).toBeDefined();

    const translitWord = translitVerse.words.find((word) => word.strong === "H7363");
    expect(translitWord).toBeDefined();
    expect(translitWord.translit_en).toBe("merachefet");
    expect(translitWord.translit_es).toBe("merajefet");
  });

  test("H7363 currently exists in roots and not words", async () => {
    const words = await readJson("data/dict/words.json");
    const roots = await readJson("data/dict/roots.json");

    expect(words.H7363).toBeUndefined();
    expect(roots.H7363).toBeDefined();
  });
});

const runSupabaseConnectivity =
  Bun.env.RUN_SUPABASE_CONNECTIVITY_TEST === "1";

describe.if(runSupabaseConnectivity)("supabase connectivity", () => {
  test("auth settings endpoint is reachable with anon key", async () => {
    const baseUrl = Bun.env.PUBLIC_SUPABASE_URL;
    const anonKey = Bun.env.PUBLIC_SUPABASE_ANON_KEY;

    if (!baseUrl || !anonKey) {
      throw new Error(
        "PUBLIC_SUPABASE_URL and PUBLIC_SUPABASE_ANON_KEY are required when RUN_SUPABASE_CONNECTIVITY_TEST=1",
      );
    }

    const response = await fetch(`${baseUrl}/auth/v1/settings`, {
      headers: {
        apikey: anonKey,
      },
    });

    expect(response.ok).toBe(true);
    const payload = await response.json();
    expect(typeof payload).toBe("object");
    expect(payload).not.toBeNull();
  });
});
