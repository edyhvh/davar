import React, { useEffect, useMemo, useState } from "react";
import { X } from "lucide-react";
import { apiRequest } from "../services/apiClient";
import {
  getPrefixSegments,
  normalizeHebrew,
  normalizeHebrewDisplay,
  splitLeadingHebrewCluster,
  stripCantillation,
  stripMeteg,
} from "../utils/hebrew";
import { useTranslation } from "../hooks/useTranslation";

interface WordInstance {
  verse: string;
  text: string;
}

interface WordCardProps {
  word: string;
  wordFromVerse?: string;
  strongNumber?: string;
  qumranWord?: string;
  qumranStrong?: string;
  qumranMeanings?: string[];
  qumranRoot?: string;
  qumranRootTransliteration?: string;
  qumranRootMeaning?: string;
  qumranCommentary?: string;
  hasQumranVariant?: boolean;
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
  isQumranLoading?: boolean;
  showNikud?: boolean;
  onClose?: () => void;
  tabResetKey?: number;
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
  strongNumber,
  qumranWord,
  qumranStrong,
  qumranMeanings = [],
  qumranRoot,
  qumranRootTransliteration,
  qumranRootMeaning,
  qumranCommentary,
  hasQumranVariant = false,
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
  isQumranLoading = false,
  showNikud = true,
  onClose,
  tabResetKey,
}: WordCardProps) {
  const { t } = useTranslation(language);
  const [activeTab, setActiveTab] = useState<
    "masoretic" | "qumran" | "instances"
  >("masoretic");
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
    qumranWord,
    qumranStrong,
    qumranMeanings,
    qumranRoot,
    qumranRootTransliteration,
    qumranRootMeaning,
    qumranCommentary,
  });
  const headerWord =
    activeTab === "qumran" && displayedData.qumranWord
      ? displayedData.qumranWord
      : displayedData.word;
  const displayWord = showNikud
    ? normalizeHebrewDisplay(stripMeteg(stripCantillation(headerWord)))
    : normalizeHebrewDisplay(normalizeHebrew(headerWord));
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

  const hasRootInfo = Boolean(
    displayedData.root ||
      displayedData.rootTransliteration ||
      displayedData.rootMeaning,
  );
  const hasQumranRootInfo = Boolean(
    displayedData.qumranRoot ||
      displayedData.qumranRootTransliteration ||
      displayedData.qumranRootMeaning,
  );
  const showQumranTab = hasQumranVariant;
  const isQumranTab = showQumranTab && activeTab === "qumran";
  const activeStrongNumber = isQumranTab
    ? displayedData.qumranStrong
    : strongNumber;
  const masoreticWordFontSize = "64px";
  const qumranWordFontSize = "70px";

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
      displayedData.rootMeaning !== rootMeaning ||
      displayedData.rootTransliteration !== rootTransliteration ||
      displayedData.meanings.join("|") !== meanings.join("|") ||
      (displayedData.qumranMeanings ?? []).join("|") !==
        (qumranMeanings ?? []).join("|") ||
      displayedData.qumranWord !== qumranWord ||
      displayedData.qumranStrong !== qumranStrong ||
      displayedData.qumranRoot !== qumranRoot ||
      displayedData.qumranRootMeaning !== qumranRootMeaning ||
      displayedData.qumranRootTransliteration !== qumranRootTransliteration ||
      displayedData.qumranCommentary !== qumranCommentary ||
      (displayedData.prefixes ?? []).join("|") !==
        (prefixes ?? []).join("|") ||
      displayedData.instances.map((item) => `${item.verse}:${item.text}`).join("|") !==
        instances.map((item) => `${item.verse}:${item.text}`).join("|");

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
          qumranWord,
          qumranStrong,
          qumranMeanings,
          qumranRoot,
          qumranRootTransliteration,
          qumranRootMeaning,
          qumranCommentary,
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
        qumranWord,
        qumranStrong,
        qumranMeanings,
        qumranRoot,
        qumranRootTransliteration,
        qumranRootMeaning,
        qumranCommentary,
      });
    }
  }, [
    displayedData.root,
    displayedData.rootMeaning,
    displayedData.transliteration,
    displayedData.word,
    displayedData.wordFromVerse,
    displayedData.qumranWord,
    displayedData.qumranStrong,
    displayedData.qumranRoot,
    displayedData.qumranRootMeaning,
    displayedData.qumranRootTransliteration,
    displayedData.qumranCommentary,
    instances,
    isLoading,
    meanings,
    qumranMeanings,
    prefixes,
    root,
    rootMeaning,
    rootTransliteration,
    transliteration,
    word,
    wordFromVerse,
    qumranWord,
    qumranStrong,
    qumranRoot,
    qumranRootMeaning,
    qumranRootTransliteration,
    qumranCommentary,
  ]);

  useEffect(() => {
    if (tabResetKey === undefined) return;
    setActiveTab("masoretic");
  }, [tabResetKey]);

  useEffect(() => {
    if (!hasQumranVariant && activeTab === "qumran") {
      setActiveTab("masoretic");
    }
  }, [activeTab, hasQumranVariant]);

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
            aria-label={t("wordCard.close")}
          >
            <X className="w-4 h-4 text-[var(--text-secondary)]" />
          </button>
        )}
      </div>

      {/* Word - Large centered */}
      <div className="text-center space-y-2 pb-6">
        <div
          style={{
            fontFamily: isQumranTab
              ? "'DeadSeaScrolls-Regular', 'Cardo', serif"
              : "'Cardo', serif",
            fontSize: isQumranTab ? qumranWordFontSize : masoreticWordFontSize,
            direction: "rtl",
            lineHeight: 1.8,
            letterSpacing: "0.05em",
            fontWeight: 400,
            wordSpacing: "0.1em",
          }}
        >
          {prefixSegments.prefixes.length > 0 && !isQumranTab ? (
            <>
              <span style={{ color: "var(--text-secondary)" }}>
                {normalizeHebrewDisplay(prefixSegments.prefixes.join(""))}
              </span>
              <span style={{ color: "var(--text-hebrew)" }}>
                {normalizeHebrewDisplay(prefixSegments.root)}
              </span>
            </>
          ) : (
            <span style={{ color: "var(--text-hebrew)" }}>
              {normalizeHebrewDisplay(displayWord.replace(/\//g, ""))}
            </span>
          )}
        </div>

        {activeStrongNumber && (
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
            {activeStrongNumber}
          </div>
        )}

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
        className={`grid ${showQumranTab ? "grid-cols-3" : "grid-cols-2"} gap-2 border-2 border-[var(--primary)] rounded-full p-1`}
        style={{ overflow: "hidden" }}
      >
        {showQumranTab && (
          <button
            onClick={() => setActiveTab("qumran")}
            className="py-3 transition-all rounded-full"
            style={{
              fontFamily: "'Inter', sans-serif",
              fontWeight: 700,
              fontSize: "11px",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
              backgroundColor:
                activeTab === "qumran" ? "var(--accent-strong)" : "transparent",
              color:
                activeTab === "qumran" ? "#ffffff" : "var(--text-secondary)",
            }}
          >
            {t("wordCard.qumran")}
          </button>
        )}
        <button
          onClick={() => setActiveTab("masoretic")}
          className="py-3 transition-all rounded-full"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontWeight: 700,
            fontSize: "11px",
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            backgroundColor:
              activeTab === "masoretic"
                ? "var(--accent-strong)"
                : "transparent",
            color:
              activeTab === "masoretic" ? "#ffffff" : "var(--text-secondary)",
          }}
        >
          {showQumranTab ? t("wordCard.masoretic") : t("wordCard.meanings")}
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
          {t("wordCard.instances")}
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === "masoretic" ? (
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
              {t("wordCard.meanings")}
            </h3>
            <div
              style={{
                fontFamily: "'Jost', sans-serif",
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
                t("wordCard.noMeanings")
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
              {t("wordCard.root")}
            </h3>
            <div className="space-y-2">
              {hasRootInfo ? (
                <>
                  {displayedData.root ? (
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
                  ) : (
                    <div
                      style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: "13px",
                        color: "var(--text-secondary)",
                        textTransform: "uppercase",
                        letterSpacing: "0.12em",
                        fontWeight: 600,
                      }}
                    >
                      —
                    </div>
                  )}

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
                  <strong>{t("wordCard.alreadyRoot")}</strong>
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
                {t("wordCard.preposition")}
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
                const { head: prefixHead, tail: prefixTail } =
                  splitLeadingHebrewCluster(prefixText);

                return (
                  <div key={`${prefixId}-${index}`} className="space-y-2">
                    <div
                      style={{
                        fontFamily: "'Cardo', serif",
                        fontSize: "48px",
                        direction: "rtl",
                        lineHeight: 1,
                        fontWeight: 600,
                      }}
                    >
                      {prefixHead && (
                        <>
                          <span style={{ color: "var(--text-secondary)" }}>
                            {normalizeHebrewDisplay(prefixHead)}
                          </span>
                          {prefixTail.length > 0 && (
                            <span style={{ color: "var(--text-hebrew)" }}>
                              {normalizeHebrewDisplay(prefixTail)}
                            </span>
                          )}
                        </>
                      )}
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
                          fontFamily: "'Jost', sans-serif",
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
      ) : activeTab === "qumran" ? (
        <div className="space-y-6 text-center">
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
              {t("wordCard.meanings")}
            </h3>
            <div
              style={{
                fontFamily: "'Jost', sans-serif",
                fontSize: "18px",
                lineHeight: 1.5,
                fontWeight: 400,
              }}
              className="dark:text-[var(--text-secondary)]"
            >
              {isQumranLoading ? (
                t("wordCard.loadingDefinitions")
              ) : displayedData.qumranMeanings?.length ? (
                <div className="space-y-2 text-center">
                  {displayedData.qumranMeanings
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
                t("wordCard.noMeanings")
              )}
            </div>
          </div>

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
              {t("wordCard.commentary")}
            </h3>
            <div
              style={{
                fontFamily: "'Jost', sans-serif",
                fontSize: "15px",
                lineHeight: 1.6,
                fontWeight: 400,
              }}
              className="dark:text-[var(--text-secondary)]"
            >
              {displayedData.qumranCommentary || "—"}
            </div>
          </div>

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
              {t("wordCard.root")}
            </h3>
            <div className="space-y-2">
              {hasQumranRootInfo ? (
                <>
                  {displayedData.qumranRoot ? (
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
                        normalizeHebrew(
                          displayedData.qumranRoot,
                        ).replace(/\//g, ""),
                      )}
                    </div>
                  ) : (
                    <div
                      style={{
                        fontFamily: "'Inter', sans-serif",
                        fontSize: "13px",
                        color: "var(--text-secondary)",
                        textTransform: "uppercase",
                        letterSpacing: "0.12em",
                        fontWeight: 600,
                      }}
                    >
                      —
                    </div>
                  )}

                  {displayedData.qumranRootTransliteration && (
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
                      {displayedData.qumranRootTransliteration}
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
                    {displayedData.qumranRootMeaning
                      ? normalizeHebrewDisplay(
                          normalizeHebrew(
                            displayedData.qumranRootMeaning,
                          ).replace(/\//g, ""),
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
                  <strong>{t("wordCard.alreadyRoot")}</strong>
                </div>
              )}
            </div>
          </div>
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
              {t("wordCard.tapToNavigate")}
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
                  {t("wordCard.noInstances")}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
