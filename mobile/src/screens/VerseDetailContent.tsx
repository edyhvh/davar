import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { FlatList, StyleSheet, View, useWindowDimensions } from "react-native";
import {
  SafeAreaView,
  useSafeAreaInsets,
} from "react-native-safe-area-context";
import { useLocalSearchParams, useNavigation } from "expo-router";
import BottomSheet from "@gorhom/bottom-sheet";
import { useBottomTabBarHeight } from "@react-navigation/bottom-tabs";
import type { BottomTabNavigationProp } from "@react-navigation/bottom-tabs";
import type { ParamListBase } from "@react-navigation/native";

import { VerseCard } from "@/src/components/VerseCard";
import { WordAnalysisBottomSheet } from "@/src/components/WordAnalysisBottomSheet";
import { NavigationSheet } from "@/src/components/NavigationSheet";
import { BookChapterPill } from "@/src/components/ui/BookChapterPill";
import { getColors, spacing } from "@/src/theme";
import {
  getMockVerseById,
  mockBooks,
  mockVerses,
} from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type TabPressEvent = {
  preventDefault: () => void;
};

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
  const navigationSheetRef = useRef<BottomSheet>(null);
  const [selectedWord, setSelectedWord] = useState<
    (typeof verse.words)[number] | null
  >(() => verse.words?.[0] || null);

  // Listen for tab press to open navigation sheet
  const navigation = useNavigation<BottomTabNavigationProp<ParamListBase>>();
  useEffect(() => {
    const unsubscribe = navigation.addListener(
      "tabPress",
      (e: TabPressEvent) => {
        // If we're already on this tab, open the navigation sheet
        if (navigation.isFocused()) {
          e.preventDefault();
          navigationSheetRef.current?.snapToIndex(0);
        }
      },
    );
    return unsubscribe;
  }, [navigation]);

  useEffect(() => {
    setSelectedWord(verse.words?.[0] || null);
  }, [verse]);

  useEffect(() => {
    // Always show hint for testing
    setShowWordHint(true);
  }, []);

  const handleNavigationSelect = useCallback(
    (bookId: string, chapter: number, verseNum: number) => {
      // Find the verse in the ordered list
      const allBookVerses = mockVerses.filter((v) => v.bookId === bookId);
      const targetVerse = allBookVerses.find(
        (v) => v.chapter === chapter && v.verse === verseNum,
      );
      if (targetVerse) {
        setCurrentVerseId(targetVerse.id);
        // If same book, scroll to it
        if (bookId === verse.bookId) {
          const nextIndex = orderedVerses.findIndex(
            (item) => item.id === targetVerse.id,
          );
          if (nextIndex >= 0) {
            listRef.current?.scrollToIndex({
              index: nextIndex,
              animated: true,
            });
          }
        }
      }
    },
    [orderedVerses, setCurrentVerseId, verse.bookId],
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
              onBookPress={() => navigationSheetRef.current?.snapToIndex(0)}
              onChapterPress={() => navigationSheetRef.current?.snapToIndex(0)}
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
                    onVersePress={() =>
                      navigationSheetRef.current?.snapToIndex(0)
                    }
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
      <NavigationSheet
        sheetRef={navigationSheetRef}
        currentBookId={verse.bookId}
        currentChapter={verse.chapter}
        currentVerse={verse.verse}
        onSelectVerse={handleNavigationSelect}
      />
    </>
  );
};
