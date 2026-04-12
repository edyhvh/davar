import { createClient } from "@supabase/supabase-js";

// Direct import.meta.env property access is required so Bun can statically
// inline PUBLIC_* values into the browser bundle at build time. Indirect
// access via a variable reference is NOT replaced by the bundler.
const PLACEHOLDER_SUPABASE_URL = "your-project-ref.supabase.co";
const PLACEHOLDER_SUPABASE_KEY = "your-supabase-anon-key";

const TS2009_BOOK_FILE_MAP: Record<string, string> = {
	genesis: "bereshit",
	exodus: "shemoth",
	leviticus: "wayyiqra",
	numbers: "bemidbar",
	deuteronomy: "debarim",
	joshua: "yehoshua",
	judges: "shophetim",
	samuel1: "samuel_1",
	samuel2: "samuel_2",
	kings1: "kings_1",
	kings2: "kings_2",
	chronicles1: "chronicles_1",
	chronicles2: "chronicles_2",
	nehemiah: "nehemyah",
	esther: "ester",
	job: "iyob",
	psalms: "tehillim",
	ecclesiastes: "qoheleth",
	songofsolomon: "shir_hashirim",
	isaiah: "yeshayahu",
	jeremiah: "yirmeyahu",
	lamentations: "ekah",
	ezekiel: "yehezqel",
	obadiah: "obadyah",
	jonah: "yonah",
	ruth: "ruth",
	ezra: "ezra",
	proverbs: "mishlei",
	daniel: "daniel",
	hosea: "hosea",
	joel: "yoel",
	amos: "amos",
	micah: "micah",
	nahum: "nahum",
	habakkuk: "habakkuk",
	zephaniah: "zephaniah",
	haggai: "haggai",
	zechariah: "zechariah",
	malachi: "malachi",
	matthew: "mattithyahu",
	mark: "marqos",
	luke: "lugqas",
	john: "yohanan",
	acts: "maasei",
	romans: "romiyim",
	corinthians1: "corinthians_1",
	corinthians2: "corinthians_2",
	galatians: "galatiyim",
	ephesians: "ephsiyim",
	philippians: "pilipiyim",
	colossians: "qolasim",
	thessalonians1: "thessalonians_1",
	thessalonians2: "thessalonians_2",
	timothy1: "timothy_1",
	timothy2: "timothy_2",
	titus: "titos",
	philemon: "pileymon",
	hebrews: "ibrim",
	james: "yaaqob",
	peter1: "peter_1",
	peter2: "peter_2",
	john1: "john_1",
	john2: "john_2",
	john3: "john_3",
	jude: "yehudah",
	revelation: "hazon",
};

const TS2009_LEGACY_BOOK_FILE_MAP: Record<string, string> = {
	genesis: "bereshit_genesis",
	exodus: "shemoth_exodus",
	leviticus: "wayyiqra_leviticus",
	numbers: "bemidbar_numbers",
	deuteronomy: "debarim_deuteronomy",
	joshua: "yehoshua_joshua",
	judges: "shophetim_judges",
	ruth: "ruth",
	samuel1: "shemuel_aleph_1_samuel",
	samuel2: "shemuel_bet_2_samuel",
	kings1: "melakim_aleph_1_kings",
	kings2: "melakim_bet_2_kings",
	chronicles1: "dibre_hayamim_aleph_1_chronicles",
	chronicles2: "dibre_hayamim_bet_2_chronicles",
	ezra: "ezra",
	nehemiah: "nehemyah_nehemiah",
	esther: "ester_esther",
	job: "iyob_job",
	psalms: "tehillim_psalms",
	proverbs: "mishle_proverbs",
	ecclesiastes: "qoheleth_ecclesiastes",
	songofsolomon: "shir_hashirim_song_of_songs",
	isaiah: "yeshayahu_isaiah",
	jeremiah: "yirmeyahu_jeremiah",
	lamentations: "ekah_lamentations",
	ezekiel: "yehezqel_ezekiel",
	daniel: "daniel_daniel",
	hosea: "hoshea_hosea",
	joel: "yoel_joel",
	amos: "amos",
	obadiah: "obadyah_obadiah",
	jonah: "yonah_jonah",
	micah: "mikah_micah",
	nahum: "nahum_nahum",
	habakkuk: "habaqqugq_habakkuk",
	zephaniah: "tsephanyah_zephaniah",
	haggai: "haggai_haggai",
	zechariah: "zekaryah_zechariah",
	malachi: "malaki_malachi",
};

