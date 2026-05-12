import type { TranslationFootnote } from "@/src/types/api";

export const DEFAULT_FOOTNOTE_MARKER_COLOR = "#B4834D";

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

export type MarkerMatch = {
  start: number;
  end: number;
  content: string;
};

const superscriptPattern = /[⁰¹²³⁴⁵⁶⁷⁸⁹]+/g;
const bracketFootnotePattern = /\[[a-z0-9]+\]/gi;

export const collectMarkerMatches = (
  text: string,
  markerRegex: RegExp | null,
  renderUnmappedSuperscripts: boolean,
): MarkerMatch[] => {
  const matches: MarkerMatch[] = [];

  if (markerRegex) {
    const explicitMarkerRegex = new RegExp(
      markerRegex.source,
      markerRegex.flags.includes("g")
        ? markerRegex.flags
        : `${markerRegex.flags}g`,
    );

    for (const match of text.matchAll(explicitMarkerRegex)) {
      if (match.index === undefined) continue;
      matches.push({
        start: match.index,
        end: match.index + match[0].length,
        content: match[0],
      });
    }
  }

  if (renderUnmappedSuperscripts) {
    for (const match of text.matchAll(superscriptPattern)) {
      if (match.index === undefined) continue;
      matches.push({
        start: match.index,
        end: match.index + match[0].length,
        content: match[0],
      });
    }

    for (const match of text.matchAll(bracketFootnotePattern)) {
      if (match.index === undefined) continue;
      matches.push({
        start: match.index,
        end: match.index + match[0].length,
        content: match[0],
      });
    }
  }

  if (matches.length === 0) {
    return [];
  }

  const unique = new Map<string, MarkerMatch>();
  for (const match of matches) {
    unique.set(`${match.start}-${match.end}`, match);
  }

  const sortedMatches = Array.from(unique.values()).sort(
    (a, b) => a.start - b.start || b.end - a.end,
  );

  const nonOverlappingMatches: MarkerMatch[] = [];
  let currentEnd = -1;
  for (const match of sortedMatches) {
    if (match.start < currentEnd) {
      continue;
    }
    nonOverlappingMatches.push(match);
    currentEnd = match.end;
  }

  return nonOverlappingMatches;
};

export const resolveFootnoteForMarker = (
  footnoteLookup: Map<string, TranslationFootnote>,
  marker: string,
): TranslationFootnote | undefined => {
  const directMatch = footnoteLookup.get(marker);
  if (directMatch) {
    return directMatch;
  }

  const bracketMatch = /^\[([a-z0-9]+)\]$/i.exec(marker);
  if (!bracketMatch) {
    return undefined;
  }

  const bracketValue = bracketMatch[1];
  return (
    footnoteLookup.get(bracketValue) ??
    footnoteLookup.get(toSuperscriptNumber(bracketValue))
  );
};

export const formatMarkerForDisplay = (marker: string): string => {
  const bracketMatch = /^\[([a-z0-9]+)\]$/i.exec(marker);
  if (!bracketMatch) {
    return marker;
  }

  const bracketValue = bracketMatch[1];
  return /^\d+$/.test(bracketValue)
    ? toSuperscriptNumber(bracketValue)
    : bracketValue;
};
