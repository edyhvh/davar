import { TTH_BOOK_MAPPING } from "@davar/shared/translationConfig";
import { fetchTs2009Translation } from "./supabaseClient";

export interface WordResponse {
	position: number;
	text: string;
	strong?: string;
	morph?: string;
	prefixes: string[];
	has_dss_variant: boolean;
	translit_en?: string;
	translit_es?: string;
}

export interface DssVariant {
	position: number;
	dss_word: string;
	masoretic_word: string;
	comment_v2_en?: string;
	comment_v2_es?: string;
	comment_v2_he?: string;
	masoretic_strong?: string;
	dss_strong?: string;
}

export interface TranslationFootnote {
	marker: string;
	number: string;
	word: string;
	explanation: string;
}

export interface VerseResponse {
	chapter: number;
	verse: number;
	hebrew: string;
	words: WordResponse[];
	translation?: string;
	translation_language?: string;
	translation_footnotes?: TranslationFootnote[];
	dss?: DssVariant[];
}

export interface BookResponse {
	id: string;
	name: string;
	section: "torah" | "neviim" | "ketuvim" | "besorah";
	chapters: number;
	order: number;
	hebrew_name: string;
	hebrew_transliteration: string;
	spanish_name: string;
}

type MetadataPayload = {
	books: BookResponse[];
	verse_counts?: Record<string, Record<string, number>>;
};

type RawWord = {
	text: string;
	strong?: string;
	morph?: string;
	prefixes?: string[];
	translit_en?: string;
	translit_es?: string;
};

type RawVerse = {
	chapter: number;
	verse: number;
	hebrew: string;
	words?: RawWord[];
};

type RawTranslationFootnote = {
	marker?: string;
	number?: string;
	word?: string;
	explanation?: string;
};

type RawTranslationVerse = {
	verse: number;
	bes?: string;
	tth?: string;
	footnotes?: RawTranslationFootnote[];
};

type RawTranslationBook = {
	book_info?: {
		hebrew_name?: string;
		spanish_name?: string;
	};
	chapters?: Array<{
		chapter: number;
		verses: RawTranslationVerse[];
	}>;
};

type RawDssDifference = {
	position?: number;
	dss_word?: string;
	masoretic_word?: string;
	commentary?: string;
	comment_v2_en?: string;
	comment_v2_es?: string;
	comment_v2_he?: string;
	masoretic_strong?: string;
	dss_strong?: string;
};

type RawDssVerse = {
	differences?: RawDssDifference[];
};

type RawDssBook = {
	chapters?: Record<
		string,
		{
			verses?: Record<string, RawDssVerse>;
		}
	>;
};

type RawTranslitWord = {
	text?: string;
	strong?: string;
	translit_en?: string;
	translit_es?: string;
};

type RawTranslitBook = {
	verses?: Array<{
		chapter: number;
		verse: number;
		words?: RawTranslitWord[];
	}>;
};

const MAX_CACHE_SIZE = 100;
const jsonCache = new Map<string, Promise<unknown>>();

// In-memory cache for TS2009 translations to avoid N+1 query problem
// Keys: `${bookId}:${chapter}:${verse}`, Values: string | null
const ts2009Cache = new Map<string, string | null>();
const ts2009ChapterCache = new Map<
	string,
	Promise<Map<number, string> | null>
>();

type StaticBase = "" | "/public" | "/web" | "/web/public";

const staticUrlPrefix = (
	(
		import.meta as ImportMeta & {
			env?: Record<string, string | undefined>;
		}
	).env?.PUBLIC_STATIC_URL ?? ""
).replace(/\/+$/, "");

let preferredStaticBase: StaticBase = "";
const STATIC_BASE_CANDIDATES: StaticBase[] = [
	"",
	"/public",
	"/web",
	"/web/public",
];

const normalizeStaticPath = (path: string): string =>
	path.startsWith("/") ? path : `/${path}`;

const buildCandidatePaths = (path: string): string[] => {
	const normalizedPath = normalizeStaticPath(path);
	const orderedBases = [
		preferredStaticBase,
		...STATIC_BASE_CANDIDATES.filter((base) => base !== preferredStaticBase),
	];
	const localPaths = orderedBases.map((base) => `${base}${normalizedPath}`);

	if (!staticUrlPrefix) {
		return localPaths;
	}

	const prefixedPaths = localPaths.map((candidatePath) =>
		`${staticUrlPrefix}${candidatePath}`,
	);

	return [...new Set([...prefixedPaths, ...localPaths])];
};

