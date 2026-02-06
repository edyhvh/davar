import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  FlatList,
  ScrollView,
  StyleSheet,
  Text,
  View,
  useWindowDimensions,
} from "react-native";
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
import { fetchMetadata } from "@/src/services/metadata";
import type { BookResponse } from "@/src/types/api";
import {
  fetchChapterVerses,
  type DisplayVerse,
} from "@/src/services/scripture";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { useTranslation } from "@/src/i18n/useTranslation";

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

type VersePageProps = {
  item: DisplayVerse;
  pageHeight: number;
  centerOffset: number;
  showWordHint: boolean;
  isSelectedVerse: boolean;
  onVersePress: () => void;
  onWordPress: (word: DisplayVerse["words"][number] | null) => void;
};

const VersePage = ({
  item,
  pageHeight,
  centerOffset,
  showWordHint,
  isSelectedVerse,
  onVersePress,
  onWordPress,
}: VersePageProps) => {
  const [contentHeight, setContentHeight] = useState(0);
  const verticalPadding = spacing[8] * 2;
  const availableHeight = Math.max(0, pageHeight - verticalPadding);
  const canScroll = contentHeight > availableHeight + 1;

  const verseContent = (
    <View
      style={{
        paddingHorizontal: spacing[6],
        paddingVertical: spacing[8],
        transform: [{ translateY: centerOffset }],
      }}
      onLayout={(event) => setContentHeight(event.nativeEvent.layout.height)}
    >
      <VerseCard
        verse={item}
        variant="detail"
        showWordHint={showWordHint && isSelectedVerse}
        onVersePress={onVersePress}
        onWordPress={onWordPress}
      />
    </View>
  );

  return (
    <View
      style={{
        height: pageHeight,
        width: "100%",
      }}
    >
      {canScroll ? (
        <ScrollView
          contentContainerStyle={{
            paddingHorizontal: spacing[6],
            paddingVertical: spacing[8],
          }}
          showsVerticalScrollIndicator={false}
          bounces={false}
          alwaysBounceVertical={false}
          overScrollMode="never"
          nestedScrollEnabled
        >
          {verseContent}
        </ScrollView>
      ) : (
        <View
          style={{
            flex: 1,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          {verseContent}
        </View>
      )}
    </View>
  );
};

export const VerseDetailContent = () => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const { t } = useTranslation();
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
  const language = useAppStore((state: AppState) => state.language);
  const showQumran = useAppStore((state: AppState) => state.showQumran);
  const lastParamIdRef = useRef<string | null>(null);
  useEffect(() => {
    if (!params.id) return;
    if (lastParamIdRef.current === params.id) return;
    lastParamIdRef.current = params.id;
    if (params.id !== currentVerseId) {
      setCurrentVerseId(params.id as string);
    }
  }, [params.id, currentVerseId, setCurrentVerseId]);

  const verseId = currentVerseId || ((params.id as string) ?? "");
  const [chapterVerses, setChapterVerses] = useState<DisplayVerse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [booksMeta, setBooksMeta] = useState<BookResponse[]>([]);

  const parseVerseId = (id: string) => {
    const [bookId, chapterValue, verseValue] = id.split("-");
    return {
      bookId,
      chapter: Number(chapterValue || 1),
      verse: Number(verseValue || 1),
    };
  };

  const { bookId, chapter, verse: verseNumber } = parseVerseId(verseId);
  const verse =
    chapterVerses.find((item) => item.verse === verseNumber) ??
    chapterVerses[0];
  const bookMeta = useMemo(
    () =>
      booksMeta.find((book) => book.id === (verse?.bookId ?? bookId)) ?? null,
    [bookId, booksMeta, verse?.bookId],
  );

  const bookVerses = useMemo(() => chapterVerses, [chapterVerses]);
  const orderedVerses = useMemo(
    () =>
      [...bookVerses].sort(
        (a, b) => a.chapter - b.chapter || a.verse - b.verse,
      ),
    [bookVerses],
  );
  const currentIndex = useMemo(
    () => (verse ? orderedVerses.findIndex((item) => item.id === verse.id) : 0),
    [orderedVerses, verse],
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
    (typeof orderedVerses)[number]["words"][number] | null
  >(null);

  // Listen for tab press to open navigation sheet
  const navigation = useNavigation<BottomTabNavigationProp<ParamListBase>>();
  useEffect(() => {
    const unsubscribe = navigation.addListener(
      "tabPress",
      (e: TabPressEvent) => {
        // If we're already on this tab, open the navigation sheet
        if (navigation.isFocused()) {
          e.preventDefault();
          // Close word analysis sheet if it's open
          sheetRef.current?.close();
          navigationSheetRef.current?.snapToIndex(0);
        }
      },
    );
    return unsubscribe;
  }, [navigation]);

  useEffect(() => {
    // Always show hint for testing
    setShowWordHint(true);
  }, []);

  useEffect(() => {
    let isMounted = true;
    const loadBooks = async () => {
      try {
        const metadata = await fetchMetadata();
        if (!isMounted) return;
        setBooksMeta(metadata.books);
      } catch (error) {
        if (!isMounted) return;
        console.error("Failed to load books metadata:", error);
        setBooksMeta([]);
      }
    };
    loadBooks();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleNavigationSelect = useCallback(
    (nextBookId: string, nextChapter: number, verseNum: number) => {
      const targetId = `${nextBookId}-${nextChapter}-${verseNum}`;
      setCurrentVerseId(targetId);
      if (nextBookId === bookId && nextChapter === chapter) {
        const nextIndex = orderedVerses.findIndex(
          (item) => item.verse === verseNum,
        );
        if (nextIndex >= 0) {
          listRef.current?.scrollToIndex({
            index: nextIndex,
            animated: true,
          });
        }
      }
    },
    [orderedVerses, setCurrentVerseId, bookId, chapter],
  );

  const handleWordPress = useCallback((word: typeof selectedWord) => {
    // Close navigation sheet if it's open
    navigationSheetRef.current?.close();
    setSelectedWord(word);
    sheetRef.current?.expand();
  }, []);

  // Clear selectedWord immediately when currentVerseId changes to prevent stale word display
  const prevVerseIdRef = useRef(currentVerseId);
  useEffect(() => {
    if (prevVerseIdRef.current !== currentVerseId) {
      const prevBookId = prevVerseIdRef.current?.split("-")[0];
      const newBookId = currentVerseId?.split("-")[0];
      // Only clear if book actually changed (not just verse within same chapter)
      if (prevBookId !== newBookId) {
        setSelectedWord(null);
        sheetRef.current?.close();
      }
      prevVerseIdRef.current = currentVerseId;
    }
  }, [currentVerseId]);

  const currentLoadRef = useRef({ bookId: "", chapter: 0 });
  useEffect(() => {
    if (!bookId) return;
    if (
      currentLoadRef.current.bookId === bookId &&
      currentLoadRef.current.chapter === chapter
    ) {
      return;
    }

    let isMounted = true;
    currentLoadRef.current = { bookId, chapter };

    const loadVerses = async () => {
      setChapterVerses([]);
      setSelectedWord(null);
      setIsLoading(true);
      setErrorMessage(null);
      sheetRef.current?.close();

      try {
        const verses = await fetchChapterVerses(bookId, chapter, {
          language: language === "he" ? undefined : language,
          showDss: showQumran,
          hebrewOnly: false, // Always load translations; UI will control display
        });
        if (!isMounted) return;
        if (
          currentLoadRef.current.bookId !== bookId ||
          currentLoadRef.current.chapter !== chapter
        ) {
          return;
        }
        setChapterVerses(verses);
        if (verses.length > 0 && verses[0].words?.length > 0) {
          setSelectedWord(verses[0].words[0]);
        }
      } catch (error) {
        if (!isMounted) return;
        setErrorMessage(t("errors.loadVerses"));
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    loadVerses();
    return () => {
      isMounted = false;
    };
  }, [bookId, chapter, language, showQumran]);

  return (
    <>
      <SafeAreaView style={styles.safeArea} edges={["top", "bottom"]}>
        <View style={styles.container}>
          <View style={styles.navigationRow}>
            <BookChapterPill
              bookLabel={bookMeta?.name ?? t("common.loading")}
              hebrewLabel={bookMeta?.hebrew_name ?? ""}
              chapter={verse?.chapter ?? chapter}
              onBookPress={() => navigationSheetRef.current?.snapToIndex(0)}
              onChapterPress={() => navigationSheetRef.current?.snapToIndex(0)}
            />
          </View>
          {isLoading ? (
            <View
              style={{ paddingHorizontal: spacing[6], paddingTop: spacing[12] }}
            >
              <Text
                style={{ textAlign: "center", color: colors.textSecondary }}
              >
                {t("verse.loading")}
              </Text>
            </View>
          ) : null}
          {errorMessage ? (
            <View
              style={{ paddingHorizontal: spacing[6], paddingTop: spacing[12] }}
            >
              <Text
                style={{ textAlign: "center", color: colors.textSecondary }}
              >
                {errorMessage}
              </Text>
            </View>
          ) : null}
          <FlatList
            ref={listRef}
            data={orderedVerses}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <VersePage
                item={item}
                pageHeight={pageHeight}
                centerOffset={centerOffset}
                showWordHint={showWordHint}
                isSelectedVerse={item.id === verse?.id}
                onVersePress={() => navigationSheetRef.current?.snapToIndex(0)}
                onWordPress={handleWordPress}
              />
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
      {selectedWord ? (
        <WordAnalysisBottomSheet
          sheetRef={sheetRef}
          word={selectedWord}
          currentVerseId={currentVerseId}
          onClosed={() => setSelectedWord(null)}
        />
      ) : null}
      <NavigationSheet
        sheetRef={navigationSheetRef}
        currentBookId={verse?.bookId ?? bookId}
        currentChapter={verse?.chapter ?? chapter}
        currentVerse={verse?.verse ?? verseNumber}
        onSelectVerse={handleNavigationSelect}
      />
    </>
  );
};
