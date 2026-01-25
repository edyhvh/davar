import React, {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import BottomSheet, {
  BottomSheetBackdrop,
  BottomSheetScrollView,
  type BottomSheetBackdropProps,
} from "@gorhom/bottom-sheet";
import { router } from "expo-router";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import type { DisplayWord } from "@/src/services/scripture";
import {
  stripCantillation,
  stripNikud,
  getPrefixSegments,
  stripMeteg,
  normalizeHebrewDisplay,
} from "@/src/utils/hebrew";
import { apiRequest } from "@/src/services/api";
import type { LexiconResponse } from "@/src/types/api";

type PrefixResponse = {
  id: string;
  main_form?: string;
  type?: string;
  transliteration_en?: string;
  transliteration_es?: string;
  meanings?: Record<string, string[]>;
  forms?: string[];
  notes?: Record<string, string>;
};

type WordAnalysisBottomSheetProps = {
  sheetRef: React.RefObject<BottomSheet | null>;
  currentVerseId?: string;
  word?:
    | (DisplayWord & {
        meanings?: string[];
        gloss?: string;
        root?: string;
        rootTransliteration?: string;
        rootMeaning?: string;
        instances?: { verse: string; text: string }[];
        strong?: string;
        translit_en?: string;
        translit_es?: string;
      })
    | null;
  // Called after the sheet has fully closed and any exit animations have completed
  onClosed?: () => void;
};

type TabType = "meanings" | "instances";

const createStyles = (
  colors: ReturnType<typeof getColors>,
  hebrewScale: number,
) =>
  StyleSheet.create({
    content: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[2],
      paddingBottom: spacing[8],
    },
    sheetBackground: {
      backgroundColor: colors.surface,
      borderTopLeftRadius: radii.xl,
      borderTopRightRadius: radii.xl,
    },
    sheetHandle: {
      backgroundColor: colors.border,
    },
    headerSection: {
      alignItems: "center",
      marginBottom: spacing[6],
    },
    hebrew: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: 48 * hebrewScale,
      color: colors.textPrimary,
      textAlign: "center",
      writingDirection: "rtl",
      lineHeight: 72 * hebrewScale,
    },
    transliteration: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      textTransform: "uppercase",
      letterSpacing: 2,
      marginTop: spacing[1],
    },
    occurrencesText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      color: colors.textSecondary,
      textAlign: "center",
      marginTop: spacing[1],
    },
    toggleContainer: {
      flexDirection: "row",
      backgroundColor: colors.background,
      borderRadius: radii.full,
      padding: 4,
      marginBottom: spacing[6],
      borderWidth: 1,
      borderColor: colors.border,
    },
    toggleButton: {
      flex: 1,
      paddingVertical: spacing[3],
      paddingHorizontal: spacing[4],
      borderRadius: radii.full,
      alignItems: "center",
    },
    toggleButtonActive: {
      backgroundColor: colors.primary,
    },
    toggleText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      fontWeight: "600",
      textTransform: "uppercase",
      letterSpacing: 1,
    },
    toggleTextActive: {
      color: colors.surface,
    },
    sectionLabel: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      color: colors.textSecondary,
      textTransform: "uppercase",
      letterSpacing: 1.5,
      textAlign: "center",
      marginBottom: spacing[3],
    },
    meaningsText: {
      fontFamily: typography.families.latinMeaning,
      fontSize: typography.sizes.h3,
      color: colors.textPrimary,
      textAlign: "center",
      lineHeight: 28,
    },
    meaningsList: {
      alignItems: "center",
      marginBottom: spacing[4],
    },
    meaningsBullet: {
      fontFamily: typography.families.latinMeaning,
      fontSize: typography.sizes.h3,
      color: colors.textPrimary,
      textAlign: "center",
      lineHeight: 28,
      marginBottom: spacing[2],
    },
    rootSection: {
      marginTop: spacing[8],
      alignItems: "center",
    },
    rootHebrew: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: 40 * hebrewScale,
      color: colors.primary,
      textAlign: "center",
      writingDirection: "rtl",
      lineHeight: 56 * hebrewScale,
    },
    rootTransliteration: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      textTransform: "uppercase",
      letterSpacing: 2,
      marginTop: spacing[1],
    },
    rootMeaning: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      textAlign: "center",
      marginTop: spacing[2],
    },
    instancesContainer: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: spacing[2],
    },
    instancePill: {
      flexDirection: "row",
      alignItems: "center",
      paddingVertical: spacing[2],
      paddingHorizontal: spacing[3],
      borderRadius: radii.full,
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    instancePillPressed: {
      backgroundColor: colors.primaryLight,
      borderColor: colors.primary,
    },
    instanceRef: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textPrimary,
      fontWeight: "500",
    },
    showMoreButton: {
      paddingVertical: spacing[2],
      paddingHorizontal: spacing[3],
      borderRadius: radii.full,
      backgroundColor: colors.background,
      borderWidth: 1,
      borderColor: colors.border,
      alignItems: "center",
    },
    showMoreText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.primary,
      fontWeight: "600",
    },
    emptyText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textSecondary,
      textAlign: "center",
      fontStyle: "italic",
    },
    prefixesSection: {
      marginTop: spacing[6],
      alignItems: "center",
    },
    prefixItem: {
      alignItems: "center",
      marginBottom: spacing[4],
    },
    prefixHebrew: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: 40 * hebrewScale,
      color: colors.textSecondary,
      textAlign: "center",
      writingDirection: "rtl",
      lineHeight: 56 * hebrewScale,
    },
    prefixTransliteration: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      textTransform: "uppercase",
      letterSpacing: 2,
      marginTop: spacing[1],
    },
    prefixMeaning: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      textAlign: "center",
      marginTop: spacing[2],
    },
    prefixText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      textAlign: "center",
      marginTop: spacing[1],
    },
  });