const inferStaticBaseFromResolvedPath = (
	resolvedPath: string,
	originalPath: string,
): StaticBase => {
	const normalizedPath = normalizeStaticPath(originalPath);

	if (!resolvedPath.endsWith(normalizedPath)) {
		return "";
	}

	const base = resolvedPath.slice(
		0,
		resolvedPath.length - normalizedPath.length,
	);
	if (
		base === "" ||
		base === "/public" ||
		base === "/web" ||
		base === "/web/public"
	) {
		return base;
	}

	return "";
};

const parseStaticJson = async <T>(
	response: Response,
	resolvedPath: string,
): Promise<T> => {
	if (!response.ok) {
		throw new Error(
			`Failed to load static data: ${resolvedPath} (status ${response.status})`,
		);
	}

	const contentType = response.headers.get("content-type") || "";
	const payload = await response.text();
	const normalizedPayload = payload.trimStart().toLowerCase();
	const looksLikeHtml =
		normalizedPayload.startsWith("<!doctype") ||
		normalizedPayload.startsWith("<html");

	if (looksLikeHtml) {
		throw new Error(
			`Static data endpoint returned HTML instead of JSON: ${resolvedPath}`,
		);
	}

	try {
		return JSON.parse(payload) as T;
	} catch {
		const contentTypeLabel = contentType || "unknown";
		throw new Error(
			`Invalid JSON for static data: ${resolvedPath} (content-type: ${contentTypeLabel})`,
		);
	}
};

const fetchJson = async <T>(path: string): Promise<T> => {
	// If already cached, move to end (mark as recently used)
	if (jsonCache.has(path)) {
		// biome-ignore lint/style/noNonNullAssertion: safe — guarded by .has() check above
		const promise = jsonCache.get(path)!;
		jsonCache.delete(path);
		jsonCache.set(path, promise);
		return promise as Promise<T>;
	}

	const promise = (async () => {
		const errors: string[] = [];

		for (const resolvedPath of buildCandidatePaths(path)) {
			try {
				const response = await fetch(resolvedPath, { cache: "no-cache" });
				const parsed = await parseStaticJson<T>(response, resolvedPath);
				preferredStaticBase = inferStaticBaseFromResolvedPath(
					resolvedPath,
					path,
				);
				return parsed;
			} catch (error) {
				const message = error instanceof Error ? error.message : String(error);
				errors.push(message);
			}
		}

		throw new Error(
			`Failed to load static data from all candidates for ${normalizeStaticPath(path)}: ${errors.join(" | ")}. Verify the web app is launched from the web/ directory (bun run dev) or served from a build that includes copied public data.`,
		);
	})().catch((error) => {
		jsonCache.delete(path); // Remove failed entry to allow retry
		throw error;
	});

	// Evict oldest if at capacity
	if (jsonCache.size >= MAX_CACHE_SIZE) {
		const firstKey = jsonCache.keys().next().value;
		if (firstKey !== undefined) {
			jsonCache.delete(firstKey);
		}
	}

	jsonCache.set(path, promise);
	return promise as Promise<T>;
};

let metadataPromise: Promise<MetadataPayload> | null = null;
let booksPromise: Promise<BookResponse[]> | null = null;

/**
 * Fetches TS2009 translation with client-side caching to avoid repeated Supabase requests.
 * Uses in-memory cache with keys formatted as `${bookId}:${chapter}:${verse}`.
 */
