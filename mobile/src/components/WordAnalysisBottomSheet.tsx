import React, {
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  Pressable,
  StyleSheet,
  Text,
  View,
  useWindowDimensions,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import BottomSheet, {
  BottomSheetBackdrop,
  BottomSheetScrollView,
  type BottomSheetBackdropProps,
  type BottomSheetMethods,
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
import { useTranslation } from "@/src/i18n/useTranslation";

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
        dss_translit_en?: string;
        dss_translit_es?: string;
        dssWord?: string;
        dssStrong?: string;
        dssCommentaryEn?: string;
        dssCommentaryEs?: string;
        dssCommentaryHe?: string;
      })
    | null;
  // Called after the sheet has fully closed and any exit animations have completed
  onClosed?: () => void;
};

type TabType = "masoretic" | "qumran" | "instances";

const createStyles = (
  colors: ReturnType<typeof getColors>,
  hebrewScale: number,
) =>
  StyleSheet.create({
    content: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[2],
    },
    sheetBackground: {
      backgroundColor: colors.surface,
      borderTopLeftRadius: radii.xl,
      borderTopRightRadius: radii.xl,
    },
    sheetBackgroundDss: {
      backgroundColor: colors.surface,
      borderTopLeftRadius: radii.xl,
      borderTopRightRadius: radii.xl,
      borderWidth: 1,
      borderColor: `${colors.accentCopper}66`,
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
    hebrewQumran: {
      fontFamily: typography.families.hebrewQumran,
      color: colors.qumranText,
    },
    qumranText: {
      color: colors.qumranText,
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
      fontWeight: "700",
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
    rootStrong: {
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
    commentaryText: {
      fontFamily: typography.families.latinMeaning,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      textAlign: "center",
      lineHeight: 22,
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

const WordAnalysisBottomSheetComponent = (
  { word, currentVerseId, onClosed }: WordAnalysisBottomSheetProps,
  ref: React.ForwardedRef<BottomSheetMethods>,
) => {
  const sheetRef = useRef<BottomSheetMethods>(null!);
  useImperativeHandle(ref, () => sheetRef.current);
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const insets = useSafeAreaInsets();
  const { height: screenHeight } = useWindowDimensions();
  const hebrewFontScale = useAppStore(
    (state: AppState) => state.hebrewFontScale,
  );
  const language = useAppStore((state: AppState) => state.language);
  const { t } = useTranslation();
  const colors = getColors(themeMode);
  const styles = useMemo(
    () => createStyles(colors, hebrewFontScale),
    [colors, hebrewFontScale],
  );
  const snapPoints = useMemo(() => {
    const minHeight = Math.max(0, screenHeight * 0.5);
    const maxHeight = Math.max(0, screenHeight * 0.8);
    if (maxHeight <= minHeight) {
      return [minHeight];
    }
    return [minHeight, maxHeight];
  }, [screenHeight]);
  const [activeTab, setActiveTab] = useState<TabType>("masoretic");
  const [lexiconEntry, setLexiconEntry] = useState<LexiconResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [dssLexiconEntry, setDssLexiconEntry] =
    useState<LexiconResponse | null>(null);
  const [isDssLoading, setIsDssLoading] = useState(false);
  const [showAllInstances, setShowAllInstances] = useState(false);
  const [prefixEntries, setPrefixEntries] = useState<
    Record<string, PrefixResponse | null>
  >({});
  const showNikud = useAppStore((state: AppState) => state.showNikud);
  const showCantillation = useAppStore(
    (state: AppState) => state.showCantillation,
  );
  const hasDssVariant = Boolean(
    word?.dssWord ||
    word?.dssStrong ||
    word?.dssCommentaryEn ||
    word?.dssCommentaryEs ||
    word?.dssCommentaryHe,
  );
  const strongNumber = useMemo(() => {
    if (!word?.strong) return null;
    const parts = word.strong.split("/").map((part) => part.trim());
    const strongPart = parts.find((part) => /^[HG]\d+$/.test(part));
    return strongPart ?? null;
  }, [word?.strong]);

  const dssStrongNumber = useMemo(() => {
    if (!word?.dssStrong) return null;
    const parts = word.dssStrong.split("/").map((part) => part.trim());
    const strongPart = parts.find((part) => /^[HG]\d+$/.test(part));
    return strongPart ?? null;
  }, [word?.dssStrong]);
  // Keep in sync with web/src/app/App.tsx transliteration selection logic.
  const wordTransliteration = useMemo(() => {
    // Determine which strong number is currently active
    const checkStrong = activeTab === "qumran" ? dssStrongNumber : strongNumber;
    // Hide transliteration for YHVH (H3068)
    if (checkStrong === "H3068") return undefined;

    if (activeTab === "qumran") {
      const strongTranslit =
        language === "en"
          ? dssLexiconEntry?.translit_en
          : language === "es"
            ? dssLexiconEntry?.translit_es
            : undefined;
      if (strongTranslit) return strongTranslit;
    }
    return language === "en"
      ? word?.translit_en
      : language === "es"
        ? word?.translit_es
        : undefined;
  }, [
    activeTab,
    language,
    word?.translit_en,
    word?.translit_es,
    dssLexiconEntry?.translit_en,
    dssLexiconEntry?.translit_es,
    strongNumber,
    dssStrongNumber,
  ]);

  const displayHebrew = useMemo(() => {
    const baseWord =
      activeTab === "qumran" && word?.dssWord
        ? word.dssWord
        : (word?.text ?? lexiconEntry?.hebrew ?? "—");
    let base = baseWord;
    if (!showNikud) {
      base = stripNikud(base);
    }
    if (!showCantillation) {
      base = stripCantillation(base);
    }
    base = stripMeteg(base);
    return normalizeHebrewDisplay(base).replace(/\//g, "");
  }, [
    activeTab,
    lexiconEntry?.hebrew,
    word?.dssWord,
    word?.text,
    showNikud,
    showCantillation,
  ]);

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
    const loadDssLexicon = async () => {
      if (!dssStrongNumber) {
        setDssLexiconEntry(null);
        return;
      }
      setIsDssLoading(true);
      try {
        const params = new URLSearchParams();
        if (language !== "he") {
          params.set("language", language);
        }
        if (word?.dssWord) {
          params.set("hebrew", word.dssWord);
        }
        const query = params.toString();
        const url = query
          ? `/api/v1/lexicon/${dssStrongNumber}?${query}`
          : `/api/v1/lexicon/${dssStrongNumber}`;
        const entry = await apiRequest<LexiconResponse>(url);
        setDssLexiconEntry(entry);
        console.debug(
          "WordAnalysisBottomSheet: dss lexicon loaded",
          dssStrongNumber,
          entry?.hebrew ?? entry?.root_strong ?? null,
        );
      } catch {
        setDssLexiconEntry(null);
        console.debug(
          "WordAnalysisBottomSheet: dss lexicon fetch failed",
          dssStrongNumber,
        );
      } finally {
        setIsDssLoading(false);
      }
    };
    loadDssLexicon();
  }, [dssStrongNumber, language, word?.dssWord]);

  useEffect(() => {
    // Reset to meanings tab when a new word is selected
    setActiveTab("masoretic");
    setShowAllInstances(false);
  }, [word?.strong, word?.dssStrong]);

  useEffect(() => {
    if (!hasDssVariant && activeTab === "qumran") {
      setActiveTab("masoretic");
    }
  }, [activeTab, hasDssVariant]);

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
    setDssLexiconEntry(null);
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
      return [t("wordCard.properName")];
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

    const formatted = rawMeanings.map((item) => formatMeaning(item));
    return formatted.length ? formatted : ["—"];
  }, [lexiconEntry, word, language, t]);

  const dssMeaningsList = useMemo(() => {
    const normalizeForDisplay = (t: string) =>
      stripCantillation(stripNikud(t)).replace(/\//g, "").trim();

    const formatMeaning = (text: string) => {
      const cleaned = text.replace(/^[-–—]\s*/, "").trim();
      if (!cleaned) return cleaned;
      return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
    };

    if (!dssLexiconEntry?.definitions?.length) {
      return ["—"];
    }

    const rawMeanings = dssLexiconEntry.definitions
      .map((item) => (item.text ? normalizeForDisplay(item.text) : ""))
      .filter(Boolean);

    const formatted = rawMeanings.map((item) => formatMeaning(item));
    return formatted.length ? formatted : ["—"];
  }, [dssLexiconEntry]);

  const formatRootMeaningText = (text: string) => {
    if (text === "ALREADY ROOT") {
      return t("wordCard.alreadyRoot");
    }
    if (text === "—") {
      return text;
    }
    const cleaned = text.replace(/^[-–—]\s*/, "").trim();
    if (!cleaned) return cleaned;
    return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
  };

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

  const isDssDerivedRoot = Boolean(
    dssLexiconEntry?.root_strong || dssLexiconEntry?.root,
  );

  const dssRootMeaningText = useMemo(() => {
    if (!isDssDerivedRoot) return "ALREADY ROOT";
    if (dssLexiconEntry?.root_definitions?.length) {
      return (
        dssLexiconEntry.root_definitions.map((item) => item.text).join(", ") ||
        "—"
      );
    }
    return "—";
  }, [dssLexiconEntry, isDssDerivedRoot]);

  const dssCommentary = useMemo(() => {
    if (!word) return undefined;
    if (language === "es") {
      return (
        word.dssCommentaryEs ?? word.dssCommentaryEn ?? word.dssCommentaryHe
      );
    }
    if (language === "he") {
      return (
        word.dssCommentaryHe ?? word.dssCommentaryEn ?? word.dssCommentaryEs
      );
    }
    return word.dssCommentaryEn ?? word.dssCommentaryEs ?? word.dssCommentaryHe;
  }, [language, word]);

  const isQumranTab = hasDssVariant && activeTab === "qumran";
  const activeStrongNumber = isQumranTab ? dssStrongNumber : strongNumber;

  return (
    <BottomSheet
      ref={sheetRef}
      index={-1}
      snapPoints={snapPoints}
      enableDynamicSizing={false}
      enablePanDownToClose
      backgroundStyle={
        hasDssVariant ? styles.sheetBackgroundDss : styles.sheetBackground
      }
      handleIndicatorStyle={styles.sheetHandle}
      onChange={handleSheetChanges}
      onClose={handleSheetClose}
      backdropComponent={renderBackdrop}
      animateOnMount={false}
    >
      <BottomSheetScrollView
        style={styles.content}
        contentContainerStyle={{ paddingBottom: spacing[8] + insets.bottom }}
      >
        {/* Show empty state when no word is selected */}
        {!word ? (
          <View style={styles.headerSection}>
            <Text style={styles.emptyText}>
              {t("wordCard.selectWordPrompt")}
            </Text>
          </View>
        ) : (
          <>
            {/* Header: Hebrew word + transliteration */}
            <View style={styles.headerSection}>
              <Text style={[styles.hebrew, isQumranTab && styles.hebrewQumran]}>
                {displayHebrew}
              </Text>
              {wordTransliteration ? (
                <Text
                  style={[
                    styles.transliteration,
                    isQumranTab && styles.qumranText,
                  ]}
                >
                  {wordTransliteration}
                </Text>
              ) : null}
              {lexiconEntry?.occurrences_count && !isQumranTab && (
                <Text style={styles.occurrencesText}>
                  {t("wordCard.appearsCount", {
                    count: lexiconEntry.occurrences_count,
                  })}
                </Text>
              )}
              {activeStrongNumber ? (
                <Text
                  style={[
                    styles.occurrencesText,
                    isQumranTab && styles.qumranText,
                  ]}
                >
                  {activeStrongNumber}
                </Text>
              ) : null}
            </View>

            {/* Toggle: Qumran / Masoretic / Instances */}
            <View style={styles.toggleContainer}>
              {hasDssVariant ? (
                <Pressable
                  style={[
                    styles.toggleButton,
                    activeTab === "qumran" && styles.toggleButtonActive,
                  ]}
                  onPress={() => setActiveTab("qumran")}
                >
                  <Text
                    style={[
                      styles.toggleText,
                      activeTab === "qumran" && styles.toggleTextActive,
                    ]}
                  >
                    {t("wordCard.qumran")}
                  </Text>
                </Pressable>
              ) : null}
              <Pressable
                style={[
                  styles.toggleButton,
                  activeTab === "masoretic" && styles.toggleButtonActive,
                ]}
                onPress={() => setActiveTab("masoretic")}
              >
                <Text
                  style={[
                    styles.toggleText,
                    activeTab === "masoretic" && styles.toggleTextActive,
                  ]}
                >
                  {hasDssVariant
                    ? t("wordCard.masoretic")
                    : t("wordCard.meanings")}
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
                  {t("wordCard.instances")}
                </Text>
              </Pressable>
            </View>

            {/* Tab Content */}
            {activeTab === "masoretic" ? (
              <>
                {/* Meanings section */}
                <Text style={[styles.sectionLabel, styles.sectionLabelBold]}>
                  {t("wordCard.meanings")}
                </Text>
                {isLoading ? (
                  <Text style={styles.emptyText}>
                    {t("wordCard.loadingDefinitions")}
                  </Text>
                ) : null}
                <View style={styles.meaningsList}>
                  {meaningsList.map((meaning, index) => (
                    <Text
                      key={`${meaning}-${index}`}
                      style={styles.meaningsBullet}
                    >
                      {meaning}
                    </Text>
                  ))}
                </View>

                {word?.prefixes?.length ? (
                  <View style={styles.prefixesSection}>
                    <Text
                      style={[styles.sectionLabel, styles.sectionLabelBold]}
                    >
                      {t("wordCard.preposition")}
                    </Text>
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

                {/* Root section */}
                <View style={styles.rootSection}>
                  <Text style={[styles.sectionLabel, styles.sectionLabelBold]}>
                    {t("wordCard.root")}
                  </Text>
                  {lexiconEntry?.root || word?.root ? (
                    <>
                      <Text style={styles.rootHebrew}>
                        {(lexiconEntry?.root ?? word?.root ?? "").replace(
                          /\//g,
                          "",
                        )}
                      </Text>
                      {lexiconEntry?.root_strong ? (
                        <Text style={styles.rootStrong}>
                          {lexiconEntry.root_strong}
                        </Text>
                      ) : null}
                      {(language === "en"
                        ? lexiconEntry?.root_translit_en
                        : lexiconEntry?.root_translit_es) ||
                      word?.rootTransliteration ? (
                        <Text style={styles.rootTransliteration}>
                          {(language === "en"
                            ? lexiconEntry?.root_translit_en
                            : lexiconEntry?.root_translit_es) ??
                            word?.rootTransliteration}
                        </Text>
                      ) : null}
                      {/* Show meaning only if root differs from word */}
                      {lexiconEntry?.root_strong &&
                        strongNumber &&
                        lexiconEntry.root_strong !== strongNumber && (
                          <Text style={styles.rootMeaning}>
                            {formatRootMeaningText(rootMeaningText)}
                          </Text>
                        )}
                    </>
                  ) : (
                    <Text style={styles.rootMeaning}>
                      {t("wordCard.alreadyRoot")}
                    </Text>
                  )}
                </View>
              </>
            ) : activeTab === "qumran" ? (
              <>
                <Text style={[styles.sectionLabel, styles.sectionLabelBold]}>
                  {t("wordCard.meanings")}
                </Text>
                {isDssLoading ? (
                  <Text style={styles.emptyText}>
                    {t("wordCard.loadingDefinitions")}
                  </Text>
                ) : null}
                <View style={styles.meaningsList}>
                  {dssMeaningsList.map((meaning, index) => (
                    <Text
                      key={`${meaning}-${index}`}
                      style={[styles.meaningsBullet, styles.qumranText]}
                    >
                      {meaning}
                    </Text>
                  ))}
                </View>

                <Text style={styles.sectionLabel}>
                  {t("wordCard.commentary")}
                </Text>
                <Text style={[styles.commentaryText, styles.qumranText]}>
                  {dssCommentary ?? "—"}
                </Text>

                <View style={styles.rootSection}>
                  <Text style={[styles.sectionLabel, styles.sectionLabelBold]}>
                    {t("wordCard.root")}
                  </Text>
                  <Text style={[styles.rootHebrew, styles.qumranText]}>
                    {(
                      dssLexiconEntry?.root ??
                      dssLexiconEntry?.hebrew ??
                      displayHebrew
                    ).replace(/\//g, "")}
                  </Text>
                  {dssLexiconEntry?.root_strong ? (
                    <Text style={[styles.rootStrong, styles.qumranText]}>
                      {dssLexiconEntry.root_strong}
                    </Text>
                  ) : null}
                  {(
                    language === "en"
                      ? dssLexiconEntry?.root_translit_en
                      : dssLexiconEntry?.root_translit_es
                  ) ? (
                    <Text
                      style={[styles.rootTransliteration, styles.qumranText]}
                    >
                      {language === "en"
                        ? dssLexiconEntry?.root_translit_en
                        : dssLexiconEntry?.root_translit_es}
                    </Text>
                  ) : null}
                  {/* Show meaning only if root differs from word or if no specific DSS root */}
                  {dssLexiconEntry?.root || dssLexiconEntry?.root_strong ? (
                    dssLexiconEntry.root_strong &&
                    dssStrongNumber &&
                    dssLexiconEntry.root_strong !== dssStrongNumber ? (
                      <Text style={[styles.rootMeaning, styles.qumranText]}>
                        {formatRootMeaningText(dssRootMeaningText)}
                      </Text>
                    ) : null
                  ) : (
                    <Text style={[styles.rootMeaning, styles.qumranText]}>
                      {t("wordCard.alreadyRoot")}
                    </Text>
                  )}
                </View>
              </>
            ) : (
              <>
                {/* Instances section */}
                <Text style={styles.sectionLabel}>
                  {t("wordCard.appearsIn")}
                </Text>
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
                          {t("wordCard.showMore", {
                            count:
                              (lexiconEntry?.instances?.length ??
                                word?.instances?.length ??
                                0) - 10,
                          })}
                        </Text>
                      </Pressable>
                    ) : null}
                  </View>
                ) : (
                  <Text style={styles.emptyText}>
                    {t("wordCard.noInstances")}
                  </Text>
                )}
              </>
            )}
          </>
        )}
      </BottomSheetScrollView>
    </BottomSheet>
  );
};

export const WordAnalysisBottomSheet = React.forwardRef(
  WordAnalysisBottomSheetComponent,
);
