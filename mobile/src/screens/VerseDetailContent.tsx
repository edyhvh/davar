import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { FlatList, StyleSheet, View, useWindowDimensions } from "react-native";
import {
  SafeAreaView,
  useSafeAreaInsets,
} from "react-native-safe-area-context";
import { useLocalSearchParams } from "expo-router";
import BottomSheet from "@gorhom/bottom-sheet";
import { useBottomTabBarHeight } from "@react-navigation/bottom-tabs";

import { VerseCard } from "@/src/components/VerseCard";
import { WordAnalysisBottomSheet } from "@/src/components/WordAnalysisBottomSheet";
import { BookSelectorSheet } from "@/src/components/BookSelectorSheet";
import { BookChapterPill } from "@/src/components/ui/BookChapterPill";
import { getColors, spacing } from "@/src/theme";
import { NumberGridBottomSheet } from "@/src/components/NumberGridBottomSheet";
import {
  getMockVerseById,
  mockBooks,
  mockVerses,
} from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { loadWordHintCount, saveWordHintCount } from "@/src/services/storage";

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      flex: 1,
    },
    navigationRow: {
      position: "absolute",
      top: spacing[16],
      left: 0,
      right: 0,
      alignItems: "center",
      zIndex: 10,
      elevation: 10,
    },
  });

