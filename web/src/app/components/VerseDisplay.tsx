import React from "react";
import { OnboardingWordHint } from "./OnboardingWordHint";
import { SwipeIndicator } from "./SwipeIndicator";
import { FullChapterView } from "./FullChapterView";
import type {
  DssVariant,
  VerseResponse,
  WordResponse,
  TranslationFootnote,
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
  seferMode?: boolean;
  hebrewOnly?: boolean;
  showNikud?: boolean;
  showCantillation?: boolean;
  chapterVerses?: VerseResponse[];
  words: WordResponse[];
  dssVariants?: DssVariant[];
  selectedWord?: string | null;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  translation_footnotes?: TranslationFootnote[];
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
  seferMode = false,
  hebrewOnly = false,
  showNikud = true,
  showCantillation = false,
  chapterVerses,
  words,
  dssVariants,
  selectedWord,
  onSwipeUp,
  onSwipeDown,
  translation_footnotes,
}: VerseDisplayProps) {
  const { t } = useTranslation(language);
  const spanishMissingTranslation = t("verse.missingSpanishTranslation");
  const dssInlineFontScale = "1.70em";
  const dssInlineBaselineShift = "-0.08em";
  // Function to render Hebrew text with DSS variants
  const renderHebrewText = () => {
    const dssMap = new Map<number, string>();
    dssVariants?.forEach((variant) => {
      dssMap.set(variant.position, variant.dss_word);
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

      // Always compare against the original Masoretic word text, not the
      // display text which may be a DSS variant.
      const normalizedWord = normalizeForMatch(word.text);
      const isSelected =
        Boolean(normalizedSelected) && normalizedSelected === normalizedWord;

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
              variantText
                ? {
                    color: "var(--qumran-text)",
                    fontFamily: "'DeadSeaScrolls-Regular', 'Cardo', serif",
                    fontSize: dssInlineFontScale,
                    display: "inline-block",
                    verticalAlign: "middle",
                    transform: `translateY(${dssInlineBaselineShift})`,
                  }
                : undefined
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
          seferMode={seferMode}
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
            {language === "es" && !translation.trim()
              ? spanishMissingTranslation
              : renderTranslation(translation, {
                  hideSuperscripts: !!translation_footnotes?.length,
                })}
          </div>
        </SwipeIndicator>
      )}
    </div>
  );
}
