import React from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
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
  removeMaqafForDisplay,
  removeSofPasukForDisplay,
} from "../utils/hebrew";
import { renderTranslation } from "../utils/translationFormatter";
import { useTranslation } from "../hooks/useTranslation";
import {
  shouldHideSuperscripts,
  getTranslationKey,
} from "../utils/translationConfig";

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
  canNavigatePrevious?: boolean;
  canNavigateNext?: boolean;
  translation_footnotes?: TranslationFootnote[];
  isBesorah?: boolean;
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
  canNavigatePrevious = false,
  canNavigateNext = false,
  translation_footnotes,
  isBesorah = false,
}: VerseDisplayProps) {
  const { t } = useTranslation(language);
  const spanishMissingTranslation = t("verse.missingSpanishTranslation");
  const hideSuperscripts = shouldHideSuperscripts(getTranslationKey(language));
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
        : removeMaqafForDisplay(hebrewText)
            .split(" ")
            .filter(Boolean)
            .map((word, index) => ({
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
      normalized = normalized.replace(/\//g, "");
      return normalized.replace(/\u05BE/g, "");
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
      displayText = removeMaqafForDisplay(displayText);
      if (isBesorah) {
        displayText = removeSofPasukForDisplay(displayText);
      }

      // Always compare against the original Masoretic word text, not the
      // display text which may be a DSS variant.
      const normalizedWord = normalizeForMatch(word.text);
      const isSelected =
        Boolean(normalizedSelected) && normalizedSelected === normalizedWord;

      // Parse word for prefix visualization only if word has prefix data
      const prefixSegments = word.prefixes?.length
        ? getPrefixSegments(displayText, word.prefixes)
        : null;

      const shouldShowHintButton =
        showOnboardingHint &&
        !variantText &&
        (isSelected || (!normalizedSelected && index === 0));

      if (shouldShowHintButton) {
        return (
          <span key={word.position}>
            <OnboardingWordHint
              word={displayText}
              isActive={showOnboardingHint}
              isPressed={isSelected}
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
            className={`word-interactive cursor-pointer ${isSelected ? "verse-highlight" : ""}`}
            style={
              variantText
                ? {
                    color: "var(--text-hebrew)",
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
          isBesorah={isBesorah}
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
          wordSpacing: "0.24em",
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
        <SwipeIndicator>
          <div
            className="text-center leading-relaxed px-4 transition-all duration-500 text-[var(--text-primary)]"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: "17px",
            }}
          >
            {language === "es" && !translation.trim()
              ? spanishMissingTranslation
              : renderTranslation(translation || "", {
                  hideSuperscripts,
                })}
          </div>
        </SwipeIndicator>
      )}

      {(canNavigatePrevious || canNavigateNext) && (
        <div
          className={`md:hidden flex items-center justify-center gap-3 px-4 ${hebrewOnly ? "mt-8" : "mt-4"}`}
        >
          {canNavigatePrevious && (
            <button
              type="button"
              onClick={onSwipeUp}
              aria-label={t("verse.previousVerse")}
              className="inline-flex items-center gap-1.5 rounded-full border px-3 py-2 text-[12px] font-medium transition-colors"
              style={{
                background: "var(--neomorph-bg)",
                borderColor: "var(--neomorph-border)",
                color: "var(--text-secondary)",
                boxShadow:
                  "2px 2px 6px var(--neomorph-shadow-dark), -2px -2px 6px var(--neomorph-shadow-light)",
                minHeight: "36px",
              }}
            >
              <ChevronUp size={14} strokeWidth={2.25} aria-hidden="true" />
              <span>{t("verse.previousVerse")}</span>
            </button>
          )}

          {canNavigateNext && (
            <button
              type="button"
              onClick={onSwipeDown}
              aria-label={t("verse.nextVerse")}
              className="inline-flex items-center gap-1.5 rounded-full border px-3 py-2 text-[12px] font-medium transition-colors"
              style={{
                background: "var(--neomorph-bg)",
                borderColor: "var(--neomorph-border)",
                color: "var(--text-secondary)",
                boxShadow:
                  "2px 2px 6px var(--neomorph-shadow-dark), -2px -2px 6px var(--neomorph-shadow-light)",
                minHeight: "36px",
              }}
            >
              <ChevronDown size={14} strokeWidth={2.25} aria-hidden="true" />
              <span>{t("verse.nextVerse")}</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
