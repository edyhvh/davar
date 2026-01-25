import React from "react";
import { OnboardingWordHint } from "./OnboardingWordHint";
import { SwipeIndicator } from "./SwipeIndicator";
import { FullChapterView } from "./FullChapterView";
import type {
  DssVariant,
  VerseResponse,
  WordResponse,
} from "../services/verseService";
import {
  parseHebrewWord,
  stripNikud,
  stripCantillation,
  stripMeteg,
  getPrefixSegments,
} from "../utils/hebrew";
import { renderTranslation } from "../utils/translationFormatter";
import { useTranslation } from "../hooks/useTranslation";

interface VerseDisplayProps {
  hebrewText: string;
  translation: string;
  verseRef: string;
  verseNumber: number;
  bookName: string;
  bookNameHebrew: string;
  book: string;
  chapter: number;
  language: "en" | "es" | "he";
  onWordClick: (word: WordResponse) => void;
  previousVerseSnippet?: string;
  nextVerseSnippet?: string;
  showOnboardingHint?: boolean;
  showQumran?: boolean;
  showFullChapter?: boolean;
  hebrewOnly?: boolean;
  showNikud?: boolean;
  showCantillation?: boolean;
  chapterVerses?: VerseResponse[];
  words: WordResponse[];
  dssVariants?: DssVariant[];
  selectedWord?: string | null;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}

export function VerseDisplay({
  hebrewText,
  translation,
  verseRef,
  verseNumber,
  bookName,
  bookNameHebrew,
  book,
  chapter,
  language,
  onWordClick,
  previousVerseSnippet,
  nextVerseSnippet,
  showOnboardingHint = false,
  showQumran = false,
  showFullChapter = false,
  hebrewOnly = false,
  showNikud = true,
  showCantillation = false,
  chapterVerses,
  words,
  dssVariants,
  selectedWord,
  onSwipeUp,
  onSwipeDown,
}: VerseDisplayProps) {
  const { t } = useTranslation(language);
  // Function to render Hebrew text with DSS variants
  const renderHebrewText = () => {
    const dssMap = new Map<number, string>();
    dssVariants?.forEach((variant) => {
      dssMap.set(variant.word_position, variant.dss_text);
    });

    const sourceWords =
      words.length > 0
        ? words
        : hebrewText.split(" ").map((word, index) => ({
            position: index + 1,
            text: word,
            text_no_nikud: word,
            prefixes: [],
            has_dss_variant: false,
          }));

    const normalizeForMatch = (text: string) => {
      let normalized = stripNikud(text);
      normalized = stripCantillation(normalized);
      normalized = stripMeteg(normalized);
      return normalized.replace(/\//g, "");
    };

    const normalizedSelected = selectedWord
      ? normalizeForMatch(selectedWord)
      : null;

    return sourceWords.map((word, index) => {
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

      const normalizedDisplay = normalizeForMatch(displayText);
      const isSelected =
        Boolean(normalizedSelected) && normalizedSelected === normalizedDisplay;

      // Parse word for prefix visualization only if word has prefix data
      const prefixSegments = word.prefixes?.length
        ? getPrefixSegments(displayText, word.prefixes)
        : null;

      if (index === 0 && showOnboardingHint && !variantText) {
        return (
          <span key={word.position}>
            <OnboardingWordHint
              word={displayText}
              isActive={showOnboardingHint}
              onClick={() => onWordClick(word)}
            />
            {index < sourceWords.length - 1 && " "}
          </span>
        );
      }

      return (
        <span key={word.position}>
          <span
            onClick={() => onWordClick(word)}
            className={`cursor-pointer transition-colors ${isSelected ? "verse-highlight" : ""}`}
            style={
              variantText ? { color: "var(--copper-highlight)" } : undefined
            }
          >
            {prefixSegments?.prefixes?.length ? (
              <>
                <span
                  style={{ color: "var(--text-secondary)" }}
                  className="cursor-pointer hover:opacity-80"
                  title={t("verse.prefixLabel", {
                    prefix: word.prefixes?.join(", ") ?? "",
                  })}
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
          {index < sourceWords.length - 1 && " "}
        </span>
      );
    });
  };

  // If full chapter mode is enabled and we have verses, show the full chapter view
  if (showFullChapter && chapterVerses && chapterVerses.length > 0) {
    return (
      <div className="transition-opacity duration-500">
        <FullChapterView
          verses={chapterVerses}
          bookName={bookName}
          bookNameHebrew={bookNameHebrew}
          chapter={chapter}
          language={language}
          hebrewOnly={hebrewOnly}
          onWordClick={onWordClick}
          showQumran={showQumran}
          selectedWord={selectedWord}
          showNikud={showNikud}
          showCantillation={showCantillation}
        />
      </div>
    );
  }

  // Otherwise show the single verse view
  return (
    <div className="space-y-10 relative">
      {/* Hebrew Text with Verse Number and Onboarding Hint - Large and Centered */}
      <div
        className="text-center leading-[2] tracking-[0.01em] relative"
        style={{
          fontFamily: "'Cardo', serif",
          fontSize: "48px",
          direction: "rtl",
          color: "var(--text-hebrew)",
          lineHeight: 1.85,
        }}
      >
        <span
          className="text-[var(--text-secondary)] opacity-50 ml-2"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: "14px",
          }}
        >
          [{verseNumber}]
        </span>
        {renderHebrewText()}
      </div>

      {/* Translation - Only show if not Hebrew Only mode */}
      {!hebrewOnly && (
        <SwipeIndicator
          onSwipeUp={onSwipeUp}
          onSwipeDown={onSwipeDown}
          label={t("navigation.swipeToNavigate")}
        >
          <div
            className="text-center leading-relaxed px-4 transition-all duration-500 text-[var(--text-primary)]"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: "17px",
            }}
          >
            {renderTranslation(translation)}
          </div>
        </SwipeIndicator>
      )}
    </div>
  );
}
