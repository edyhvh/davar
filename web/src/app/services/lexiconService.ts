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

const isRawWordEntry = (
  value: RawWordEntry | RawCustomEntry | null,
): value is RawWordEntry => Boolean(value && ("lemma" in value || "root_ref" in value));

const isRawCustomEntry = (
  value: RawWordEntry | RawCustomEntry | null,
): value is RawCustomEntry => Boolean(value && ("root" in value || "compound_key" in value));

const jsonCache = new Map<string, Promise<unknown>>();

const fetchJson = async <T>(path: string): Promise<T> => {
  if (!jsonCache.has(path)) {
    jsonCache.set(
      path,
      fetch(path, { cache: "force-cache" }).then(async (response) => {
        if (!response.ok) {
          throw new Error(`Failed to load static data: ${path}`);
        }
        return response.json();
      }),
    );
  }

  return jsonCache.get(path) as Promise<T>;
};

let wordsPromise: Promise<Record<string, RawWordEntry>> | null = null;
let rootsPromise: Promise<Record<string, RawWordEntry>> | null = null;
let customPromise: Promise<Record<string, RawCustomEntry>> | null = null;

const loadWords = async (): Promise<Record<string, RawWordEntry>> => {
  if (!wordsPromise) {
    wordsPromise = fetchJson<Record<string, RawWordEntry>>("/data/dict/words.json");
  }
  return wordsPromise;
};

const loadRoots = async (): Promise<Record<string, RawWordEntry>> => {
  if (!rootsPromise) {
    rootsPromise = fetchJson<Record<string, RawWordEntry>>("/data/dict/roots.json");
  }
  return rootsPromise;
};

const loadCustomDefinitions = async (): Promise<Record<string, RawCustomEntry>> => {
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

const mergeUniqueDefinitions = (...groups: DefinitionItem[][]): DefinitionItem[] => {
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

  return roots[normalizedRoot] ?? words[normalizedRoot] ?? custom[normalizedRoot] ?? null;
};

const toWordAnalysis = (
  strong: string,
  language: "en" | "es",
  words: Record<string, RawWordEntry>,
  roots: Record<string, RawWordEntry>,
  custom: Record<string, RawCustomEntry>,
): WordAnalysis | null => {
  const wordEntry = words[strong];
  const customEntry = custom[strong];

  if (!wordEntry && !customEntry) {
    return null;
  }

  const strongNumber = customEntry?.strong_number ?? wordEntry?.strong_number ?? strong;
  const hebrew = customEntry?.hebrew ?? wordEntry?.lemma ?? wordEntry?.hebrew;
  const translit_en =
    customEntry?.transliteration_en ??
    wordEntry?.translit_en ??
    wordEntry?.transliteration_en;
  const translit_es =
    customEntry?.transliteration_es ??
    wordEntry?.translit_es ??
    wordEntry?.transliteration_es;

  const definitions = mergeUniqueDefinitions(
    mapDefinitions(customEntry?.definitions, language),
    mapDefinitions(wordEntry?.definitions, language),
  );

  const rootStrong = customEntry?.root_strong ?? wordEntry?.root_ref ?? wordEntry?.root_strong;
  const rootEntry = getRootEntry(rootStrong, words, roots, custom);

  const rootDefinitions = mergeUniqueDefinitions(mapDefinitions(rootEntry?.definitions, language));

  const occurrenceReferences = wordEntry?.occurrences?.references?.map(formatOccurrenceReference) ?? [];
  const manualInstances = customEntry?.manual_instances ?? [];
  const oeInstances = customEntry?.oe_instances?.map(formatCustomOccurrence) ?? [];
  const ntInstances = customEntry?.nt_instances?.map(formatCustomOccurrence) ?? [];
  const instances = [...manualInstances, ...oeInstances, ...ntInstances, ...occurrenceReferences];

  const occurrencesCount =
    customEntry?.manual_instances?.length ||
    customEntry?.oe_instances?.length ||
    customEntry?.nt_instances?.length
      ? instances.length
      : (wordEntry?.occurrences?.total ?? instances.length);

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

export const getWordAnalysisByStrong = async (
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

  return toWordAnalysis(normalizedStrong, selectedLanguage, words, roots, custom);
};

export const searchWordAnalysis = async (
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