const fetchCachedTs2009Translation = async (
	bookId: string,
	chapter: number,
	verse: number,
): Promise<string | null> => {
	const cacheKey = `${bookId}:${chapter}:${verse}`;

	// Return cached value if available
	if (ts2009Cache.has(cacheKey)) {
		// biome-ignore lint/style/noNonNullAssertion: safe — guarded by .has() check above
		return ts2009Cache.get(cacheKey)!;
	}

	const chapterKey = `${bookId}:${chapter}`;

	let chapterPromise = ts2009ChapterCache.get(chapterKey);
	if (!chapterPromise) {
		chapterPromise = (async () => {
			try {
				const staticChapter = await fetchJson<{
					verses?: Record<string, string>;
				}>(`/data/ts2009/${bookId}/${chapter}.json`);

				const verses = staticChapter.verses ?? {};
				const verseMap = new Map<number, string>();
				for (const [verseKey, translation] of Object.entries(verses)) {
					const verseNumber = Number(verseKey);
					if (
						!Number.isFinite(verseNumber) ||
						typeof translation !== "string"
					) {
						continue;
					}
					verseMap.set(verseNumber, translation);
				}

				return verseMap;
			} catch {
				return null;
			}
		})();

		ts2009ChapterCache.set(chapterKey, chapterPromise);
	}

	const staticChapterTranslations = await chapterPromise;
	const staticTranslation = staticChapterTranslations?.get(verse) ?? null;
	if (staticTranslation) {
		ts2009Cache.set(cacheKey, staticTranslation);
		return staticTranslation;
	}

	// Fall back to Supabase if static TS2009 chapter data is unavailable.
	const translation = await fetchTs2009Translation(bookId, chapter, verse);
	ts2009Cache.set(cacheKey, translation);
	return translation;
};

export const loadMetadata = async (): Promise<MetadataPayload> => {
	if (!metadataPromise) {
		metadataPromise = fetchJson<MetadataPayload>("/data/metadata.json").catch(
			(error) => {
				metadataPromise = null;
				throw error;
			},
		);
	}
	return metadataPromise;
};

const normalizeBookToken = (value: string): string =>
	value.toLowerCase().replace(/[^a-z0-9]/g, "");

const findBook = (
	books: BookResponse[],
	bookName: string,
): BookResponse | undefined => {
	const target = normalizeBookToken(bookName);
	return books.find((book) => {
		const candidates = [
			book.id,
			book.name,
			book.hebrew_name,
			book.hebrew_transliteration,
			book.spanish_name,
		];

		return candidates.some(
			(candidate) => normalizeBookToken(candidate) === target,
		);
	});
};

const toDssBookKey = (bookId: string): string => {
	const dssMap: Record<string, string> = {
		samuel1: "1samuel",
		samuel2: "2samuel",
		songofsolomon: "songs",
		hosea: "hoseah",
	};

	return dssMap[bookId] ?? bookId;
};

const HEBREW_MARKS_RE = /[\u0591-\u05C7]/g;

const normalizeSurfaceWord = (value?: string): string =>
	(value ?? "").replaceAll("/", "").replace(HEBREW_MARKS_RE, "");

const extractBaseStrong = (value?: string): string | undefined => {
	if (!value) return undefined;

	const parts = value
		.toUpperCase()
		.replace(/\s+/g, "")
		.split("/")
		.filter(Boolean);

	for (let index = parts.length - 1; index >= 0; index -= 1) {
		if (/^[HG]\d+$/.test(parts[index])) {
			return parts[index];
		}
	}

	return parts.length > 0 ? parts[parts.length - 1] : undefined;
};

const mapDssDifferences = (differences?: RawDssDifference[]): DssVariant[] => {
	if (!differences?.length) return [];

	return differences.map((difference, index) => {
		const normalizedPosition =
			typeof difference.position === "number"
				? Math.max(0, Math.trunc(difference.position - 1))
				: index;

		return {
			position: normalizedPosition,
			dss_word: difference.dss_word ?? "",
			masoretic_word: difference.masoretic_word ?? "",
			comment_v2_en: difference.comment_v2_en ?? difference.commentary,
			comment_v2_es: difference.comment_v2_es,
			comment_v2_he: difference.comment_v2_he,
			masoretic_strong: difference.masoretic_strong,
			dss_strong: difference.dss_strong,
		};
	});
};

const mapTranslationFootnotes = (
	footnotes?: RawTranslationFootnote[],
): TranslationFootnote[] => {
	if (!footnotes?.length) return [];

	return footnotes
		.map((footnote): TranslationFootnote | null => {
			if (!footnote.marker && !footnote.number && !footnote.explanation) {
				return null;
			}

			return {
				marker: footnote.marker ?? "",
				number: footnote.number ?? "",
				word: footnote.word ?? "",
				explanation: footnote.explanation ?? "",
			};
		})
		.filter((footnote): footnote is TranslationFootnote => footnote !== null);
};

