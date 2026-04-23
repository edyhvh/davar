// Translation configuration utilities for footnote handling and display rules

export type AppLanguage = "en" | "es" | "he";
export type TranslationKey = "ts2009" | "tth" | "delitzsch";

type DssCommentaryInput = {
  comment_v2_en?: string | null;
  comment_v2_es?: string | null;
  comment_v2_he?: string | null;
  dssCommentaryEn?: string | null;
  dssCommentaryEs?: string | null;
  dssCommentaryHe?: string | null;
};

// Mapping from canonical English book names to TTH_2 Hebrew file names
// TTH_2 covers 35 books (Torah, some Neviim, some Ketuvim, some Besorah)
export const TTH_BOOK_MAPPING: Record<string, string> = {
  // TORAH
  "Genesis": "bereshit",
  "Exodus": "shemot",
  "Leviticus": "vaikra",
  "Numbers": "bamidbar",
  "Deuteronomy": "devarim",
  // NEVIIM (Former Prophets)
  "Joshua": "iehoshua",
  "Judges": "shoftim",
  "Samuel1": "shemuel_alef",
  "Samuel2": "shemuel_bet",
  "Kings1": "melajim_alef",
  "Kings2": "melajim_bet",
  // NEVIIM (Latter Prophets)
  "Isaiah": "ieshaiahu",
  "Jeremiah": "irmeiahu",
  "Ezekiel": "iejezkel",
  // NEVIIM (The Twelve)
  "Hosea": "hoshea",
  "Joel": "ioel",
  "Amos": "amos",
  "Jonah": "ionah",
  "Micah": "micah",
  "Nahum": "najum",
  "Habakkuk": "jabakuk",
  "Zephaniah": "tzefaniah",
  "Haggai": "jagai",
  "Zechariah": "zejariah",
  "Malachi": "malaji",
  // KETUVIM (partial in tth_2)
  "Psalms": "tehilim",
  "Proverbs": "mishlei",
  "SongOfSolomon": "shir_hashirim",
  // BESORAH (tth_2 format)
  "Matthew": "matityahu",
  "Mark": "markos",
  "Luke": "lukas",
  "John": "iojanan",
  "Acts": "maasei_hashlijim",
  "Romans": "romanos",
  "Revelation": "sodot",
};

export const getTranslationKey = (language: AppLanguage): TranslationKey => {
  switch (language) {
    case "en":
      return "ts2009";
    case "es":
      return "tth";
    case "he":
      return "delitzsch";
    default:
      return "ts2009"; // fallback
  }
};

export const shouldHideTranslationText = (
  language: AppLanguage,
  hebrewOnly = false,
): boolean => {
  return hebrewOnly || language === "he";
};

export const getDssCommentaryForLanguage = (
  language: AppLanguage,
  commentary?: DssCommentaryInput | null,
): string | undefined => {
  if (!commentary) return undefined;

  const commentaryEn = commentary.comment_v2_en ?? commentary.dssCommentaryEn;
  const commentaryEs = commentary.comment_v2_es ?? commentary.dssCommentaryEs;
  const commentaryHe = commentary.comment_v2_he ?? commentary.dssCommentaryHe;

  if (language === "he") {
    return commentaryHe ?? undefined;
  }

  if (language === "es") {
    return commentaryEs ?? commentaryEn ?? commentaryHe ?? undefined;
  }

  return commentaryEn ?? commentaryEs ?? commentaryHe ?? undefined;
};

export const shouldHideSuperscripts = (
  translationKey: TranslationKey,
): boolean => {
  // TS2009 embeds numeric superscripts that are currently not interactive in UI.
  // TTH markers remain visible so the mobile app can render tappable footnotes.
  return translationKey === "ts2009";
};