type Ts2009VersePayload = {
	translation?: unknown;
	text?: unknown;
};

type Ts2009BookVerse = {
	number?: number;
	verse?: number;
	translation?: unknown;
	text?: unknown;
};

type Ts2009BookPayload = {
	chapters?: unknown;
};

const supabaseUrl = import.meta.env.PUBLIC_SUPABASE_URL ?? "";
const supabaseAnonKey = import.meta.env.PUBLIC_SUPABASE_ANON_KEY ?? "";

let supabase: ReturnType<typeof createClient> | null = null;
let hasWarnedNetworkFailure = false;
let hasWarnedStorageMismatch = false;

const chapterBookCache = new Map<string, Promise<Map<number, string> | null>>();

const looksLikePlaceholder = (value: string): boolean => {
	const normalized = value.toLowerCase();
	return (
		normalized.includes(PLACEHOLDER_SUPABASE_URL) ||
		normalized.includes(PLACEHOLDER_SUPABASE_KEY)
	);
};

const warnNetworkFailureOnce = (error: unknown) => {
	if (hasWarnedNetworkFailure) return;
	hasWarnedNetworkFailure = true;
	console.warn(
		"TS2009 network unavailable; using fallback translation sources.",
		error,
	);
};

const warnStorageMismatchOnce = (errorMessage: string, path: string) => {
	if (hasWarnedStorageMismatch) return;
	hasWarnedStorageMismatch = true;
	console.warn(
		`TS2009 storage path mismatch for ${path}: ${errorMessage}. Falling back to per-book format.`,
	);
};

const isNetworkErrorMessage = (message: string): boolean =>
	message.includes("network request failed");

const isNotFoundLikeMessage = (message: string): boolean =>
	message.includes("not found") ||
	message.includes("404") ||
	message.includes("object") ||
	message.includes("resource") ||
	message.includes("does not exist");

