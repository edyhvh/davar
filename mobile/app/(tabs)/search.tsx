import { useCallback, useMemo, useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import type BottomSheet from "@gorhom/bottom-sheet";

import { AppIcon } from "@/src/components/ui/AppIcon";
import { BookSelectorSheet } from "@/src/components/BookSelectorSheet";
import { NumberGridBottomSheet } from "@/src/components/NumberGridBottomSheet";
import { VerseSelectorSheet } from "@/src/components/VerseSelectorSheet";
import { getColors, radii, spacing, typography } from "@/src/theme";
import { mockBooks, mockVerses } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[6],
      paddingBottom: spacing[4],
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    title: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.h2,
      color: colors.textPrimary,
    },
    subtitle: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      marginTop: spacing[2],
    },
    content: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      paddingHorizontal: spacing[6],
    },
    searchButton: {
      width: 120,
      height: 120,
      borderRadius: 60,
      backgroundColor: colors.surface,
      borderWidth: 2,
      borderColor: colors.primary,
      alignItems: "center",
      justifyContent: "center",
      marginBottom: spacing[6],
    },
    searchButtonPressed: {
      backgroundColor: colors.primaryLight,
    },
    searchButtonIcon: {
      color: colors.primary,
    },
    searchLabel: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textSecondary,
      textAlign: "center",
    },
    selectionContainer: {
      marginTop: spacing[8],
      width: "100%",
    },
    selectionRow: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: spacing[3],
      marginBottom: spacing[4],
    },
    selectionPill: {
      flexDirection: "row",
      alignItems: "center",
      paddingVertical: spacing[3],
      paddingHorizontal: spacing[4],
      borderRadius: radii.full,
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    selectionPillActive: {
      borderColor: colors.primary,
      backgroundColor: colors.primaryLight,
    },
    selectionText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
    },
    selectionTextPlaceholder: {
      color: colors.textSecondary,
    },
    arrow: {
      color: colors.textSecondary,
    },
    goButton: {
      paddingVertical: spacing[3],
      paddingHorizontal: spacing[6],
      borderRadius: radii.full,
      backgroundColor: colors.primary,
      alignSelf: "center",
      marginTop: spacing[4],
    },
    goButtonDisabled: {
      backgroundColor: colors.border,
    },
    goButtonText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.background,
      fontWeight: typography.weights.medium,
    },
  });

// Get the number of chapters for a book (mock implementation)
const getChapterCount = (bookId: string): number => {
  // Find max chapter number from mockVerses for this book
  const chaptersForBook = mockVerses
    .filter((v) => v.bookId === bookId)
    .map((v) => v.chapter);
  return chaptersForBook.length > 0 ? Math.max(...chaptersForBook) : 50;
};

// Get verse count for a chapter
const getVerseCount = (bookId: string, chapter: number): number => {
  const versesForChapter = mockVerses.filter(
    (v) => v.bookId === bookId && v.chapter === chapter,
  );
  if (versesForChapter.length > 0) {
    return Math.max(...versesForChapter.map((v) => v.verse));
  }
  // Default to reasonable verse count
  return 30;
};

