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

const normalizeSuperscripts = (value: string): string =>
  value
    .split("")
    .map((char) => superscriptDigitMap[char] ?? char)
    .join("");

const renderTextSegment = (
  text: string,
  italic: boolean,
  keyPrefix: string,
): React.ReactNode[] => {
  const nodes: React.ReactNode[] = [];
  let lastIndex = 0;
  let matchIndex = 0;

  for (const match of text.matchAll(superscriptPattern)) {
    if (match.index === undefined) continue;
    const start = match.index;
    const end = start + match[0].length;
    const plainText = text.slice(lastIndex, start);
    const normalized = normalizeSuperscripts(match[0]);

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

    nodes.push(
      <sup
        key={`${keyPrefix}-sup-${matchIndex}`}
        className={`ml-0.5 align-super text-[0.65em] leading-none${italic ? " italic" : ""}`}
      >
        {normalized}
      </sup>,
    );

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

export const renderTranslation = (translation: string): React.ReactNode[] => {
  if (!translation) return [];

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

    nodes.push(...renderTextSegment(token, italic, `seg-${index}`));
  });

  return nodes;
};
