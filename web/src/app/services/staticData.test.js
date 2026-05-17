import { describe, expect, test } from "bun:test";
import {
	resolveTranslationLookupKey,
	resolveTranslationTarget,
} from "../../../../shared/translationConfig";

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

		const verse = chapter.find(
			(item) => item.chapter === 1 && item.verse === 2,
		);
		expect(verse).toBeDefined();

		const verseWord = verse.words.find((word) => word.strong === "H7363");
		expect(verseWord).toBeDefined();
		expect(verseWord.translit_en).toBeUndefined();
		expect(verseWord.translit_es).toBeUndefined();

		const translitVerse = translit.verses.find(
			(item) => item.chapter === 1 && item.verse === 2,
		);
		expect(translitVerse).toBeDefined();

		const translitWord = translitVerse.words.find(
			(word) => word.strong === "H7363",
		);
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

	test("Spanish Psalms superscriptions use chapter titles and keep later verses aligned", async () => {
		const psalms = await readJson("data/bes/psalms.json");
		const chapter = psalms.chapters.find((item) => item.chapter === 3);

		expect(chapter).toBeDefined();
		expect(typeof chapter.title).toBe("string");
		expect(chapter.title.length > 0).toBe(true);

		const verse1Target = resolveTranslationTarget("psalms", 3, 1, {
			language: "es",
		});
		expect(verse1Target.usesPsalmTitle).toBe(true);
		expect(verse1Target.reference).toBeNull();

		const displayedVerse1 = verse1Target.usesPsalmTitle
			? chapter.title
			: chapter.verses.find(
				(item) =>
					item.verse === verse1Target.reference?.verse,
			)?.bes;
		expect(displayedVerse1).toBe(chapter.title);

		const verse2Target = resolveTranslationTarget("psalms", 3, 2, {
			language: "es",
		});
		expect(verse2Target.usesPsalmTitle).toBe(false);
		expect(verse2Target.reference).toEqual({ chapter: 3, verse: 1 });

		const displayedVerse2 = chapter.verses.find(
			(item) => item.verse === verse2Target.reference?.verse,
		)?.bes;
		expect(displayedVerse2).toBe(chapter.verses.find((item) => item.verse === 1)?.bes);
	});

	test("English and Spanish both honor versification shifts", () => {
		expect(
			resolveTranslationLookupKey("psalms", 3, 1, { language: "en" }),
		).toBeNull();
		expect(
			resolveTranslationLookupKey("psalms", 3, 2, { language: "en" }),
		).toBe("3-1");
		expect(
			resolveTranslationLookupKey("exodus", 7, 26, { language: "es" }),
		).toBe("8-1");
		expect(
			resolveTranslationLookupKey("exodus", 7, 26, { language: "en" }),
		).toBe("8-1");
		expect(
			resolveTranslationLookupKey("hosea", 2, 25, { language: "es" }),
		).toBe("2-23");
	});
});

const runSupabaseConnectivity = Bun.env.RUN_SUPABASE_CONNECTIVITY_TEST === "1";

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
