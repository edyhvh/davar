import { useMemo } from "react";
import { FlatList, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams } from "expo-router";

import { getColors, spacing, typography } from "@/src/theme";
import { mockBooks, mockVerses } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

const stripNikud = (value: string) =>
  value.normalize("NFD").replace(/[\u0591-\u05C7]/g, "");

const createStyles = (colors: ReturnType<typeof getColors>) =>
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
      fontSize: typography.sizes.hebrewVerseMedium,
      lineHeight:
        typography.sizes.hebrewVerseMedium *
        typography.lineHeights.hebrewScripture,
      color: colors.textPrimary,
      textAlign: "right",
      writingDirection: "rtl",
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
  const hebrewOnly = useAppStore((state: AppState) => state.hebrewOnly);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const bookId = params.bookId ?? "genesis";
  const chapter = Number(params.chapter ?? 1);
  const book = mockBooks.find((item) => item.id === bookId);

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
      <FlatList
        data={verses}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <View style={styles.verseBlock}>
            <Text style={styles.verseNumber}>[{item.verse}]</Text>
            <Text style={styles.hebrewText}>{item.hebrew}</Text>
            {hebrewOnly ? null : (
              <Text style={styles.translation}>{item.translation}</Text>
            )}
          </View>
        )}
        showsVerticalScrollIndicator={false}
      />
    </SafeAreaView>
  );
}
