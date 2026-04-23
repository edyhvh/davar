import type { TranslationFootnote } from "@/src/types/api";

export const sanitizeEmTags = (value: string): string =>
  value.replace(/<\/?em>/gi, "");

export const escapeRegex = (value: string): string =>
  value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const SUPERSCRIPT_DIGITS: Record<string, string> = {
  "0": "⁰",
  "1": "¹",
  "2": "²",
  "3": "³",
  "4": "⁴",
  "5": "⁵",
  "6": "⁶",
  "7": "⁷",
  "8": "⁸",
  "9": "⁹",
};

export const toSuperscriptNumber = (value: string): string =>
  value
    .split("")
    .map((digit) => SUPERSCRIPT_DIGITS[digit] ?? digit)
    .join("");

export const createFootnoteLookup = (
  footnotes?: TranslationFootnote[],
): Map<string, TranslationFootnote> => {
  const lookup = new Map<string, TranslationFootnote>();

  if (!footnotes?.length) {
    return lookup;
  }

  for (const footnote of footnotes) {
    const marker = footnote.marker.trim();
    const number = footnote.number.trim();

    if (marker) {
      lookup.set(marker, footnote);
      lookup.set(`[${marker}]`, footnote);
    }

    if (number) {
      lookup.set(toSuperscriptNumber(number), footnote);
    }
  }

  return lookup;
};

export const buildMarkerRegex = (
  footnoteLookup: Map<string, TranslationFootnote>,
): RegExp | null => {
  const markers = Array.from(footnoteLookup.keys()).sort(
    (a, b) => b.length - a.length,
  );
  return markers.length > 0
    ? new RegExp(
        `(${markers.map((marker) => escapeRegex(marker)).join("|")})`,
        "g",
      )
    : null;
};
