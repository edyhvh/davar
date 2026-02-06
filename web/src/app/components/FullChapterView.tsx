import React from "react";
import type {
  DssVariant,
  VerseResponse,
  WordResponse,
} from "../services/verseService";
import {
  getPrefixSegments,
  stripNikud,
  stripCantillation,
  stripMeteg,
} from "../utils/hebrew";
import { renderTranslation } from "../utils/translationFormatter";

interface FullChapterViewProps {
  verses: VerseResponse[];
  bookName: string;
  bookNameHebrew: string;
  chapter: number;
  language: "en" | "es" | "he";
  hebrewOnly: boolean;
  seferMode?: boolean;
  onWordClick: (word: WordResponse) => void;
  showQumran?: boolean;
  selectedWord?: string | null;
  showNikud?: boolean;
  showCantillation?: boolean;
}

export function FullChapterView({
  verses,
  bookName,
  bookNameHebrew,
  chapter,
  language,
  hebrewOnly,
  seferMode = false,
  onWordClick,
  showQumran,
  selectedWord,
  showNikud = true,
  showCantillation = true,
}: FullChapterViewProps) {
  const shouldShowSefer = seferMode && hebrewOnly;

  const normalizeForMatch = (text: string) => {
    let normalized = stripNikud(text);
    normalized = stripCantillation(normalized);
    normalized = stripMeteg(normalized);
    return normalized.replace(/\//g, "");
  };

  const normalizedSelected = selectedWord
    ? normalizeForMatch(selectedWord)
    : null;

  const renderVerseWords = (verse: VerseResponse) => {
    const dssMap = new Map<number, string>();
    verse.dss?.forEach((variant) =>
      dssMap.set(variant.word_position, variant.dss_text),
    );

    return verse.words.map((word, wordIdx) => {
      const variantText = showQumran ? dssMap.get(word.position) : undefined;
      const rawText = variantText ?? word.text;

      // Apply nikud and cantillation settings
      let displayText = rawText;
      if (!showNikud) {
        displayText = stripNikud(displayText);
      }
      if (!showCantillation) {
        displayText = stripCantillation(displayText);
      }
      displayText = stripMeteg(displayText);
      // Remove "/" separators from display
      displayText = displayText.replace(/\//g, "");

      // Always compare against the original Masoretic word text, not the
      // display text which may be a DSS variant.
      const normalizedWord = normalizeForMatch(word.text);
      const isSelected =
        Boolean(normalizedSelected) && normalizedSelected === normalizedWord;

      const prefixSegments = word.prefixes?.length
        ? getPrefixSegments(displayText, word.prefixes)
        : null;

      return (
        <span key={word.position}>
          <span
            onClick={() => onWordClick(word)}
            className={`cursor-pointer transition-colors duration-200 ${isSelected ? "verse-highlight" : ""}`}
            style={
              variantText ? { color: "var(--copper-highlight)" } : undefined
            }
          >
            {prefixSegments?.prefixes?.length ? (
              <>
                <span
                  style={{ color: "var(--text-secondary)" }}
                  className="cursor-pointer hover:opacity-80"
                  title={`Prefix: ${word.prefixes?.join(", ")}`}
                >
                  {prefixSegments.prefixes.join("")}
                </span>
                <span style={{ color: "var(--text-hebrew)" }}>
                  {prefixSegments.root}
                </span>
              </>
            ) : (
              displayText
            )}
          </span>
          {wordIdx < verse.words.length - 1 && " "}
        </span>
      );
    });
  };

  return (
    <div className="space-y-6 transition-all duration-500 full-chapter-scroll">
      {/* Chapter Verses */}
      {shouldShowSefer ? (
        <div className="px-2">
          <div
            className="leading-relaxed tracking-[0.01em]"
            style={{
              fontFamily: "'Cardo', serif",
              fontSize: "48px",
              direction: "rtl",
              color: "var(--text-hebrew)",
              lineHeight: 1.9,
              letterSpacing: "0.01em",
            }}
          >
            {verses.map((verse, idx) => (
              <span key={verse.verse}>
                <span
                  className="text-[var(--text-secondary)] opacity-40 ml-2"
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: "14px",
                  }}
                >
                  [{idx + 1}]
                </span>
                {renderVerseWords(verse)}
                {idx < verses.length - 1 && " "}
              </span>
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-8 px-2">
          {verses.map((verse, idx) => (
            <div
              key={verse.verse}
              className="space-y-3 transition-all duration-300 verse-block"
            >
              {/* Hebrew Text with Verse Number */}
              <div
                className="leading-relaxed tracking-[0.01em]"
                style={{
                  fontFamily: "'Cardo', serif",
                  fontSize: "48px",
                  direction: "rtl",
                  color: "var(--text-hebrew)",
                  lineHeight: 1.85,
                }}
              >
                <span
                  className="text-[var(--text-secondary)] opacity-40 ml-2"
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: "14px",
                  }}
                >
                  [{idx + 1}]
                </span>
                {renderVerseWords(verse)}
              </div>

              {/* Translation - only show if not Hebrew Only mode */}
              {!hebrewOnly && (
                <div
                  className="text-[var(--text-secondary)] leading-relaxed"
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    fontSize: "15px",
                  }}
                >
                  [{renderTranslation(verse.translation ?? "")}]
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