const loadCoreChapter = async (
	book: BookResponse,
	chapter: number,
): Promise<RawVerse[]> => {
	const chapterPath =
		book.section === "besorah"
			? `/data/besorah/${book.id}/${chapter}.json`
			: `/data/oe/${book.id}/${chapter}.json`;

	try {
		return await fetchJson<RawVerse[]>(chapterPath);
	} catch {
		return [];
	}
};

const loadTranslationChapter = async (
	bookId: string,
	chapter: number,
): Promise<Record<number, RawTranslationVerse>> => {
	// Try TTH_2 first (official Spanish translation)
	const tthBookId =
		TTH_BOOK_MAPPING[bookId.charAt(0).toUpperCase() + bookId.slice(1)];
	if (tthBookId) {
		try {
			const translationBook = await fetchJson<RawTranslationBook>(
				`/data/tth/${tthBookId}.json`,
			);
			const chapterData = translationBook.chapters?.find(
				(item) => item.chapter === chapter,
			);

			if (chapterData) {
				return Object.fromEntries(
					chapterData.verses.map((verse) => [verse.verse, verse]),
				);
			}
		} catch {
			// TTH_2 not available for this book, try BES fallback below
		}
	}

	// Try BES fallback
	try {
		const translationBook = await fetchJson<RawTranslationBook>(
			`/data/bes/${bookId}.json`,
		);
		const chapterData = translationBook.chapters?.find(
			(item) => item.chapter === chapter,
		);

		if (!chapterData) return {};

		return Object.fromEntries(
			chapterData.verses.map((verse) => [verse.verse, verse]),
		);
	} catch {
		return {};
	}
};

const loadDssChapter = async (
	bookId: string,
	chapter: number,
): Promise<Record<number, RawDssVerse>> => {
	const dssBookKey = toDssBookKey(bookId);

	try {
		const dssBook = await fetchJson<RawDssBook>(`/data/dss/${dssBookKey}.json`);
		const chapterData = dssBook.chapters?.[String(chapter)];

		if (!chapterData?.verses) return {};

		return Object.entries(chapterData.verses).reduce(
			(acc, [verseKey, verseValue]) => {
				acc[Number.parseInt(verseKey, 10)] = verseValue;
				return acc;
			},
			{} as Record<number, RawDssVerse>,
		);
	} catch {
		return {};
	}
};

const loadTranslitChapter = async (
	bookId: string,
	chapter: number,
): Promise<Record<number, RawTranslitWord[]>> => {
	try {
		const translitBook = await fetchJson<RawTranslitBook>(
			`/data/translit/${bookId}.json`,
		);

		const verseMap: Record<number, RawTranslitWord[]> = {};
		for (const verseEntry of translitBook.verses ?? []) {
			if (verseEntry.chapter !== chapter) continue;
			verseMap[verseEntry.verse] = verseEntry.words ?? [];
		}

		return verseMap;
	} catch {
		return {};
	}
};

const findFallbackTranslitWord = (
	word: RawWord,
	translitWords: RawTranslitWord[],
): RawTranslitWord | undefined => {
	const baseStrong = extractBaseStrong(word.strong);
	const normalizedText = normalizeSurfaceWord(word.text);

	if (!baseStrong && !normalizedText) {
		return undefined;
	}

	return translitWords.find((candidate) => {
		const candidateStrong = extractBaseStrong(candidate.strong);
		const candidateText = normalizeSurfaceWord(candidate.text);

		const strongMatches =
			baseStrong && candidateStrong ? baseStrong === candidateStrong : false;
		const textMatches =
			normalizedText && candidateText
				? normalizedText === candidateText
				: false;

		if (baseStrong && !strongMatches) return false;
		if (normalizedText && !textMatches) return false;

		return strongMatches || textMatches;
	});
};

