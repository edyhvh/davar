import React, { useCallback, useMemo, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import BottomSheet, {
  BottomSheetBackdrop,
  BottomSheetView,
  type BottomSheetBackdropProps,
} from "@gorhom/bottom-sheet";
import { router } from "expo-router";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import type { MockWord } from "@/src/constants/mockData";

type WordAnalysisBottomSheetProps = {
  sheetRef: React.RefObject<BottomSheet | null>;
  word?: MockWord | null;
  onClose?: () => void;
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
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.h3,
      color: colors.textPrimary,
      textAlign: "center",
      lineHeight: 28,
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
    emptyText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textSecondary,
      textAlign: "center",
      fontStyle: "italic",
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
  "1Sam": "1samuel",
  "2Sam": "2samuel",
  "1Kgs": "1kings",
  "2Kgs": "2kings",
  "1Chr": "1chronicles",
  "2Chr": "2chronicles",
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
  "1Cor": "1corinthians",
  "2Cor": "2corinthians",
  Gal: "galatians",
  Eph: "ephesians",
  Phil: "philippians",
  Col: "colossians",
  "1Thess": "1thessalonians",
  "2Thess": "2thessalonians",
  "1Tim": "1timothy",
  "2Tim": "2timothy",
  Titus: "titus",
  Phlm: "philemon",
  Heb: "hebrews",
  Jas: "james",
  "1Pet": "1peter",
  "2Pet": "2peter",
  "1John": "1john",
  "2John": "2john",
  "3John": "3john",
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
  onClose,
}: WordAnalysisBottomSheetProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const hebrewFontScale = useAppStore(
    (state: AppState) => state.hebrewFontScale,
  );
  const colors = getColors(themeMode);
  const styles = useMemo(
    () => createStyles(colors, hebrewFontScale),
    [colors, hebrewFontScale],
  );
  const [activeTab, setActiveTab] = useState<TabType>("meanings");

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

  const handleSheetChanges = useCallback(
    (index: number) => {
      if (index === -1) {
        onClose?.();
        setActiveTab("meanings");
      }
    },
    [onClose],
  );

  const meaningsText = useMemo(() => {
    if (!word) return "—";
    const meanings = word.meanings?.length ? word.meanings : [word.gloss];
    return meanings.filter(Boolean).join(", ") || "—";
  }, [word]);

  const rootMeaningText = useMemo(() => {
    if (!word?.rootMeaning) return "—";
    return word.rootMeaning;
  }, [word]);

  return (
    <BottomSheet
      ref={sheetRef}
      index={-1}
      enableDynamicSizing
      maxDynamicContentSize={600}
      enablePanDownToClose
      backgroundStyle={styles.sheetBackground}
      handleIndicatorStyle={styles.sheetHandle}
      onChange={handleSheetChanges}
      backdropComponent={renderBackdrop}
    >
      <BottomSheetView style={styles.content}>
        {/* Header: Hebrew word + transliteration */}
        <View style={styles.headerSection}>
          <Text style={styles.hebrew}>{word?.text ?? "—"}</Text>
          {word?.transliteration ? (
            <Text style={styles.transliteration}>{word.transliteration}</Text>
          ) : null}
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
            <Text style={styles.meaningsText}>{meaningsText}</Text>

            {/* Root section */}
            {word?.root ? (
              <View style={styles.rootSection}>
                <Text style={styles.sectionLabel}>Root</Text>
                <Text style={styles.rootHebrew}>{word.root}</Text>
                {word.rootTransliteration ? (
                  <Text style={styles.rootTransliteration}>
                    {word.rootTransliteration}
                  </Text>
                ) : null}
                <Text style={styles.rootMeaning}>{rootMeaningText}</Text>
              </View>
            ) : null}
          </>
        ) : (
          <>
            {/* Instances section */}
            <Text style={styles.sectionLabel}>Appears In</Text>
            {word?.instances?.length ? (
              <View style={styles.instancesContainer}>
                {word.instances.map((instance, index) => {
                  const verseId = parseVerseReference(instance.verse);
                  return (
                    <Pressable
                      key={`${instance.verse}-${index}`}
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
                      <Text style={styles.instanceRef}>{instance.verse}</Text>
                    </Pressable>
                  );
                })}
              </View>
            ) : (
              <Text style={styles.emptyText}>No instances available</Text>
            )}
          </>
        )}
      </BottomSheetView>
    </BottomSheet>
  );
};