export default function SearchScreen() {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);

  // Selection state
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);
  const [selectedVerse, setSelectedVerse] = useState<number | null>(null);

  // Sheet refs
  const bookSheetRef = useRef<BottomSheet>(null);
  const chapterSheetRef = useRef<BottomSheet>(null);
  const verseSheetRef = useRef<BottomSheet>(null);

  // Computed values
  const selectedBook = useMemo(
    () => mockBooks.find((b) => b.id === selectedBookId),
    [selectedBookId],
  );

  const chapterNumbers = useMemo(() => {
    if (!selectedBookId) return [];
    const count = getChapterCount(selectedBookId);
    return Array.from({ length: count }, (_, i) => i + 1);
  }, [selectedBookId]);

  const verseNumbers = useMemo(() => {
    if (!selectedBookId || !selectedChapter) return [];
    const count = getVerseCount(selectedBookId, selectedChapter);
    return Array.from({ length: count }, (_, i) => i + 1);
  }, [selectedBookId, selectedChapter]);

  const canNavigate =
    selectedBookId !== null &&
    selectedChapter !== null &&
    selectedVerse !== null;

  // Handlers
  const handleOpenBookSelector = useCallback(() => {
    bookSheetRef.current?.snapToIndex(0);
  }, []);

  const handleSelectBook = useCallback((bookId: string) => {
    setSelectedBookId(bookId);
    setSelectedChapter(null);
    setSelectedVerse(null);
    // Open chapter selector after a brief delay
    setTimeout(() => {
      chapterSheetRef.current?.snapToIndex(0);
    }, 300);
  }, []);

  const handleSelectChapter = useCallback((chapter: number) => {
    setSelectedChapter(chapter);
    setSelectedVerse(null);
    chapterSheetRef.current?.close();
    // Open verse selector after a brief delay
    setTimeout(() => {
      verseSheetRef.current?.snapToIndex(0);
    }, 300);
  }, []);

  const handleSelectVerse = useCallback(
    (verse: number) => {
      setSelectedVerse(verse);
      verseSheetRef.current?.close();
      // Navigate to the verse
      if (selectedBookId && selectedChapter) {
        const verseId = `${selectedBookId}-${selectedChapter}-${verse}`;
        router.push({
          pathname: "/verse-detail",
          params: { id: verseId },
        });
      }
    },
    [selectedBookId, selectedChapter],
  );

  const handleBackToChapters = useCallback(() => {
    setSelectedVerse(null);
    setTimeout(() => {
      chapterSheetRef.current?.snapToIndex(0);
    }, 300);
  }, []);

  const handleNavigate = useCallback(() => {
    if (canNavigate) {
      const verseId = `${selectedBookId}-${selectedChapter}-${selectedVerse}`;
      router.push({
        pathname: "/verse-detail",
        params: { id: verseId },
      });
    }
  }, [canNavigate, selectedBookId, selectedChapter, selectedVerse]);

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Search</Text>
          <Text style={styles.subtitle}>
            Navigate to any book, chapter, and verse
          </Text>
        </View>

        <View style={styles.content}>
          <Pressable
            style={({ pressed }) => [
              styles.searchButton,
              pressed && styles.searchButtonPressed,
            ]}
            onPress={handleOpenBookSelector}
          >
            <AppIcon
              name="search"
              size={48}
              color={styles.searchButtonIcon.color}
            />
          </Pressable>
          <Text style={styles.searchLabel}>
            Tap to select a book, chapter, and verse
          </Text>

          {/* Current selection display */}
          {(selectedBookId || selectedChapter || selectedVerse) && (
            <View style={styles.selectionContainer}>
              <View style={styles.selectionRow}>
                <Pressable
                  style={[
                    styles.selectionPill,
                    selectedBookId && styles.selectionPillActive,
                  ]}
                  onPress={handleOpenBookSelector}
                >
                  <Text
                    style={[
                      styles.selectionText,
                      !selectedBook && styles.selectionTextPlaceholder,
                    ]}
                  >
                    {selectedBook?.name ?? "Book"}
                  </Text>
                </Pressable>

                <AppIcon name="book" size={16} color={styles.arrow.color} />

                <Pressable
                  style={[
                    styles.selectionPill,
                    selectedChapter !== null && styles.selectionPillActive,
                  ]}
                  onPress={() =>
                    selectedBookId && chapterSheetRef.current?.snapToIndex(0)
                  }
                >
                  <Text
                    style={[
                      styles.selectionText,
                      selectedChapter === null && styles.selectionTextPlaceholder,
                    ]}
                  >
                    {selectedChapter ?? "Ch"}
                  </Text>
                </Pressable>

                <Text style={styles.selectionText}>:</Text>

                <Pressable
                  style={[
                    styles.selectionPill,
                    selectedVerse !== null && styles.selectionPillActive,
                  ]}
                  onPress={() =>
                    selectedChapter && verseSheetRef.current?.snapToIndex(0)
                  }
                >
                  <Text
                    style={[
                      styles.selectionText,
                      selectedVerse === null && styles.selectionTextPlaceholder,
                    ]}
                  >
                    {selectedVerse ?? "V"}
                  </Text>
                </Pressable>
              </View>

              {canNavigate && (
                <Pressable
                  style={[
                    styles.goButton,
                    !canNavigate && styles.goButtonDisabled,
                  ]}
                  onPress={handleNavigate}
                >
                  <Text style={styles.goButtonText}>Go to Verse</Text>
                </Pressable>
              )}
            </View>
          )}
        </View>
      </View>

      {/* Book Selector Sheet */}
      <BookSelectorSheet
        sheetRef={bookSheetRef}
        currentBookId={selectedBookId ?? undefined}
        onSelectBook={handleSelectBook}
      />

      {/* Chapter Selector Sheet */}
      <NumberGridBottomSheet
        sheetRef={chapterSheetRef}
        title={`Select Chapter${selectedBook ? ` - ${selectedBook.name}` : ""}`}
        numbers={chapterNumbers}
        selected={selectedChapter ?? 0}
        onSelect={handleSelectChapter}
      />

      {/* Verse Selector Sheet */}
      <VerseSelectorSheet
        sheetRef={verseSheetRef}
        title={`Select Verse${selectedBook && selectedChapter ? ` - ${selectedBook.name} ${selectedChapter}` : ""}`}
        numbers={verseNumbers}
        selected={selectedVerse ?? 0}
        onSelect={handleSelectVerse}
        onBack={handleBackToChapters}
      />
    </SafeAreaView>
  );
}
