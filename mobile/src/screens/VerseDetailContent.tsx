import {
  memo,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  Alert,
  Animated,
  FlatList,
  Pressable,
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
import type { BottomSheetMethods } from "@gorhom/bottom-sheet/lib/typescript/types";
import { BottomTabBarHeightContext } from "@react-navigation/bottom-tabs";
import type { BottomTabNavigationProp } from "@react-navigation/bottom-tabs";
import type { ParamListBase } from "@react-navigation/native";
import { VerseCard } from "@/src/components/VerseCard";
import { WordAnalysisBottomSheet } from "@/src/components/WordAnalysisBottomSheet";
import {
  NavigationSheet,
  type NavigationSheetMethods,
} from "@/src/components/NavigationSheet";
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
import {
  loadBesorahDisclaimerCount,
  saveBesorahDisclaimerCount,
} from "@/src/services/storage";
import { formatBookDisplayName } from "../utils/bookNameFormatter";

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
  topPadding: number;
  showWordHint: boolean;
  isSelectedVerse: boolean;
  isBesorah: boolean;
  onVersePress: () => void;
  selectedWord: DisplayVerse["words"][number] | null;
  onWordPress: (word: DisplayVerse["words"][number] | null) => void;
  onBackgroundPress: () => void;
  onScrollBegin?: () => void;
};

const VersePageComponent = ({
  item,
  pageHeight,
  topPadding,
  showWordHint,
  isSelectedVerse,
  isBesorah,
  onVersePress,
  selectedWord,
  onWordPress,
  onBackgroundPress,
  onScrollBegin,
}: VersePageProps) => {
  const [contentHeight, setContentHeight] = useState(0);
  const horizontalPadding = spacing[4];
  const bottomPadding = spacing[8];
  const verticalPadding = topPadding + bottomPadding;
  const availableHeight = Math.max(0, pageHeight - verticalPadding);
  const canScroll = contentHeight > availableHeight + 1;

  const verseContent = (
    <Pressable
      onPress={onBackgroundPress}
      style={{
        paddingHorizontal: horizontalPadding,
        paddingTop: topPadding,
        paddingBottom: bottomPadding,
      }}
      onLayout={(event) => setContentHeight(event.nativeEvent.layout.height)}
    >
      <VerseCard
        verse={item}
        variant="detail"
        showWordHint={showWordHint && isSelectedVerse}
        selectedWord={isSelectedVerse ? selectedWord : null}
        isBesorah={isBesorah}
        onVersePress={onVersePress}
        onWordPress={onWordPress}
      />
    </Pressable>
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
          showsVerticalScrollIndicator={false}
          bounces={false}
          alwaysBounceVertical={false}
          overScrollMode="never"
          nestedScrollEnabled
          onScrollBeginDrag={onScrollBegin}
        >
          {verseContent}
        </ScrollView>
      ) : (
        <View
          style={{
            flex: 1,
            justifyContent: "flex-start",
            alignItems: "stretch",
          }}
        >
          {verseContent}
        </View>
      )}
    </View>
  );
};

const VersePage = memo(
  VersePageComponent,
  (prevProps, nextProps) =>
    prevProps.item.id === nextProps.item.id &&
    prevProps.pageHeight === nextProps.pageHeight &&
    prevProps.showWordHint === nextProps.showWordHint &&
    prevProps.isSelectedVerse === nextProps.isSelectedVerse &&
    prevProps.isBesorah === nextProps.isBesorah &&
    prevProps.selectedWord === nextProps.selectedWord &&
    prevProps.onVersePress === nextProps.onVersePress &&
    prevProps.onWordPress === nextProps.onWordPress &&
    prevProps.onBackgroundPress === nextProps.onBackgroundPress &&
    prevProps.onScrollBegin === nextProps.onScrollBegin,
);

