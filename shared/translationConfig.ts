// Translation configuration utilities for footnote handling and display rules

export type AppLanguage = "en" | "es" | "he";
export type TranslationKey = "ts2009" | "tth" | "delitzsch";

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

export const shouldHideSuperscripts = (
  translationKey: TranslationKey,
): boolean => {
  // TTH (Spanish) and TS2009 (English) embed footnote markers that we hide in UI
  return translationKey === "tth" || translationKey === "ts2009";
};
