import { getTranslationKey, shouldHideSuperscripts, type AppLanguage } from "./translationConfig";

const superscriptPattern = /[⁰¹²³⁴⁵⁶⁷⁸⁹]+/g;

const stripSuperscripts = (value: string): string =>
  value.replace(superscriptPattern, "");

type TranslationDisplayInput = {
  language: AppLanguage;
  translation?: string | null;
  missingTranslationText: string;
};

export const getTranslationDisplayText = ({
  language,
  translation,
  missingTranslationText,
}: TranslationDisplayInput): string => {
  const baseText =
    language === "es" && !translation?.trim()
      ? missingTranslationText
      : (translation ?? "");

  return shouldHideSuperscripts(getTranslationKey(language))
    ? stripSuperscripts(baseText)
    : baseText;
};