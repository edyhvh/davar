import React from "react";

const superscriptDigitMap: Record<string, string> = {
  "⁰": "0",
  "¹": "1",
  "²": "2",
  "³": "3",
  "⁴": "4",
  "⁵": "5",
  "⁶": "6",
  "⁷": "7",
  "⁸": "8",
  "⁹": "9",
};

const superscriptPattern = /[⁰¹²³⁴⁵⁶⁷⁸⁹]+/g;
const bracketFootnotePattern = /\[([a-z0-9]+)\]/gi;

const normalizeSuperscripts = (value: string): string =>
  value
    .split("")
    .map((char) => superscriptDigitMap[char] ?? char)
    .join("");

const renderTextSegment = (
  text: string,
  italic: boolean,
  keyPrefix: string,
  hideSuperscripts: boolean,
): React.ReactNode[] => {
  const nodes: React.ReactNode[] = [];
  let lastIndex = 0;
  let matchIndex = 0;

  // Find all matches (both superscript digits and bracket footnotes)
  const allMatches: Array<{type: 'superscript' | 'bracket', start: number, end: number, content: string}> = [];
  
  // Find superscript digit matches (create fresh RegExp to avoid lastIndex mutation)
  for (const match of text.matchAll(new RegExp(superscriptPattern))) {
    if (match.index === undefined) continue;
    allMatches.push({
      type: 'superscript',
      start: match.index,
      end: match.index + match[0].length,
      content: match[0]
    });
  }

  // Find bracket footnote matches (create fresh RegExp to avoid lastIndex mutation)
  for (const match of text.matchAll(new RegExp(bracketFootnotePattern))) {
    if (match.index === undefined) continue;
    allMatches.push({
      type: 'bracket',
      start: match.index,
      end: match.index + match[0].length,
      content: match[0]
    });
  }
  
  // Sort matches by position
  allMatches.sort((a, b) => a.start - b.start);

  for (const match of allMatches) {
    const start = match.start;
    const end = match.end;
    const plainText = text.slice(lastIndex, start);

    if (plainText) {
      nodes.push(
        italic ? (
          <span key={`${keyPrefix}-text-${matchIndex}`} className="italic">
            {plainText}
          </span>
        ) : (
          <React.Fragment key={`${keyPrefix}-text-${matchIndex}`}>
            {plainText}
          </React.Fragment>
        ),
      );
    }

    if (!hideSuperscripts) {
      if (match.type === 'superscript') {
        const normalized = normalizeSuperscripts(match.content);
        nodes.push(
          <sup
            key={`${keyPrefix}-sup-${matchIndex}`}
            className={`ml-0.5 align-super text-[0.65em] leading-none${italic ? " italic" : ""}`}
          >
            {normalized}
          </sup>,
        );
      } else if (match.type === 'bracket') {
        // Render bracket footnotes as superscripts
        const marker = match.content.slice(1, -1); // Remove brackets
        nodes.push(
          <sup
            key={`${keyPrefix}-bracket-${matchIndex}`}
            className={`ml-0.5 align-super text-[0.65em] leading-none${italic ? " italic" : ""}`}
          >
            {marker}
          </sup>,
        );
      }
    }

    lastIndex = end;
    matchIndex += 1;
  }

  const trailingText = text.slice(lastIndex);
  if (trailingText) {
    nodes.push(
      italic ? (
        <span key={`${keyPrefix}-text-tail`} className="italic">
          {trailingText}
        </span>
      ) : (
        <React.Fragment key={`${keyPrefix}-text-tail`}>
          {trailingText}
        </React.Fragment>
      ),
    );
  }

  return nodes;
};

export const renderTranslation = (
  translation: string,
  options?: { hideSuperscripts?: boolean },
): React.ReactNode[] => {
  if (!translation) return [];

  const { hideSuperscripts = false } = options || {};
  const tokens = translation
    .split(/(<\/?em>)/i)
    .filter((token) => token !== "");
  const nodes: React.ReactNode[] = [];
  let italic = false;

  tokens.forEach((token, index) => {
    const lowerToken = token.toLowerCase();

    if (lowerToken === "<em>") {
      italic = true;
      return;
    }

    if (lowerToken === "</em>") {
      italic = false;
      return;
    }

    nodes.push(
      ...renderTextSegment(token, italic, `seg-${index}`, hideSuperscripts),
    );
  });

  return nodes;
};