const mapVerse = (
	rawVerse: RawVerse,
	translationVerse?: RawTranslationVerse,
	dssVerse?: RawDssVerse,
	translitWords?: RawTranslitWord[],
	options?: {
		language?: "es" | "en";
		showDss?: boolean;
		hebrewOnly?: boolean;
	},
	ts2009Translation?: string | null,
): VerseResponse => {
	const dssVariants = mapDssDifferences(dssVerse?.differences);
	const dssPositions = new Set(dssVariants.map((variant) => variant.position));
	const sourceWords = rawVerse.words ?? [];
	const canMapTranslitByPosition = translitWords
		? translitWords.length === sourceWords.length
		: false;

	const words: WordResponse[] = sourceWords.map((word, index) => {
		const translitWord = canMapTranslitByPosition
			? translitWords?.[index]
			: translitWords
				? findFallbackTranslitWord(word, translitWords)
				: undefined;

		return {
			position: index,
			text: word.text,
			strong: word.strong,
			morph: word.morph,
			prefixes: word.prefixes ?? [],
			has_dss_variant: dssPositions.has(index),
			translit_en: word.translit_en ?? translitWord?.translit_en,
			translit_es: word.translit_es ?? translitWord?.translit_es,
		};
	});

	const response: VerseResponse = {
		chapter: rawVerse.chapter,
		verse: rawVerse.verse,
		hebrew: rawVerse.hebrew,
		words,
	};

	// Handle translation based on language
	if (!options?.hebrewOnly) {
		if (options?.language === "en") {
			if (ts2009Translation) {
				// Use TS2009 for English only.
				response.translation = ts2009Translation;
				response.translation_language = "en";
			}
		} else if (
			options?.language === "es" &&
			(translationVerse?.bes || translationVerse?.tth)
		) {
			// Use TTH/BES for Spanish or fallback
			response.translation = translationVerse.bes ?? translationVerse.tth ?? "";
			response.translation_language = "es";
			const translationFootnotes = mapTranslationFootnotes(
				translationVerse.footnotes,
			);
			if (translationFootnotes.length > 0) {
				response.translation_footnotes = translationFootnotes;
			}
		}
	}

	if (options?.showDss && dssVariants.length > 0) {
		response.dss = dssVariants;
	}

	return response;
};

export const getBooks = async (): Promise<BookResponse[]> => {
	if (!booksPromise) {
		booksPromise = (async () => {
			const metadata = await loadMetadata();
			const books = metadata.books;

			const hasPlaceholderLabels = books.some(
				(book) =>
					book.hebrew_name === book.name ||
					book.spanish_name === book.name ||
					book.hebrew_transliteration === book.name,
			);

			if (!hasPlaceholderLabels) {
				return books;
			}

			const hydrated = await Promise.all(
				books.map(async (book) => {
					try {
						const translationBook = await fetchJson<RawTranslationBook>(
							`/data/bes/${book.id}.json`,
						);
						const bookInfo = translationBook.book_info;

						return {
							...book,
							hebrew_name: bookInfo?.hebrew_name || book.hebrew_name,
							spanish_name: bookInfo?.spanish_name || book.spanish_name,
						};
					} catch {
						return book;
					}
				}),
			);

			return hydrated;
		})().catch((error) => {
			booksPromise = null;
			throw error;
		});
	}

	return booksPromise;
};

export const lookupBook = async (bookName: string): Promise<BookResponse> => {
	const metadata = await loadMetadata();
	const match = findBook(metadata.books, bookName);

	if (!match) {
		throw new Error(`Book not found: ${bookName}`);
	}

	return match;
};

export const getChapterCount = async (book: string): Promise<number> => {
	const metadata = await loadMetadata();
	const bookEntry = findBook(metadata.books, book);

	if (!bookEntry) return 1;
	return bookEntry.chapters;
};

export const getVerseCount = async (
	book: string,
	chapter: number,
): Promise<number> => {
	const metadata = await loadMetadata();
	const bookEntry = findBook(metadata.books, book);

	if (!bookEntry) return 1;

	const verseCounts = metadata.verse_counts?.[bookEntry.name];
	if (verseCounts?.[String(chapter)]) {
		return verseCounts[String(chapter)];
	}

	const chapterVerses = await getChapterVerses(bookEntry.id, chapter, {
		hebrewOnly: true,
	});
	return chapterVerses.length;
};

