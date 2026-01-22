import React, { useEffect, useMemo, useState } from "react";
import { X } from "lucide-react";
import { apiRequest } from "../services/apiClient";
import {
  getPrefixSegments,
  normalizeHebrew,
  normalizeHebrewDisplay,
  stripCantillation,
  stripMeteg,
} from "../utils/hebrew";

interface WordInstance {
  verse: string;
  text: string;
}

interface WordCardProps {
  word: string;
  wordFromVerse?: string;
  transliteration?: string;
  meanings: string[];
  root?: string;
  rootTransliteration?: string;
  rootMeaning?: string;
  prefixes?: string[];
  language?: "en" | "es" | "he";
  instances: WordInstance[];
  onInstanceClick: (verse: string) => void;
  isLoading?: boolean;
  showNikud?: boolean;
  onClose?: () => void;
}

interface PrefixEntry {
  id: string;
  main_form?: string;
  type?: string;
  transliteration_en?: string;
  transliteration_es?: string;
  meanings?: Record<string, string[]>;
  forms?: string[];
  notes?: Record<string, string>;
}

export function WordCard({
  word,
  wordFromVerse,
  transliteration,
  meanings,
  root,
  rootTransliteration,
  rootMeaning,
  prefixes,
  language = "en",
  instances,
  onInstanceClick,
  isLoading = false,
  showNikud = true,
  onClose,
}: WordCardProps) {
  const [activeTab, setActiveTab] = useState<"meanings" | "instances">(
    "meanings",
  );
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [displayedData, setDisplayedData] = useState({
    word,
    wordFromVerse,
    transliteration,
    meanings,
    root,
    rootTransliteration,
    rootMeaning,
    prefixes,
    instances,
  });
  const displayWord = showNikud
    ? normalizeHebrewDisplay(stripMeteg(stripCantillation(displayedData.word)))
    : normalizeHebrewDisplay(normalizeHebrew(displayedData.word));
  const [prefixEntries, setPrefixEntries] = useState<
    Record<string, PrefixEntry | null>
  >({});

  const formatMeaning = (text: string) => {
    const cleaned = stripMeteg(stripCantillation(text))
      .replace(/^[-–—]\s*/, "")
      .trim();
    if (!cleaned) return cleaned;
    return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
  };

  const prefixSegments = useMemo(() => {
    if (!displayedData.wordFromVerse || !displayedData.prefixes?.length) {
      return { prefixes: [], root: displayedData.wordFromVerse ?? "" };
    }
    let displayBase = normalizeHebrewDisplay(
      stripMeteg(stripCantillation(displayedData.wordFromVerse)),
    );
    if (!showNikud) {
      displayBase = normalizeHebrew(displayBase);
    }
    return getPrefixSegments(displayBase, displayedData.prefixes);
  }, [displayedData.prefixes, displayedData.wordFromVerse, showNikud]);

  useEffect(() => {
    const loadPrefixes = async () => {
      if (!displayedData.prefixes?.length) {
        setPrefixEntries({});
        return;
      }

      const entries: Record<string, PrefixEntry | null> = {};
      await Promise.all(
        displayedData.prefixes.map(async (prefixId) => {
          try {
            const entry = await apiRequest<PrefixEntry>(
              `/api/v1/prefixes/${prefixId}`,
            );
            entries[prefixId] = entry;
          } catch {
            entries[prefixId] = null;
          }
        }),
      );

      setPrefixEntries(entries);
    };

    loadPrefixes();
  }, [displayedData.prefixes]);

  useEffect(() => {
    const hasChanged =
      displayedData.word !== word ||
      displayedData.wordFromVerse !== wordFromVerse ||
      displayedData.transliteration !== transliteration ||
      displayedData.root !== root ||
      displayedData.rootMeaning !== rootMeaning;

    if (!hasChanged) return undefined;

    if (isLoading) {
      // Only transition when loading new word analysis
      setIsTransitioning(true);
      const timeout = window.setTimeout(() => {
        setDisplayedData({
          word,
          wordFromVerse,
          transliteration,
          meanings,
          root,
          rootTransliteration,
          rootMeaning,
          prefixes,
          instances,
        });
        setIsTransitioning(false);
      }, 140);
      return () => window.clearTimeout(timeout);
    } else {
      // Update immediately without transition for word switching
      setDisplayedData({
        word,
        wordFromVerse,
        transliteration,
        meanings,
        root,
        rootTransliteration,
        rootMeaning,
        prefixes,
        instances,
      });
    }
  }, [
    displayedData.root,
    displayedData.rootMeaning,
    displayedData.transliteration,
    displayedData.word,
    displayedData.wordFromVerse,
    instances,
    isLoading,
    meanings,
    prefixes,
    root,
    rootMeaning,
    rootTransliteration,
    transliteration,
    word,
    wordFromVerse,
  ]);

  return (
    <div
      className="space-y-6 py-2"
      style={{
        opacity: isTransitioning ? 0.8 : 1,
        transition: "opacity 160ms ease",
      }}
    >
      <div className="flex justify-end">
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-full p-2 transition-all hover:scale-105 active:scale-95"
            style={{
              backgroundColor: "var(--neomorph-bg)",
              border: "1px solid var(--neomorph-border)",
              boxShadow:
                "6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)",
            }}
            aria-label="Close word meaning"
          >
            <X className="w-4 h-4 text-[var(--text-secondary)]" />
          </button>
        )}
      </div>

      {/* Word - Large centered */}
      <div className="text-center space-y-2 pb-6">
        <div
          style={{
            fontFamily: "'Cardo', serif",
            fontSize: "64px",
            direction: "rtl",
            lineHeight: 1.8,
            letterSpacing: "0.05em",
            color: "var(--text-hebrew)",
            fontWeight: 400,
            wordSpacing: "0.1em",
          }}
        >
          {normalizeHebrewDisplay(displayWord.replace(/\//g, ""))}
        </div>

        {/* Transliteration */}
        {displayedData.transliteration && (
          <div
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: "11px",
              color: "var(--text-secondary)",
              textTransform: "uppercase",
              letterSpacing: "0.15em",
              fontWeight: 500,
              marginTop: "12px",
            }}
          >
            {displayedData.transliteration}
          </div>
        )}
      </div>

      {/* Segmented Control - Pill style with border */}
      <div
        className="grid grid-cols-2 gap-2 border-2 border-[var(--primary)] rounded-full p-1"
        style={{ overflow: "hidden" }}
      >
        <button
          onClick={() => setActiveTab("meanings")}
          className="py-3 transition-all rounded-full"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 700,
            fontSize: "11px",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            backgroundColor:
              activeTab === "meanings" ? "var(--accent-strong)" : "transparent",
            color:
              activeTab === "meanings" ? "#ffffff" : "var(--text-secondary)",
          }}
        >
          Meanings
        </button>
        <button
          onClick={() => setActiveTab("instances")}
          className="py-3 transition-all rounded-full"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 700,
            fontSize: "11px",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            backgroundColor:
              activeTab === "instances"
                ? "var(--accent-strong)"
                : "transparent",
            color:
              activeTab === "instances" ? "#ffffff" : "var(--text-secondary)",
          }}
        >
          Instances
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === "meanings" ? (
        <div className="space-y-6 text-center">
          {/* Meanings Section */}
          <div className="pb-6">
            <h3
              className="mb-4"
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: "11px",
                color: "var(--text-secondary)",
                fontWeight: 700,
                letterSpacing: "0.15em",
                textTransform: "uppercase",
              }}
            >
              Meanings
            </h3>
            <div
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: "18px",
                lineHeight: 1.5,
                fontWeight: 400,
              }}
              className="dark:text-[var(--text-secondary)]"
            >
              {displayedData.meanings.length > 0 ? (
                <div className="space-y-2 text-center">
                  {displayedData.meanings
                    .flatMap((m) =>
                      m ? m.split(/[,;]\s*/).map((s) => s.trim()) : [],
                    )
                    .map((m, i) => (
                      <div key={i} style={{ whiteSpace: "normal" }}>
                        {formatMeaning(m).replace(/\//g, "")}
                      </div>
                    ))}
                </div>
              ) : (
                "No meanings available yet."
              )}
            </div>
          </div>

          {/* Root Section */}
          {/* Root Section — always show; if no root, show ALREADY ROOT */}
          <div className="pb-6">
            <h3
              className="mb-4"
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: "11px",
                color: "var(--text-secondary)",
                fontWeight: 700,
                letterSpacing: "0.15em",
                textTransform: "uppercase",
              }}
            >
              Root
            </h3>
            <div className="space-y-2">
              {displayedData.root ? (
                <>
                  <div
                    style={{
                      fontFamily: "'Cardo', serif",
                      fontSize: "48px",
                      direction: "rtl",
                      color: "var(--primary)",
                      fontWeight: 600,
                      lineHeight: 1.4,
                    }}
                  >
                    {normalizeHebrewDisplay(
                      normalizeHebrew(displayedData.root).replace(/\//g, ""),
                    )}
                  </div>

                  {displayedData.rootTransliteration && (
                    <div
                      style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: "11px",
                        color: "var(--text-secondary)",
                        textTransform: "uppercase",
                        letterSpacing: "0.12em",
                        fontWeight: 500,
                        marginTop: "8px",
                      }}
                    >
                      {displayedData.rootTransliteration}
                    </div>
                  )}

                  <div
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: "15px",
                      lineHeight: 1.5,
                      marginTop: "12px",
                    }}
                    className="dark:text-[var(--text-secondary)]"
                  >
                    {displayedData.rootMeaning
                      ? normalizeHebrewDisplay(
                          normalizeHebrew(displayedData.rootMeaning).replace(
                            /\//g,
                            "",
                          ),
                        )
                      : "—"}
                  </div>
                </>
              ) : (
                <div
                  style={{
                    fontFamily: "'Inter', sans-serif",
                    lineHeight: 1.5,
                    textAlign: "center",
                  }}
                  className="dark:text-[var(--text-secondary)]"
                >
                  <strong>ALREADY ROOT</strong>
                </div>
              )}
            </div>
          </div>

          {displayedData.prefixes?.length ? (
            <div className="text-center space-y-4 pb-6">
              <h3
                className="mb-2"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  fontSize: "11px",
                  color: "var(--text-secondary)",
                  fontWeight: 700,
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                }}
              >
                Preposition
              </h3>
              {displayedData.prefixes.map((prefixId, index) => {
                const entry = prefixEntries[prefixId];
                const meanings =
                  entry?.meanings?.[language] ??
                  entry?.meanings?.en ??
                  entry?.meanings?.es ??
                  [];
                const translit =
                  language === "es"
                    ? entry?.transliteration_es
                    : (entry?.transliteration_en ?? entry?.transliteration_es);
                const prefixText = stripMeteg(
                  prefixSegments.prefixes[index]?.replace(/\//g, "") ??
                    entry?.main_form ??
                    "",
                );

                return (
                  <div key={`${prefixId}-${index}`} className="space-y-2">
                    <div
                      style={{
                        fontFamily: "'Cardo', serif",
                        fontSize: "48px",
                        direction: "rtl",
                        lineHeight: 1,
                        color: "var(--text-secondary)",
                        fontWeight: 600,
                      }}
                    >
                      {normalizeHebrewDisplay(prefixText)}
                    </div>
                    {translit ? (
                      <div
                        style={{
                          fontFamily: "'Inter', sans-serif",
                          fontSize: "11px",
                          color: "var(--text-secondary)",
                          textTransform: "uppercase",
                          letterSpacing: "0.15em",
                          fontWeight: 500,
                        }}
                      >
                        {translit}
                      </div>
                    ) : null}
                    {meanings.length ? (
                      <div
                        style={{
                          fontFamily: "'Inter', sans-serif",
                          fontSize: "15px",
                          lineHeight: 1.5,
                        }}
                        className="dark:text-[var(--text-secondary)]"
                      >
                        {meanings.join(", ")}
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
          ) : null}
        </div>
      ) : (
        <div className="space-y-6 text-center pb-6">
          {/* Instances Section */}
          <div className="pb-6">
            <h3
              className="mb-4"
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: "11px",
                color: "var(--text-secondary)",
                fontWeight: 700,
                letterSpacing: "0.15em",
                textTransform: "uppercase",
              }}
            >
              Tap to Navigate
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {displayedData.instances.length > 0 ? (
                displayedData.instances.map((instance, idx) => (
                  <button
                    key={idx}
                    onClick={() => onInstanceClick(instance.verse)}
                    className="py-4 transition-all hover:bg-[var(--primary)] hover:text-white rounded-[20px]"
                    style={{
                      backgroundColor: "var(--muted)",
                      fontFamily: "'Inter', sans-serif",
                      fontSize: "13px",
                      fontWeight: 600,
                      color: "var(--foreground)",
                    }}
                  >
                    {instance.verse}
                  </button>
                ))
              ) : (
                <div
                  className="col-span-3 text-sm text-[var(--text-secondary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  No instances available yet.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