const parseVerseText = (payload: Ts2009VersePayload): string | null => {
	if (typeof payload.translation === "string") return payload.translation;
	if (typeof payload.text === "string") return payload.text;
	return null;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
	typeof value === "object" && value !== null;

const extractChapterVerseEntries = (
	chaptersRaw: unknown,
	chapter: number,
): Ts2009BookVerse[] | null => {
	if (Array.isArray(chaptersRaw)) {
		if (chaptersRaw.length === 0) return null;

		const chapterAtIndex = chaptersRaw[chapter - 1];
		if (Array.isArray(chapterAtIndex)) {
			return chapterAtIndex as Ts2009BookVerse[];
		}

		const chapterObjectMatch = chaptersRaw.find((entry) => {
			if (!isRecord(entry)) return false;
			const chapterNumber = Number(entry.number ?? entry.chapter ?? NaN);
			return Number.isFinite(chapterNumber) && chapterNumber === chapter;
		});

		if (
			isRecord(chapterObjectMatch) &&
			Array.isArray(chapterObjectMatch.verses)
		) {
			return chapterObjectMatch.verses as Ts2009BookVerse[];
		}

		return null;
	}

	if (!isRecord(chaptersRaw)) return null;

	const keyedChapter = chaptersRaw[String(chapter)];
	if (Array.isArray(keyedChapter)) {
		return keyedChapter as Ts2009BookVerse[];
	}

	if (isRecord(keyedChapter) && Array.isArray(keyedChapter.verses)) {
		return keyedChapter.verses as Ts2009BookVerse[];
	}

	if (isRecord(keyedChapter)) {
		return Object.values(keyedChapter) as Ts2009BookVerse[];
	}

	return null;
};

const getBookFileCandidates = (bookId: string): string[] => {
	const normalized = bookId.toLowerCase();
	const mapped = TS2009_BOOK_FILE_MAP[normalized];
	const legacyMapped = TS2009_LEGACY_BOOK_FILE_MAP[normalized];
	const underscoreVariant = normalized.replace(/(\D)(\d+)$/, "$1_$2");
	const stems = [mapped, legacyMapped, normalized, underscoreVariant].filter(
		(value): value is string => Boolean(value),
	);

	const paths: string[] = [];
	for (const stem of stems) {
		paths.push(`${stem}.json`);
		paths.push(`ts2009/${stem}.json`);
	}

	return [...new Set(paths)];
};

const loadChapterFromBookFile = async (
	bookId: string,
	chapter: number,
): Promise<Map<number, string> | null> => {
	if (!supabase) return null;

	const cacheKey = `${bookId.toLowerCase()}:${chapter}`;
	if (chapterBookCache.has(cacheKey)) {
		return chapterBookCache.get(cacheKey) as Promise<Map<
			number,
			string
		> | null>;
	}

	const loader = (async () => {
		const candidates = getBookFileCandidates(bookId);

		for (const candidate of candidates) {
			const { data, error } = await supabase.storage
				.from("ts2009")
				.download(candidate);

			if (error || !data) continue;

			try {
				const parsed = JSON.parse(await data.text()) as Ts2009BookPayload;
				const chapterVerses = extractChapterVerseEntries(
					parsed.chapters,
					chapter,
				);

				if (!chapterVerses || chapterVerses.length === 0) continue;

				const verseMap = new Map<number, string>();
				for (const [index, verseEntry] of chapterVerses.entries()) {
					const verseNumber = Number(
						verseEntry.number ?? verseEntry.verse ?? index + 1,
					);
					if (!Number.isFinite(verseNumber)) continue;

					const text = parseVerseText(verseEntry);
					if (text) verseMap.set(verseNumber, text);
				}

				return verseMap;
			} catch {
				// Keep probing candidate filenames.
			}
		}

		return null;
	})();

	chapterBookCache.set(cacheKey, loader);
	return loader;
};

if (supabaseUrl && supabaseAnonKey) {
	try {
		if (
			looksLikePlaceholder(supabaseUrl) ||
			looksLikePlaceholder(supabaseAnonKey)
		) {
			throw new Error("placeholder Supabase credentials");
		}
		new URL(supabaseUrl);
		supabase = createClient(supabaseUrl, supabaseAnonKey);
	} catch {
		console.warn(
			"Skipping Supabase initialization: PUBLIC_SUPABASE_URL/PUBLIC_SUPABASE_ANON_KEY are missing, invalid, or placeholder values",
		);
	}
} else {
	console.warn(
		"Skipping Supabase initialization: missing PUBLIC_SUPABASE_URL or PUBLIC_SUPABASE_ANON_KEY",
	);
}

export { supabase };

export const fetchTs2009Translation = async (
	book: string,
	chapter: number,
	verse: number,
): Promise<string | null> => {
	if (!supabase) {
		return null;
	}

	const perVersePath = `${book}/${chapter}/${verse}.json`;

	try {
		const { data, error } = await supabase.storage
			.from("ts2009")
			.download(perVersePath);

		if (!error && data) {
			const json = JSON.parse(await data.text()) as Ts2009VersePayload;
			return parseVerseText(json);
		}

		const message = error?.message?.toLowerCase() ?? "";
		if (isNetworkErrorMessage(message)) {
			warnNetworkFailureOnce(error);
			return null;
		}

		if (message.length > 0 && isNotFoundLikeMessage(message)) {
			const chapterTranslations = await loadChapterFromBookFile(book, chapter);
			const fallbackTranslation = chapterTranslations?.get(verse) ?? null;

			if (fallbackTranslation) {
				return fallbackTranslation;
			}

			warnStorageMismatchOnce(message, perVersePath);
			return null;
		}

		return null;
	} catch (error) {
		const message = error instanceof Error ? error.message.toLowerCase() : "";
		if (isNetworkErrorMessage(message)) {
			warnNetworkFailureOnce(error);
			return null;
		}

		const chapterTranslations = await loadChapterFromBookFile(book, chapter);
		if (chapterTranslations) {
			return chapterTranslations.get(verse) ?? null;
		}

		console.warn(
			`Failed to fetch TS2009 for ${book} ${chapter}:${verse}:`,
			error,
		);
		return null;
	}
};