export const getChapterVerses = async (
	book: string,
	chapter: number,
	options?: {
		language?: "es" | "en";
		showDss?: boolean;
		hebrewOnly?: boolean;
	},
): Promise<VerseResponse[]> => {
	const metadata = await loadMetadata();
	const bookEntry = findBook(metadata.books, book);

	if (!bookEntry) return [];

	const [coreVerses, translations, dssVerses, transliterations] =
		await Promise.all([
			loadCoreChapter(bookEntry, chapter),
			options?.hebrewOnly
				? Promise.resolve<Record<number, RawTranslationVerse>>({})
				: loadTranslationChapter(bookEntry.id, chapter),
			options?.showDss
				? loadDssChapter(bookEntry.id, chapter)
				: Promise.resolve<Record<number, RawDssVerse>>({}),
			loadTranslitChapter(bookEntry.id, chapter),
		]);

	// If language is English, load TS2009 translations from Supabase (with caching)
	let ts2009Translations: Record<number, string> = {};
	if (options?.language === "en") {
		const ts2009Promises = coreVerses.map((verse) =>
			fetchCachedTs2009Translation(bookEntry.id, chapter, verse.verse),
		);
		const ts2009Results = await Promise.all(ts2009Promises);
		ts2009Translations = Object.fromEntries(
			coreVerses
				.map((verse, index) => [verse.verse, ts2009Results[index]])
				.filter(([, translation]) => translation !== null),
		);
	}

	return coreVerses.map((rawVerse) =>
		mapVerse(
			rawVerse,
			translations[rawVerse.verse],
			dssVerses[rawVerse.verse],
			transliterations[rawVerse.verse],
			options,
			ts2009Translations[rawVerse.verse],
		),
	);
};

export const getVerse = async (
	book: string,
	chapter: number,
	verse: number,
	options?: {
		language?: "es" | "en";
		showDss?: boolean;
		hebrewOnly?: boolean;
	},
): Promise<VerseResponse | null> => {
	const verses = await getChapterVerses(book, chapter, options);
	return verses.find((item) => item.verse === verse) ?? null;
};

// ── Lexicon Service ───────────────────────────────────────────────────────

export interface DefinitionItem {
	text: string;
	source: "custom" | "strong" | "bdb" | string;
	language: "en" | "es" | string;
}

export interface WordAnalysis {
	strong_number: string;
	hebrew?: string;
	translit_en?: string;
	translit_es?: string;
	definitions: DefinitionItem[];
	root?: string;
	root_strong?: string;
	root_definitions?: DefinitionItem[];
	root_translit_en?: string;
	root_translit_es?: string;
	occurrences_count: number;
	instances?: Array<string | { verse: string; text: string }>;
}

type RawDefinition = {
	text?: string;
	text_en?: string;
	text_es?: string;
	source?: string;
};

type RawOccurrence = {
	total?: number;
	references?: string[];
};

type RawWordEntry = {
	strong_number?: string;
	lemma?: string;
	hebrew?: string;
	translit_en?: string;
	translit_es?: string;
	transliteration_en?: string;
	transliteration_es?: string;
	definitions?: RawDefinition[];
	occurrences?: RawOccurrence;
	root_ref?: string;
	root_strong?: string;
};

type RawCustomInstance = {
	book: string;
	chapter: number;
	verse: number;
};

type RawCustomEntry = {
	strong_number?: string;
	compound_key?: string;
	hebrew?: string;
	transliteration_en?: string;
	transliteration_es?: string;
	definitions?: RawDefinition[];
	root?: string;
	root_strong?: string;
	manual_instances?: string[];
	oe_instances?: RawCustomInstance[];
	nt_instances?: RawCustomInstance[];
};

let wordsPromise: Promise<Record<string, RawWordEntry>> | null = null;
let rootsPromise: Promise<Record<string, RawWordEntry>> | null = null;
let customPromise: Promise<Record<string, RawCustomEntry>> | null = null;

const loadWords = async (): Promise<Record<string, RawWordEntry>> => {
	if (!wordsPromise) {
		wordsPromise = fetchJson<Record<string, RawWordEntry>>(
			"/data/dict/words.json",
		);
	}
	return wordsPromise;
};

const loadRoots = async (): Promise<Record<string, RawWordEntry>> => {
	if (!rootsPromise) {
		rootsPromise = fetchJson<Record<string, RawWordEntry>>(
			"/data/dict/roots.json",
		);
	}
	return rootsPromise;
};