// Map of book abbreviations to book IDs
const bookAbbreviations: Record<string, string> = {
  Gen: "genesis",
  Exod: "exodus",
  Ex: "exodus",
  Lev: "leviticus",
  Num: "numbers",
  Deut: "deuteronomy",
  Josh: "joshua",
  Judg: "judges",
  Ruth: "ruth",
  "1Sam": "samuel1",
  "2Sam": "samuel2",
  "1Kgs": "kings1",
  "2Kgs": "kings2",
  "1Chr": "chronicles1",
  "2Chr": "chronicles2",
  Ezra: "ezra",
  Neh: "nehemiah",
  Esth: "esther",
  Job: "job",
  Ps: "psalms",
  Prov: "proverbs",
  Eccl: "ecclesiastes",
  Song: "songofsolomon",
  Isa: "isaiah",
  Jer: "jeremiah",
  Lam: "lamentations",
  Ezek: "ezekiel",
  Dan: "daniel",
  Hos: "hosea",
  Joel: "joel",
  Amos: "amos",
  Obad: "obadiah",
  Jonah: "jonah",
  Mic: "micah",
  Nah: "nahum",
  Hab: "habakkuk",
  Zeph: "zephaniah",
  Hag: "haggai",
  Zech: "zechariah",
  Mal: "malachi",
  Matt: "matthew",
  Mark: "mark",
  Luke: "luke",
  John: "john",
  Acts: "acts",
  Rom: "romans",
  "1Cor": "corinthians1",
  "2Cor": "corinthians2",
  Gal: "galatians",
  Eph: "ephesians",
  Phil: "philippians",
  Col: "colossians",
  "1Thess": "thessalonians1",
  "2Thess": "thessalonians2",
  "1Tim": "timothy1",
  "2Tim": "timothy2",
  Titus: "titus",
  Phlm: "philemon",
  Heb: "hebrews",
  Jas: "james",
  "1Pet": "peter1",
  "2Pet": "peter2",
  "1John": "john1",
  "2John": "john2",
  "3John": "john3",
  Jude: "jude",
  Rev: "revelation",
};

// Parse verse reference like "Gen 1:1" to verse ID like "genesis-1-1"
const parseVerseReference = (ref: string): string | null => {
  // Match patterns like "Gen 1:1", "1Sam 2:3", "Ps 119:105"
  const match = ref.match(/^(\d?\w+)\s+(\d+):(\d+)/);
  if (!match) return null;

  const [, bookAbbr, chapter, verse] = match;
  const bookId = bookAbbreviations[bookAbbr];
  if (!bookId) return null;

  return `${bookId}-${chapter}-${verse}`;
};