export const VerseDetailContent = () => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const { t } = useTranslation();
  const { height: screenHeight } = useWindowDimensions();
  const insets = useSafeAreaInsets();
  const tabBarHeight = useContext(BottomTabBarHeightContext) ?? 0;
  const pageHeight = Math.max(0, screenHeight - insets.top - tabBarHeight);
  const params = useLocalSearchParams<{ id?: string | string[] }>();
  const currentVerseId = useAppStore((state: AppState) => state.currentVerseId);
  const setCurrentVerseId = useAppStore(
    (state: AppState) => state.setCurrentVerseId,
  );
  const language = useAppStore((state: AppState) => state.language);
  const showQumran = useAppStore((state: AppState) => state.showQumran);
  const isConnected = useAppStore((state: AppState) => state.isConnected);
  const DEFAULT_VERSE_ID = "genesis-1-1";
  const normalizeVerseId = (value?: string | null) => {
    if (!value) return DEFAULT_VERSE_ID;
    const [bookId, chapterValue, verseValue] = value.split("-");
    const chapterNumber = Number(chapterValue);
    const verseNumber = Number(verseValue);
    if (
      !bookId ||
      !Number.isFinite(chapterNumber) ||
      chapterNumber <= 0 ||
      !Number.isFinite(verseNumber) ||
      verseNumber <= 0
    ) {
      return DEFAULT_VERSE_ID;
    }
    return `${bookId}-${chapterNumber}-${verseNumber}`;
  };

  const paramId = Array.isArray(params.id) ? params.id[0] : params.id;
  const isStandaloneVerseDetailRoute = Boolean(paramId);

  // Standalone screens use local state so they never touch the global store
  const [localVerseId, setLocalVerseId] = useState(
    () => normalizeVerseId(paramId),
  );
  const effectiveVerseId = isStandaloneVerseDetailRoute
    ? localVerseId
    : normalizeVerseId(currentVerseId);
  const setEffectiveVerseId = isStandaloneVerseDetailRoute
    ? setLocalVerseId
    : setCurrentVerseId;

  // Keep refs current for the onViewableItemsChanged closure
  const effectiveVerseIdRef = useRef(effectiveVerseId);
  const setEffectiveVerseIdRef = useRef(setEffectiveVerseId);
  useEffect(() => {
    effectiveVerseIdRef.current = effectiveVerseId;
    setEffectiveVerseIdRef.current = setEffectiveVerseId;
  });

  const verseId = effectiveVerseId;
  const navigationRowTop = isStandaloneVerseDetailRoute
    ? spacing[1]
    : spacing[16];
  const contentTopPadding = isStandaloneVerseDetailRoute
    ? spacing[10]
    : navigationRowTop + spacing[12];

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
  const isBesorah = bookMeta?.section === "besorah";
  const previousBookSectionRef = useRef<string | null>(null);

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

  const [showWordHint] = useState(false);
  const listRef = useRef<FlatList<(typeof orderedVerses)[number]>>(null);
  const viewabilityConfigRef = useRef({ itemVisiblePercentThreshold: 70 });
  const onViewableItemsChanged = useRef(
    ({
      viewableItems,
    }: {
      viewableItems: { item: (typeof orderedVerses)[number] }[];
    }) => {
      const next = viewableItems[0]?.item;
      if (next && next.id !== effectiveVerseIdRef.current) {
        setEffectiveVerseIdRef.current(next.id);
      }
    },
  );
  const sheetRef = useRef<BottomSheetMethods>(null!);
  const navigationSheetRef = useRef<NavigationSheetMethods>(null!);
  const [selectedWord, setSelectedWord] = useState<
    (typeof orderedVerses)[number]["words"][number] | null
  >(null);
  const pillVisibility = useRef(new Animated.Value(1)).current;
  const [pillVisible, setPillVisible] = useState(true);

  const animatePill = useCallback(
    (nextVisible: boolean) => {
      setPillVisible(nextVisible);
      Animated.timing(pillVisibility, {
        toValue: nextVisible ? 1 : 0,
        duration: 220,
        useNativeDriver: true,
      }).start();
    },
    [pillVisibility],
  );

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

  useEffect(() => {
    const currentSection = bookMeta?.section ?? null;
    const previousSection = previousBookSectionRef.current;
    const enteredBesorahFromTanaj =
      Boolean(previousSection) &&
      previousSection !== "besorah" &&
      currentSection === "besorah";

    if (enteredBesorahFromTanaj) {
      void (async () => {
        const shownCount = await loadBesorahDisclaimerCount();
        if (shownCount >= 3) {
          return;
        }

        Alert.alert(
          t("verse.besorahDisclaimer.modalTitle"),
          t("verse.besorahDisclaimer.modalMessage"),
          [{ text: t("verse.besorahDisclaimer.modalConfirm") }],
          { cancelable: true },
        );

        await saveBesorahDisclaimerCount(shownCount + 1);
      })();
    }

    if (currentSection) {
      previousBookSectionRef.current = currentSection;
    }
  }, [bookMeta?.section, t]);

  const handleNavigationSelect = useCallback(
    (nextBookId: string, nextChapter: number, verseNum: number) => {
      const targetId = `${nextBookId}-${nextChapter}-${verseNum}`;
      setEffectiveVerseId(targetId);
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
    [orderedVerses, setEffectiveVerseId, bookId, chapter],
  );

  // Track when a word was just selected to prevent race condition with sheet's onClose
  const justSelectedWordRef = useRef(false);

  const handleWordPress = useCallback(
    (word: typeof selectedWord) => {
      if (!word) return;

      const isSameWord =
        selectedWord?.position === word.position &&
        selectedWord?.text === word.text &&
        selectedWord?.strong === word.strong;

      navigationSheetRef.current?.close();

      if (isSameWord) {
        justSelectedWordRef.current = false;
        setSelectedWord(null);
        sheetRef.current?.close();
        return;
      }

      justSelectedWordRef.current = true;
      setSelectedWord(word);
      if (sheetRef.current) {
        sheetRef.current.snapToIndex(0);
      }
    },
    [selectedWord],
  );

  // Open the word analysis sheet whenever a word is selected
  useEffect(() => {
    if (selectedWord && sheetRef.current) {
      sheetRef.current.snapToIndex(0);
    }
  }, [selectedWord]);

  // Handle sheet close - only clear selectedWord if it wasn't just set
  const handleSheetClosed = useCallback(() => {
    if (justSelectedWordRef.current) {
      // A new word was just selected, don't clear it
      justSelectedWordRef.current = false;
      return;
    }
    // Normal close (user swiped down or tapped backdrop) - clear the selection
    setSelectedWord(null);
  }, []);

  const handleBackgroundPress = useCallback(() => {
    animatePill(true);
  }, [animatePill]);

  const handleScrollBegin = useCallback(() => {
    if (pillVisible) {
      animatePill(false);
    }
  }, [animatePill, pillVisible]);

  const handleOpenNavigationSheet = useCallback(() => {
    navigationSheetRef.current?.snapToIndex(0);
  }, []);

  const keyExtractor = useCallback(
    (item: (typeof orderedVerses)[number]) => item.id,
    [],
  );

  const renderVersePage = useCallback(
    ({ item }: { item: (typeof orderedVerses)[number] }) => (
      <VersePage
        item={item}
        pageHeight={pageHeight}
        topPadding={contentTopPadding}
        showWordHint={showWordHint}
        isSelectedVerse={item.id === verse?.id}
        isBesorah={isBesorah}
        selectedWord={selectedWord}
        onVersePress={handleOpenNavigationSheet}
        onWordPress={handleWordPress}
        onBackgroundPress={handleBackgroundPress}
        onScrollBegin={handleScrollBegin}
      />
    ),
    [
      pageHeight,
      contentTopPadding,
      showWordHint,
      verse?.id,
      isBesorah,
      selectedWord,
      handleOpenNavigationSheet,
      handleWordPress,
      handleBackgroundPress,
      handleScrollBegin,
    ],
  );

  // Clear selectedWord immediately when verse changes to prevent stale word display
  const prevVerseIdRef = useRef(effectiveVerseId);
  useEffect(() => {
    if (prevVerseIdRef.current !== effectiveVerseId) {
      const prevBookId = prevVerseIdRef.current?.split("-")[0];
      const newBookId = effectiveVerseId?.split("-")[0];
      // Only clear if book actually changed (not just verse within same chapter)
      if (prevBookId !== newBookId) {
        setSelectedWord(null);
        sheetRef.current?.close();
      }
      prevVerseIdRef.current = effectiveVerseId;
    }
  }, [effectiveVerseId]);

  const currentLoadRef = useRef({
    bookId: "",
    chapter: 0,
    language: "en" as AppState["language"],
    showQumran: false,
    isConnected: true,
  });
  useEffect(() => {
    if (!bookId) return;
    if (
      currentLoadRef.current.bookId === bookId &&
      currentLoadRef.current.chapter === chapter &&
      currentLoadRef.current.language === language &&
      currentLoadRef.current.showQumran === showQumran &&
      currentLoadRef.current.isConnected === isConnected
    ) {
      return;
    }

    let isMounted = true;
    currentLoadRef.current = {
      bookId,
      chapter,
      language,
      showQumran,
      isConnected,
    };

    const loadVerses = async () => {
      setChapterVerses([]);
      setSelectedWord(null);
      setIsLoading(true);
      setErrorMessage(null);
      sheetRef.current?.close();

      try {
        const hideTranslations = language === "he";
        const verses = await fetchChapterVerses(bookId, chapter, {
          language: hideTranslations ? undefined : language,
          showDss: showQumran,
          hebrewOnly: hideTranslations,
          isConnected,
        });
        if (!isMounted) return;
        if (
          currentLoadRef.current.bookId !== bookId ||
          currentLoadRef.current.chapter !== chapter ||
          currentLoadRef.current.language !== language ||
          currentLoadRef.current.showQumran !== showQumran ||
          currentLoadRef.current.isConnected !== isConnected
        ) {
          return;
        }
        setChapterVerses(verses);
        // Don't auto-select a word - let user tap to select
      } catch {
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
  }, [bookId, chapter, language, showQumran, isConnected, t]);

  return (
    <>
      <SafeAreaView style={styles.safeArea} edges={isStandaloneVerseDetailRoute ? [] : ["top"]}>
        <View style={styles.container}>
          <View style={[styles.navigationRow, { top: navigationRowTop }]}>
            <Animated.View
              pointerEvents={pillVisible ? "auto" : "none"}
              style={{
                opacity: pillVisibility,
                transform: [
                  {
                    translateY: pillVisibility.interpolate({
                      inputRange: [0, 1],
                      outputRange: [-12, 0],
                    }),
                  },
                ],
              }}
            >
              <BookChapterPill
                bookLabel={formatBookDisplayName(
                  language === "es"
                    ? (bookMeta?.spanish_name ?? t("common.loading"))
                    : (bookMeta?.name ?? t("common.loading")),
                )}
                hebrewLabel={bookMeta?.hebrew_name ?? ""}
                chapter={verse?.chapter ?? chapter}
                onBookPress={() => navigationSheetRef.current?.snapToIndex(0)}
                onChapterPress={() =>
                  navigationSheetRef.current?.openAtChapter()
                }
              />
            </Animated.View>
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
            keyExtractor={keyExtractor}
            renderItem={renderVersePage}
            pagingEnabled
            showsVerticalScrollIndicator={false}
            decelerationRate="fast"
            snapToInterval={pageHeight}
            snapToAlignment="start"
            removeClippedSubviews
            windowSize={5}
            initialNumToRender={3}
            maxToRenderPerBatch={4}
            updateCellsBatchingPeriod={50}
            initialScrollIndex={Math.max(currentIndex, 0)}
            getItemLayout={(_, index) => ({
              length: pageHeight,
              offset: pageHeight * index,
              index,
            })}
            viewabilityConfig={viewabilityConfigRef.current}
            onViewableItemsChanged={onViewableItemsChanged.current}
            onScrollBeginDrag={handleScrollBegin}
            onMomentumScrollBegin={handleScrollBegin}
          />
        </View>
      </SafeAreaView>
      <WordAnalysisBottomSheet
        ref={sheetRef}
        word={selectedWord}
        currentVerseId={effectiveVerseId}
        isBesorah={isBesorah}
        onClosed={handleSheetClosed}
      />
      <NavigationSheet
        ref={navigationSheetRef}
        currentBookId={verse?.bookId ?? bookId}
        currentChapter={verse?.chapter ?? chapter}
        currentVerse={verse?.verse ?? verseNumber}
        onSelectVerse={handleNavigationSelect}
      />
    </>
  );
};