const loadCustomDefinitions = async (): Promise<
	Record<string, RawCustomEntry>
> => {
	if (!customPromise) {
		customPromise = fetchJson<Record<string, RawCustomEntry>>(
			"/data/dict/custom_definitions.json",
		);
	}
	return customPromise;
};

const normalizeStrong = (strong?: string): string | null => {
	if (!strong) return null;
	const cleaned = strong.trim().toUpperCase();
	if (/^[HG]\d+$/.test(cleaned)) return cleaned;
	return null;
};

const formatOccurrenceReference = (reference: string): string => {
	const [book, chapter, verse] = reference.split(".");
	if (!book || !chapter || !verse) return reference;
	return `${book} ${chapter}:${verse}`;
};

const formatCustomOccurrence = (instance: RawCustomInstance): string =>
	`${instance.book} ${instance.chapter}:${instance.verse}`;

const mapDefinitions = (
	definitions: RawDefinition[] | undefined,
	language: "en" | "es",
): DefinitionItem[] => {
	if (!definitions?.length) return [];

	const mapped: Array<DefinitionItem | null> = definitions.map((definition) => {
		const text =
			language === "es"
				? (definition.text_es ?? definition.text)
				: (definition.text_en ?? definition.text);

		if (!text) return null;

		return {
			text,
			source: definition.source ?? "strong",
			language,
		};
	});

	return mapped.filter((item): item is DefinitionItem => Boolean(item));
};

const mergeUniqueDefinitions = (
	...groups: DefinitionItem[][]
): DefinitionItem[] => {
	const seen = new Set<string>();
	const merged: DefinitionItem[] = [];

	for (const group of groups) {
		for (const definition of group) {
			const key = `${definition.source}:${definition.text.toLowerCase()}`;
			if (seen.has(key)) continue;
			seen.add(key);
			merged.push(definition);
		}
	}

	return merged;
};

const getRootEntry = (
	rootStrong: string | undefined,
	words: Record<string, RawWordEntry>,
	roots: Record<string, RawWordEntry>,
	custom: Record<string, RawCustomEntry>,
): RawWordEntry | RawCustomEntry | null => {
	const normalizedRoot = normalizeStrong(rootStrong);
	if (!normalizedRoot) return null;

	return (
		roots[normalizedRoot] ??
		words[normalizedRoot] ??
		custom[normalizedRoot] ??
		null
	);
};

const isRawWordEntry = (
	value: RawWordEntry | RawCustomEntry | null,
): value is RawWordEntry =>
	Boolean(value && ("lemma" in value || "root_ref" in value));

const isRawCustomEntry = (
	value: RawWordEntry | RawCustomEntry | null,
): value is RawCustomEntry =>
	Boolean(value && ("root" in value || "compound_key" in value));

