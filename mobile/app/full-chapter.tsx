import { useMemo } from "react";
import { FlatList, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams } from "expo-router";

import { getColors, spacing, typography } from "@/src/theme";
import { mockBooks, mockVerses } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { stripCantillation, stripMeteg, stripNikud } from "@/src/utils/hebrew";

const createStyles = (
  colors: ReturnType<typeof getColors>,
  hebrewScale: number,
) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[6],
      paddingBottom: spacing[4],
      alignItems: "center",
    },
    headerTitle: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      letterSpacing: 0.8,
      textTransform: "uppercase",
    },
    headerHebrew: {
      fontFamily: typography.families.hebrewUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      marginTop: spacing[2],
    },
    listContent: {
      paddingHorizontal: spacing[6],
      paddingBottom: spacing[12],
    },
    verseBlock: {
      marginBottom: spacing[6],
    },
    verseNumber: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      color: colors.textSecondary,
      letterSpacing: 0.6,
      textAlign: "right",
      marginBottom: spacing[2],
    },
    hebrewText: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: typography.sizes.hebrewVerseMedium * hebrewScale * 1.06,
      lineHeight:
        typography.sizes.hebrewVerseMedium *
        hebrewScale *
        typography.lineHeights.hebrewScripture,
      color: colors.textPrimary,
      textAlign: "right",
      writingDirection: "rtl",
    },
    seferText: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: typography.sizes.hebrewVerseMedium * hebrewScale * 1.06,
      lineHeight:
        typography.sizes.hebrewVerseMedium *
        hebrewScale *
        typography.lineHeights.hebrewScripture,
      color: colors.textPrimary,
      textAlign: "right",
      writingDirection: "rtl",
      letterSpacing: 0.3,
    },
    seferVerseNumber: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      color: colors.textSecondary,
      letterSpacing: 0.6,
    },
    translation: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      lineHeight: typography.sizes.body * typography.lineHeights.body,
      color: colors.textSecondary,
      marginTop: spacing[3],
    },
  });

export default function FullChapterScreen() {
  const params = useLocalSearchParams<{ bookId?: string; chapter?: string }>();
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const hebrewFontScale = useAppStore(
    (state: AppState) => state.hebrewFontScale,
  );
  const hebrewOnly = useAppStore((state: AppState) => state.hebrewOnly);
  const seferMode = useAppStore((state: AppState) => state.seferMode);
  const showNikud = useAppStore((state: AppState) => state.showNikud);
  const showCantillation = useAppStore(
    (state: AppState) => state.showCantillation,
  );
  const colors = getColors(themeMode);
  const styles = useMemo(
    () => createStyles(colors, hebrewFontScale),
    [colors, hebrewFontScale],
  );
  const bookId = params.bookId ?? "genesis";
  const chapter = Number(params.chapter ?? 1);
  const book = mockBooks.find((item) => item.id === bookId);
  const shouldShowSefer = seferMode && hebrewOnly;

  const normalizeHebrew = (text: string) => {
    let normalized = text;
    if (!showNikud) {
      normalized = stripNikud(normalized);
    }
    if (!showCantillation) {
      normalized = stripCantillation(normalized);
    }
    normalized = stripMeteg(normalized);
    return normalized.replace(/\//g, "");
  };

  const verses = useMemo(
    () =>
      mockVerses
        .filter((item) => item.bookId === bookId && item.chapter === chapter)
        .sort((a, b) => a.verse - b.verse),
    [bookId, chapter],
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={["top", "bottom"]}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          {book?.name ?? ""} {chapter}
        </Text>
        {book?.hebrewName ? (
          <Text style={styles.headerHebrew}>{stripNikud(book.hebrewName)}</Text>
        ) : null}
      </View>
      {shouldShowSefer ? (
        <ScrollView
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.seferText}>
            {verses.map((item, index) => (
              <Text key={item.id}>
                <Text style={styles.seferVerseNumber}>[{item.verse}]</Text>{" "}
                {normalizeHebrew(item.hebrew)}
                {index < verses.length - 1 ? " " : ""}
              </Text>
            ))}
          </Text>
        </ScrollView>
      ) : (
        <FlatList
          data={verses}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          renderItem={({ item }) => (
            <View style={styles.verseBlock}>
              <Text style={styles.verseNumber}>[{item.verse}]</Text>
              <Text style={styles.hebrewText}>{normalizeHebrew(item.hebrew)}</Text>
              {hebrewOnly ? null : (
                <Text style={styles.translation}>{item.translation}</Text>
              )}
            </View>
          )}
          showsVerticalScrollIndicator={false}
        />
      )}
    </SafeAreaView>
  );
}