export const WordAnalysisBottomSheet = ({
  sheetRef,
  word,
  currentVerseId,
  onClosed,
}: WordAnalysisBottomSheetProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const hebrewFontScale = useAppStore(
    (state: AppState) => state.hebrewFontScale,
  );
  const language = useAppStore((state: AppState) => state.language);
  const colors = getColors(themeMode);
  const styles = useMemo(
    () => createStyles(colors, hebrewFontScale),
    [colors, hebrewFontScale],
  );
  const [activeTab, setActiveTab] = useState<TabType>("meanings");
  const [lexiconEntry, setLexiconEntry] = useState<LexiconResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [showAllInstances, setShowAllInstances] = useState(false);
  const [prefixEntries, setPrefixEntries] = useState<
    Record<string, PrefixResponse | null>
  >({});
  const showNikud = useAppStore((state: AppState) => state.showNikud);
  const showCantillation = useAppStore(
    (state: AppState) => state.showCantillation,
  );
  // Keep in sync with web/src/app/App.tsx transliteration selection logic.
  const wordTransliteration =
    language === "en"
      ? word?.translit_en
      : language === "es"
        ? word?.translit_es
        : undefined;

  const strongNumber = useMemo(() => {
    if (!word?.strong) return null;
    const parts = word.strong.split("/").map((part) => part.trim());
    const strongPart = parts.find((part) => /^[HG]\d+$/.test(part));
    return strongPart ?? null;
  }, [word?.strong]);

  const displayHebrew = useMemo(() => {
    let base = word?.text ?? lexiconEntry?.hebrew ?? "—";
    if (!showNikud) {
      base = stripNikud(base);
    }
    if (!showCantillation) {
      base = stripCantillation(base);
    }
    base = stripMeteg(base);
    return normalizeHebrewDisplay(base).replace(/\//g, "");
  }, [lexiconEntry?.hebrew, word?.text, showNikud, showCantillation]);

  const prefixSegments = useMemo(() => {
    if (!word?.text || !word?.prefixes?.length) {
      return { prefixes: [], root: word?.text ?? "" };
    }
    let displayBase = normalizeHebrewDisplay(
      stripMeteg(stripCantillation(word.text)),
    );
    if (!showNikud) {
      displayBase = stripNikud(displayBase);
    }
    return getPrefixSegments(displayBase, word.prefixes);
  }, [showNikud, word?.text, word?.prefixes]);

  useEffect(() => {
    const loadLexicon = async () => {
      if (!strongNumber) {
        setLexiconEntry(null);
        return;
      }
      setIsLoading(true);
      try {
        const params = new URLSearchParams();
        if (language !== "he") {
          params.set("language", language);
        }
        if (word?.text) {
          params.set("hebrew", word.text);
        }
        const query = params.toString();
        const url = query
          ? `/api/v1/lexicon/${strongNumber}?${query}`
          : `/api/v1/lexicon/${strongNumber}`;
        const entry = await apiRequest<LexiconResponse>(url);
        setLexiconEntry(entry);
        console.debug(
          "WordAnalysisBottomSheet: lexicon loaded",
          strongNumber,
          entry?.hebrew ?? entry?.root_strong ?? null,
        );
      } catch {
        setLexiconEntry(null);
        console.debug(
          "WordAnalysisBottomSheet: lexicon fetch failed",
          strongNumber,
        );
      } finally {
        setIsLoading(false);
      }
    };
    loadLexicon();
  }, [strongNumber, language, word?.text]);

  useEffect(() => {
    // Reset to meanings tab when a new word is selected
    setActiveTab("meanings");
    setShowAllInstances(false);
  }, [word?.strong]);

  useEffect(() => {
    const loadPrefixes = async () => {
      if (!word?.prefixes?.length) {
        setPrefixEntries({});
        return;
      }

      const entries: Record<string, PrefixResponse | null> = {};
      await Promise.all(
        word.prefixes.map(async (prefixId) => {
          try {
            const entry = await apiRequest<PrefixResponse>(
              `/api/v1/prefixes/${prefixId}`,
            );
            entries[prefixId] = entry;
          } catch {
            entries[prefixId] = null;
          }
        }),
      );

      setPrefixEntries(entries);
      console.debug(
        "WordAnalysisBottomSheet: loaded prefixes",
        Object.keys(entries),
      );
    };

    loadPrefixes();
  }, [word?.prefixes]);

  useEffect(() => {
    // Clear lexicon and prefix entries when the current verse changes to avoid showing stale data
    setLexiconEntry(null);
    setPrefixEntries({});
  }, [currentVerseId]);

  const renderBackdrop = useCallback(
    (props: BottomSheetBackdropProps) => (
      <BottomSheetBackdrop
        {...props}
        appearsOnIndex={0}
        disappearsOnIndex={-1}
        opacity={0.5}
        pressBehavior="close"
      />
    ),
    [],
  );

  const handleSheetChanges = useCallback((index: number) => {
    console.debug("WordAnalysisBottomSheet onChange", { index });
  }, []);

  const handleSheetClose = useCallback(() => {
    onClosed?.();
  }, [onClosed]);

  const meaningsList = useMemo(() => {
    const normalizeForDisplay = (t: string) =>
      stripCantillation(stripNikud(t)).replace(/\//g, "").trim();

    const formatMeaning = (text: string) => {
      const cleaned = text.replace(/^[-–—]\s*/, "").trim();
      if (!cleaned) return cleaned;
      return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
    };

    let rawMeanings: string[] = [];
    if (lexiconEntry?.definitions?.length) {
      rawMeanings = lexiconEntry.definitions
        .map((item) => (item.text ? normalizeForDisplay(item.text) : ""))
        .filter(Boolean);
    } else if (!word) {
      return ["—"];
    } else if (
      word.morph?.includes("Np") ||
      (!word.meanings?.length && !word.gloss)
    ) {
      return ["Proper Name"];
    } else {
      const meanings = word.meanings?.length ? word.meanings : [word.gloss];
      // If user language is not Hebrew, prefer Latin-script meanings to avoid mixing languages
      const preferLatin = language !== "he";
      const isLatin = (s: string) => /[A-Za-zÀ-ž0-9]/.test(s);
      rawMeanings = meanings
        .map((m) => (m ? normalizeForDisplay(m) : ""))
        .filter(Boolean)
        .filter((m) => (preferLatin ? isLatin(m) : true));

      // If filtering removed all items and we have raw ones, fall back to unfiltered normalized list
      if (!rawMeanings.length && meanings) {
        rawMeanings = meanings
          .map((m) => (m ? normalizeForDisplay(m) : ""))
          .filter(Boolean);
      }
    }

    const expanded = rawMeanings.flatMap((meaning) =>
      meaning
        .split(/[,;]\s*/)
        .map((item) => item.trim())
        .filter(Boolean),
    );

    const formatted = expanded.map((item) => formatMeaning(item));
    return formatted.length ? formatted : ["—"];
  }, [lexiconEntry, word, language]);

  const isDerivedRoot = Boolean(lexiconEntry?.root_strong || word?.root);

  const rootMeaningText = useMemo(() => {
    // If this entry is itself a root, show ALREADY ROOT
    if (!isDerivedRoot) return "ALREADY ROOT";

    if (lexiconEntry?.root_definitions?.length) {
      return (
        lexiconEntry.root_definitions.map((item) => item.text).join(", ") || "—"
      );
    }
    if (!word?.rootMeaning) return "—";
    return word.rootMeaning;
  }, [lexiconEntry, word, isDerivedRoot]);

  return (
    <BottomSheet
      ref={sheetRef}
      index={-1}
      snapPoints={["50%", "80%"]}
      enablePanDownToClose
      backgroundStyle={styles.sheetBackground}
      handleIndicatorStyle={styles.sheetHandle}
      onChange={handleSheetChanges}
      onClose={handleSheetClose}
      backdropComponent={renderBackdrop}
      animateOnMount={false}
    >
      <BottomSheetScrollView style={styles.content}>
        {/* Show empty state when no word is selected */}
        {!word ? (
          <View style={styles.headerSection}>
            <Text style={styles.emptyText}>
              Select a word to see its analysis
            </Text>
          </View>
        ) : (
          <>
            {/* Header: Hebrew word + transliteration */}
            <View style={styles.headerSection}>
              <Text style={styles.hebrew}>{displayHebrew}</Text>
              {wordTransliteration ? (
                <Text style={styles.transliteration}>
                  {wordTransliteration}
                </Text>
              ) : null}
              {lexiconEntry?.occurrences_count && (
                <Text style={styles.occurrencesText}>
                  Appears {lexiconEntry.occurrences_count} times
                </Text>
              )}
            </View>

            {/* Toggle: Meanings / Instances */}
            <View style={styles.toggleContainer}>
              <Pressable
                style={[
                  styles.toggleButton,
                  activeTab === "meanings" && styles.toggleButtonActive,
                ]}
                onPress={() => setActiveTab("meanings")}
              >
                <Text
                  style={[
                    styles.toggleText,
                    activeTab === "meanings" && styles.toggleTextActive,
                  ]}
                >
                  Meanings
                </Text>
              </Pressable>
              <Pressable
                style={[
                  styles.toggleButton,
                  activeTab === "instances" && styles.toggleButtonActive,
                ]}
                onPress={() => setActiveTab("instances")}
              >
                <Text
                  style={[
                    styles.toggleText,
                    activeTab === "instances" && styles.toggleTextActive,
                  ]}
                >
                  Instances
                </Text>
              </Pressable>
            </View>

            {/* Tab Content */}
            {activeTab === "meanings" ? (
              <>
                {/* Meanings section */}
                <Text style={styles.sectionLabel}>Meanings</Text>
                {isLoading ? (
                  <Text style={styles.emptyText}>Loading definitions...</Text>
                ) : null}
                <View style={styles.meaningsList}>
                  {meaningsList.map((meaning, index) => (
                    <Text
                      key={`${meaning}-${index}`}
                      style={styles.meaningsBullet}
                    >
                      • {meaning}
                    </Text>
                  ))}
                </View>

                {/* Root section */}
                {word || lexiconEntry ? (
                  <View style={styles.rootSection}>
                    <Text style={styles.sectionLabel}>Root</Text>
                    <Text style={styles.rootHebrew}>
                      {(
                        lexiconEntry?.root ??
                        word?.root ??
                        displayHebrew
                      ).replace(/\//g, "")}
                    </Text>
                    {lexiconEntry?.root_strong || word?.rootTransliteration ? (
                      <Text style={styles.rootTransliteration}>
                        {lexiconEntry?.root_strong ?? word?.rootTransliteration}
                      </Text>
                    ) : null}
                    <Text style={styles.rootMeaning}>
                      {lexiconEntry?.root || word?.root
                        ? rootMeaningText
                        : "ALREADY ROOT"}
                    </Text>
                  </View>
                ) : null}

                {word?.prefixes?.length ? (
                  <View style={styles.prefixesSection}>
                    <Text style={styles.sectionLabel}>Preposition</Text>
                    {word.prefixes.map((prefix, index) => {
                      const entry = prefixEntries[prefix];
                      const meanings =
                        entry?.meanings?.[language] ??
                        entry?.meanings?.en ??
                        entry?.meanings?.es ??
                        [];
                      const transliteration =
                        language === "es"
                          ? entry?.transliteration_es
                          : (entry?.transliteration_en ??
                            entry?.transliteration_es);
                      const prefixText =
                        prefixSegments.prefixes[index]?.replace(/\//g, "") ??
                        entry?.main_form ??
                        "";

                      return (
                        <View
                          key={`${prefix}-${index}`}
                          style={styles.prefixItem}
                        >
                          <Text style={styles.prefixHebrew}>{prefixText}</Text>
                          {transliteration ? (
                            <Text style={styles.prefixTransliteration}>
                              {transliteration}
                            </Text>
                          ) : null}
                          {meanings.length ? (
                            <Text style={styles.prefixMeaning}>
                              {meanings.join(", ")}
                            </Text>
                          ) : null}
                        </View>
                      );
                    })}
                  </View>
                ) : null}
              </>
            ) : (
              <>
                {/* Instances section */}
                <Text style={styles.sectionLabel}>Appears In</Text>
                {lexiconEntry?.instances?.length || word?.instances?.length ? (
                  <View style={styles.instancesContainer}>
                    {(
                      (lexiconEntry?.instances ?? word?.instances ?? []) as (
                        | string
                        | { verse: string; text: string }
                      )[]
                    )
                      .slice(0, showAllInstances ? undefined : 10)
                      .map((instance, index) => {
                        const verseRef =
                          typeof instance === "string"
                            ? instance
                            : instance.verse;
                        const cleanedRef = verseRef.replace(/\./g, "");
                        const verseId = parseVerseReference(cleanedRef);
                        return (
                          <Pressable
                            key={`${verseRef}-${index}`}
                            style={({ pressed }) => [
                              styles.instancePill,
                              pressed && styles.instancePillPressed,
                            ]}
                            onPress={() => {
                              if (verseId) {
                                sheetRef.current?.close();
                                router.push({
                                  pathname: "/verse-detail",
                                  params: { id: verseId },
                                });
                              }
                            }}
                          >
                            <Text style={styles.instanceRef}>{verseRef}</Text>
                          </Pressable>
                        );
                      })}
                    {!showAllInstances &&
                    (lexiconEntry?.instances?.length ??
                      word?.instances?.length ??
                      0) > 10 ? (
                      <Pressable
                        style={styles.showMoreButton}
                        onPress={() => setShowAllInstances(true)}
                      >
                        <Text style={styles.showMoreText}>
                          Show{" "}
                          {(lexiconEntry?.instances?.length ??
                            word?.instances?.length ??
                            0) - 10}{" "}
                          more
                        </Text>
                      </Pressable>
                    ) : null}
                  </View>
                ) : (
                  <Text style={styles.emptyText}>No instances available</Text>
                )}
              </>
            )}
          </>
        )}
      </BottomSheetScrollView>
    </BottomSheet>
  );
};
