import {
  getTranslationKey,
  shouldHideSuperscripts,
  type AppLanguage,
} from "./translationConfig";

const superscriptPattern = /[⁰¹²³⁴⁵⁶⁷⁸⁹]+/g;
const bracketFootnotePattern = /\[([a-z0-9]+)\]/gi;

const stripSuperscripts = (value: string): string => {
  let result = value.replace(superscriptPattern, "");
  result = result.replace(bracketFootnotePattern, "");
  return result;
};

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