const toWordAnalysis = (
	strong: string,
	language: "en" | "es",
	words: Record<string, RawWordEntry>,
	roots: Record<string, RawWordEntry>,
	custom: Record<string, RawCustomEntry>,
): WordAnalysis | null => {
	const wordEntry = words[strong];
	const rootsEntry = roots[strong];
	const customEntry = custom[strong];
	const dictionaryEntry = wordEntry ?? rootsEntry;

	if (!dictionaryEntry && !customEntry) {
		return null;
	}

	const strongNumber =
		customEntry?.strong_number ?? dictionaryEntry?.strong_number ?? strong;
	const hebrew =
		customEntry?.hebrew ?? dictionaryEntry?.lemma ?? dictionaryEntry?.hebrew;
	const translit_en =
		customEntry?.transliteration_en ??
		dictionaryEntry?.translit_en ??
		dictionaryEntry?.transliteration_en;
	const translit_es =
		customEntry?.transliteration_es ??
		dictionaryEntry?.translit_es ??
		dictionaryEntry?.transliteration_es;

	const definitions = mergeUniqueDefinitions(
		mapDefinitions(customEntry?.definitions, language),
		mapDefinitions(dictionaryEntry?.definitions, language),
	);

	const rootStrong =
		customEntry?.root_strong ??
		dictionaryEntry?.root_ref ??
		dictionaryEntry?.root_strong;
	const rootEntry = getRootEntry(rootStrong, words, roots, custom);

	const rootDefinitions = mergeUniqueDefinitions(
		mapDefinitions(rootEntry?.definitions, language),
	);

	const occurrenceReferences =
		dictionaryEntry?.occurrences?.references?.map(formatOccurrenceReference) ??
		[];
	const manualInstances = customEntry?.manual_instances ?? [];
	const oeInstances =
		customEntry?.oe_instances?.map(formatCustomOccurrence) ?? [];
	const ntInstances =
		customEntry?.nt_instances?.map(formatCustomOccurrence) ?? [];
	const instances = [
		...manualInstances,
		...oeInstances,
		...ntInstances,
		...occurrenceReferences,
	];

	const occurrencesCount =
		customEntry?.manual_instances?.length ||
		customEntry?.oe_instances?.length ||
		customEntry?.nt_instances?.length
			? instances.length
			: (dictionaryEntry?.occurrences?.total ?? instances.length);

	return {
		strong_number: strongNumber,
		hebrew,
		translit_en,
		translit_es,
		definitions,
		root:
			customEntry?.root ??
			(isRawWordEntry(rootEntry) ? rootEntry.lemma : undefined) ??
			(isRawCustomEntry(rootEntry) ? rootEntry.hebrew : undefined),
		root_strong: rootStrong,
		root_definitions: rootDefinitions.length > 0 ? rootDefinitions : undefined,
		root_translit_en: isRawWordEntry(rootEntry)
			? rootEntry.translit_en
			: rootEntry?.transliteration_en,
		root_translit_es: isRawWordEntry(rootEntry)
			? rootEntry.translit_es
			: rootEntry?.transliteration_es,
		occurrences_count: occurrencesCount,
		instances: instances.length > 0 ? instances : undefined,
	};
};

export const loadLexiconEntry = async (
	strong?: string,
	language?: "en" | "es",
): Promise<WordAnalysis | null> => {
	const normalizedStrong = normalizeStrong(strong);
	if (!normalizedStrong) return null;

	const selectedLanguage = language ?? "en";
	const [words, roots, custom] = await Promise.all([
		loadWords(),
		loadRoots(),
		loadCustomDefinitions(),
	]);

	return toWordAnalysis(
		normalizedStrong,
		selectedLanguage,
		words,
		roots,
		custom,
	);
};

export const searchLexicon = async (
	query: string,
	options?: { limit?: number; offset?: number },
): Promise<WordAnalysis[]> => {
	const needle = query.trim().toLowerCase();
	if (!needle) return [];

	const [words, roots, custom] = await Promise.all([
		loadWords(),
		loadRoots(),
		loadCustomDefinitions(),
	]);

	const strongKeys = new Set<string>([
		...Object.keys(words),
		...Object.keys(custom),
	]);

	const matches: WordAnalysis[] = [];

	for (const strong of strongKeys) {
		const word = words[strong];
		const customEntry = custom[strong];

		const haystack = [
			strong,
			word?.lemma,
			word?.translit_en,
			word?.translit_es,
			customEntry?.hebrew,
			customEntry?.transliteration_en,
			customEntry?.transliteration_es,
			...(word?.definitions?.flatMap((definition) => [
				definition.text_en,
				definition.text_es,
			]) ?? []),
			...(customEntry?.definitions?.flatMap((definition) => [
				definition.text_en,
				definition.text_es,
				definition.text,
			]) ?? []),
		]
			.filter(Boolean)
			.join(" ")
			.toLowerCase();

		if (!haystack.includes(needle)) continue;

		const analysis = toWordAnalysis(strong, "en", words, roots, custom);
		if (analysis) {
			matches.push(analysis);
		}
	}

	const offset = options?.offset ?? 0;
	const limit = options?.limit ?? 20;
	return matches.slice(offset, offset + limit);
};

// ── Prefix Service ───────────────────────────────────────────────────────

let prefixesPromise: Promise<Record<string, unknown>> | null = null;

const loadPrefixes = async (): Promise<Record<string, unknown>> => {
	if (!prefixesPromise) {
		prefixesPromise = fetchJson<Record<string, unknown>>("/data/prefixes.json");
	}
	return prefixesPromise;
};

export const loadPrefix = async (prefixId: string): Promise<unknown> => {
	const prefixes = await loadPrefixes();
	return prefixes[prefixId] ?? null;
};
