export type WordResponse = {
  position: number;
  text: string;
  strong?: string;
  morph?: string;
  prefixes: string[];
  has_dss_variant: boolean;
};

export type DssVariant = {
  word_position: number;
  dss_text: string;
  manuscript: string;
  commentary?: string;
};

export type TranslationFootnote = {
  marker: string;
  number: string;
  word: string;
  explanation: string;
};

export type VerseResponse = {
  chapter: number;
  verse: number;
  hebrew: string;
  words: WordResponse[];
  translation?: string;
  translation_language?: string;
  translation_footnotes?: TranslationFootnote[];
  dss?: DssVariant[];
};

export type DefinitionItem = {
  text: string;
  source: string;
  language: string;
};

export type LexiconResponse = {
  strong_number: string;
  hebrew?: string;
  transliteration?: string;
  definitions: DefinitionItem[];
  root?: string;
  root_strong?: string;
  root_transliteration?: string;
  root_definitions?: DefinitionItem[];
  occurrences_count: number;
  instances: string[];
};

export type BookResponse = {
  id: string;
  name: string;
  section: "torah" | "neviim" | "ketuvim" | "besorah";
  chapters: number;
  order: number;
  hebrew_name: string;
  hebrew_transliteration: string;
  spanish_name: string;
};