export const VerseDetailContent = () => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const { height: screenHeight } = useWindowDimensions();
  const insets = useSafeAreaInsets();
  const tabBarHeight = useBottomTabBarHeight();
  const pageHeight = Math.max(
    0,
    screenHeight - insets.top - insets.bottom - tabBarHeight,
  );
  const centerOffset = spacing[6];
  const params = useLocalSearchParams<{ id?: string }>();
  const currentVerseId = useAppStore((state: AppState) => state.currentVerseId);
  const setCurrentVerseId = useAppStore(
    (state: AppState) => state.setCurrentVerseId,
  );
  const verseId = (params.id as string) ?? currentVerseId;
  const verse = getMockVerseById(verseId) ?? mockVerses[0];
  const bookMeta = useMemo(
    () =>
      mockBooks.find((book) => book.id === verse.bookId) ?? {
        id: verse.bookId,
        name: verse.book,
        hebrewName: verse.book,
      },
    [verse.book, verse.bookId],
  );

  const bookVerses = useMemo(
    () => mockVerses.filter((item) => item.bookId === verse.bookId),
    [verse.bookId],
  );
  const orderedVerses = useMemo(
    () =>
      [...bookVerses].sort(
        (a, b) => a.chapter - b.chapter || a.verse - b.verse,
      ),
    [bookVerses],
  );
  const currentIndex = useMemo(
    () => orderedVerses.findIndex((item) => item.id === verse.id),
    [orderedVerses, verse.id],
  );

  const chapterNumbers = useMemo(() => {
    const unique = new Set(bookVerses.map((item) => item.chapter));
    return Array.from(unique).sort((a, b) => a - b);
  }, [bookVerses]);

  const verseNumbers = useMemo(() => {
    const unique = new Set(
      bookVerses
        .filter((item) => item.chapter === verse.chapter)
        .map((item) => item.verse),
    );
    return Array.from(unique).sort((a, b) => a - b);
  }, [bookVerses, verse.chapter]);

  const [showWordHint, setShowWordHint] = useState(false);
  const listRef = useRef<FlatList<(typeof orderedVerses)[number]>>(null);
  const viewabilityConfigRef = useRef({ itemVisiblePercentThreshold: 70 });
  const onViewableItemsChanged = useRef(
    ({
      viewableItems,
    }: {
      viewableItems: { item: (typeof orderedVerses)[number] }[];
    }) => {
      const next = viewableItems[0]?.item;
      if (next && next.id !== currentVerseId) {
        setCurrentVerseId(next.id);
      }
    },
  );
  const sheetRef = useRef<BottomSheet>(null);
  const bookSheetRef = useRef<BottomSheet>(null);
  const chapterSheetRef = useRef<BottomSheet>(null);
  const verseSheetRef = useRef<BottomSheet>(null);
  const [selectedWord, setSelectedWord] = useState<
    (typeof verse.words)[number] | null
  >(() => verse.words?.[0] || null);

  useEffect(() => {
    setSelectedWord(verse.words?.[0] || null);
  }, [verse]);

  useEffect(() => {
    // Always show hint for testing
    setShowWordHint(true);
  }, []);

  const handleSelectChapter = useCallback(
    (chapter: number) => {
      const nextIndex = orderedVerses.findIndex(
        (item) => item.chapter === chapter,
      );
      if (nextIndex >= 0) {
        const nextVerse = orderedVerses[nextIndex];
        setCurrentVerseId(nextVerse.id);
        listRef.current?.scrollToIndex({ index: nextIndex, animated: true });
      }
      chapterSheetRef.current?.close();
    },
    [orderedVerses, setCurrentVerseId],
  );

  const handleSelectBook = useCallback(
    (bookId: string) => {
      const nextVerse = mockVerses.find((v) => v.bookId === bookId);
      if (nextVerse) {
        setCurrentVerseId(nextVerse.id);
      }
      bookSheetRef.current?.close();
    },
    [setCurrentVerseId],
  );

  const handleSelectVerse = useCallback(
    (verseNumber: number) => {
      const nextIndex = orderedVerses.findIndex(
        (item) => item.chapter === verse.chapter && item.verse === verseNumber,
      );
      if (nextIndex >= 0) {
        const nextVerse = orderedVerses[nextIndex];
        setCurrentVerseId(nextVerse.id);
        listRef.current?.scrollToIndex({ index: nextIndex, animated: true });
      }
      verseSheetRef.current?.close();
    },
    [orderedVerses, setCurrentVerseId, verse.chapter],
  );

  const handleWordPress = useCallback((word: typeof selectedWord) => {
    setSelectedWord(word);
    sheetRef.current?.expand();
  }, []);

  return (
    <>
      <SafeAreaView style={styles.safeArea} edges={["top", "bottom"]}>
        <View style={styles.container}>
          <View style={styles.navigationRow}>
            <BookChapterPill
              bookLabel={bookMeta.name}
              hebrewLabel={bookMeta.hebrewName}
              chapter={verse.chapter}
              onBookPress={() => bookSheetRef.current?.snapToIndex(0)}
              onChapterPress={() => chapterSheetRef.current?.expand()}
            />
          </View>
          <FlatList
            ref={listRef}
            data={orderedVerses}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <View
                style={{
                  height: pageHeight,
                  paddingHorizontal: spacing[6],
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                <View style={{ transform: [{ translateY: centerOffset }] }}>
                  <VerseCard
                    verse={item}
                    variant="detail"
                    showWordHint={showWordHint && item.id === verse.id}
                    onVersePress={() => verseSheetRef.current?.snapToIndex(0)}
                    onWordPress={handleWordPress}
                  />
                </View>
              </View>
            )}
            pagingEnabled
            showsVerticalScrollIndicator={false}
            decelerationRate="fast"
            snapToInterval={pageHeight}
            snapToAlignment="start"
            initialScrollIndex={Math.max(currentIndex, 0)}
            getItemLayout={(_, index) => ({
              length: pageHeight,
              offset: pageHeight * index,
              index,
            })}
            viewabilityConfig={viewabilityConfigRef.current}
            onViewableItemsChanged={onViewableItemsChanged.current}
          />
        </View>
      </SafeAreaView>
      <WordAnalysisBottomSheet
        sheetRef={sheetRef}
        word={selectedWord}
        onClose={() => sheetRef.current?.close()}
      />
      <BookSelectorSheet
        sheetRef={bookSheetRef}
        currentBookId={verse.bookId}
        onSelectBook={handleSelectBook}
      />
      <NumberGridBottomSheet
        sheetRef={chapterSheetRef}
        title="Chapter"
        numbers={chapterNumbers}
        selected={verse.chapter}
        onSelect={handleSelectChapter}
      />
      <NumberGridBottomSheet
        sheetRef={verseSheetRef}
        title="Verse"
        numbers={verseNumbers}
        selected={verse.verse}
        onSelect={handleSelectVerse}
      />
    </>
  );
};
