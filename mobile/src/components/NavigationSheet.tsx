import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import BottomSheet, {
  BottomSheetBackdrop,
  BottomSheetFlatList,
  BottomSheetView,
  type BottomSheetBackdropProps,
} from "@gorhom/bottom-sheet";
import { Ionicons } from "@expo/vector-icons";
import Animated, {
  SlideInRight,
  SlideInLeft,
  SlideOutLeft,
  SlideOutRight,
} from "react-native-reanimated";

import {
  getColors,
  getNeumorphShadowStyle,
  radii,
  spacing,
  typography,
} from "@/src/theme";
import { fetchMetadata } from "@/src/services/metadata";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type NavigationSheetProps = {
  sheetRef: React.RefObject<BottomSheet | null>;
  currentBookId: string;
  currentChapter: number;
  currentVerse: number;
  onSelectVerse: (bookId: string, chapter: number, verse: number) => void;
  onClose?: () => void;
};

type Step = "book" | "chapter" | "verse";

type BookMeta = {
  id: string;
  name: string;
  hebrewName: string;
};

const COLUMN_COUNT = 5;

const stripNikud = (value: string) =>
  value.normalize("NFD").replace(/[\u0591-\u05C7]/g, "");

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    sheetBackground: {
      backgroundColor: colors.surface,
      borderTopLeftRadius: radii.xl,
      borderTopRightRadius: radii.xl,
    },
    sheetHandle: {
      backgroundColor: colors.border,
    },
    header: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[4],
      paddingBottom: spacing[4],
    },
    titleRow: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: spacing[4],
    },
    backButton: {
      width: 32,
      height: 32,
      borderRadius: 16,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    backButtonHidden: {
      opacity: 0,
    },
    title: {
      flex: 1,
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.h3,
      color: colors.textPrimary,
      fontWeight: typography.weights.semibold,
      textAlign: "center",
    },
    closeButton: {
      width: 32,
      height: 32,
      borderRadius: 16,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    breadcrumb: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
      gap: spacing[2],
      marginBottom: spacing[4],
    },
    breadcrumbItem: {
      paddingVertical: spacing[1],
      paddingHorizontal: spacing[3],
      borderRadius: radii.full,
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
    },
    breadcrumbItemActive: {
      backgroundColor: colors.primaryLight,
      borderColor: colors.primary,
    },
    breadcrumbText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      color: colors.textSecondary,
    },
    breadcrumbTextActive: {
      color: colors.primary,
      fontWeight: typography.weights.medium,
    },
    breadcrumbArrow: {
      color: colors.textSecondary,
    },
    searchContainer: {
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: colors.neomorphBg,
      borderRadius: radii.full,
      paddingHorizontal: spacing[4],
      minHeight: 48,
      borderWidth: 1,
      borderColor: colors.neomorphBorder,
    },
    searchIcon: {
      marginRight: spacing[2],
    },
    searchInput: {
      flex: 1,
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      paddingVertical: spacing[3],
    },
    clearButton: {
      padding: spacing[1],
    },
    content: {
      flex: 1,
    },
    listContent: {
      paddingHorizontal: spacing[6],
      paddingBottom: spacing[8],
    },
    bookItem: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingVertical: spacing[4],
      paddingHorizontal: spacing[4],
      marginBottom: spacing[3],
      backgroundColor: colors.surface,
      borderRadius: radii.lg,
      borderWidth: 1,
      borderColor: colors.border,
    },
    bookItemSelected: {
      backgroundColor: colors.primaryLight,
      borderColor: colors.primary,
    },
    bookEnglish: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      fontWeight: typography.weights.medium,
    },
    bookHebrew: {
      fontFamily: typography.families.hebrewUI,
      fontSize: typography.sizes.h3,
      color: colors.textPrimary,
      textAlign: "right",
      writingDirection: "rtl",
    },
    gridContainer: {
      paddingHorizontal: spacing[6],
      paddingBottom: spacing[8],
    },
    gridTitle: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      letterSpacing: 1,
      textTransform: "uppercase",
      textAlign: "center",
      marginBottom: spacing[4],
    },
    grid: {
      flexDirection: "row",
      flexWrap: "wrap",
      justifyContent: "center",
      gap: spacing[3],
    },
    cell: {
      width: 52,
      height: 52,
      borderRadius: radii.md,
      alignItems: "center",
      justifyContent: "center",
      borderWidth: 1,
      borderColor: colors.border,
      backgroundColor: colors.surface,
    },
    cellPlaceholder: {
      opacity: 0,
    },
    cellSelected: {
      backgroundColor: colors.primary,
      borderColor: colors.primary,
    },
    cellLabel: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
    },
    cellLabelSelected: {
      color: colors.background,
      fontWeight: typography.weights.medium,
    },
    emptyContainer: {
      alignItems: "center",
      paddingVertical: spacing[8],
    },
    emptyText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textSecondary,
    },
  });

export const NavigationSheet = ({
  sheetRef,
  currentBookId,
  currentChapter,
  currentVerse,
  onSelectVerse,
  onClose,
}: NavigationSheetProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const snapPoints = useMemo(() => ["70%", "90%"], []);

  const [step, setStep] = useState<Step>("book");
  const [selectedBookId, setSelectedBookId] = useState(currentBookId);
  const [selectedChapter, setSelectedChapter] = useState(currentChapter);
  const [searchQuery, setSearchQuery] = useState("");
  const [direction, setDirection] = useState<"forward" | "backward">("forward");
  const [booksMeta, setBooksMeta] = useState<BookMeta[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [chapterCounts, setChapterCounts] = useState<Record<string, number[]>>(
    {},
  );
  const [verseCounts, setVerseCounts] = useState<
    Record<string, Record<string, number>>
  >({});

  useEffect(() => {
    let isMounted = true;
    const loadMetadata = async () => {
      try {
        const metadata = await fetchMetadata();
        if (!isMounted) return;
        const mappedBooks = metadata.books.map((book) => ({
          id: book.id,
          name: book.name,
          hebrewName: book.hebrew_name,
        }));
        setBooksMeta(mappedBooks);
        setLoadError(null);
        setChapterCounts(metadata.chapter_counts ?? {});
        setVerseCounts(metadata.verse_counts ?? {});
      } catch {
        if (!isMounted) return;
        setBooksMeta([]);
        setChapterCounts({});
        setVerseCounts({});
        setLoadError("Unable to load books from the server.");
      }
    };
    loadMetadata();
    return () => {
      isMounted = false;
    };
  }, []);

  // Get selected book info
  const selectedBook = useMemo(
    () => booksMeta.find((b) => b.id === selectedBookId),
    [booksMeta, selectedBookId],
  );

  // Filter books by search
  const filteredBooks = useMemo(() => {
    if (!searchQuery.trim()) {
      return booksMeta;
    }
    const query = searchQuery.toLowerCase();
    return booksMeta.filter(
      (book) =>
        book.name.toLowerCase().includes(query) ||
        stripNikud(book.hebrewName).includes(query) ||
        book.hebrewName.includes(query),
    );
  }, [booksMeta, searchQuery]);

  // Get chapters for selected book
  const chapterNumbers = useMemo(() => {
    const chapters = chapterCounts[selectedBookId];
    if (chapters?.length) return chapters;
    return [];
  }, [chapterCounts, selectedBookId]);

  // Get verses for selected chapter
  const verseNumbers = useMemo(() => {
    const count = verseCounts[selectedBookId]?.[String(selectedChapter)];
    if (count) return Array.from({ length: count }, (_, i) => i + 1);
    return [];
  }, [selectedBookId, selectedChapter, verseCounts]);

  // Pad numbers for grid
  const padNumbers = useCallback((numbers: number[]) => {
    const remainder = numbers.length % COLUMN_COUNT;
    if (remainder === 0) return numbers;
    const fillerCount = COLUMN_COUNT - remainder;
    return numbers.concat(Array.from({ length: fillerCount }, () => -1));
  }, []);

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

  const [isOpen, setIsOpen] = useState(false);

  const handleSheetChanges = useCallback(
    (index: number) => {
      console.debug("NavigationSheet onChange", { index });
      if (index === -1) {
        // Reset state when closed
        setStep("book");
        setSearchQuery("");
        setSelectedBookId(currentBookId);
        setSelectedChapter(currentChapter);
        setIsOpen(false);
        onClose?.();
      } else {
        setIsOpen(true);
      }
    },
    [onClose, currentBookId, currentChapter],
  );

  const handleBack = useCallback(() => {
    setDirection("backward");
    if (step === "verse") {
      setStep("chapter");
    } else if (step === "chapter") {
      setStep("book");
    }
  }, [step]);

  const handleSelectBook = useCallback((bookId: string) => {
    setSelectedBookId(bookId);
    setDirection("forward");
    setSearchQuery("");
    setStep("chapter");
  }, []);

  const handleSelectChapter = useCallback((chapter: number) => {
    setSelectedChapter(chapter);
    setDirection("forward");
    setStep("verse");
  }, []);

  const handleSelectVerse = useCallback(
    (verse: number) => {
      onSelectVerse(selectedBookId, selectedChapter, verse);
      sheetRef.current?.close();
    },
    [selectedBookId, selectedChapter, onSelectVerse, sheetRef],
  );

  const renderBookItem = useCallback(
    ({ item }: { item: BookMeta }) => {
      const isSelected = item.id === selectedBookId;
      return (
        <Pressable
          onPress={() => handleSelectBook(item.id)}
          style={({ pressed }) => [
            styles.bookItem,
            isSelected && styles.bookItemSelected,
            pressed
              ? getNeumorphShadowStyle("pressed", colors)
              : getNeumorphShadowStyle("raised", colors),
          ]}
        >
          <Text style={styles.bookEnglish}>{item.name}</Text>
          <Text style={styles.bookHebrew}>{stripNikud(item.hebrewName)}</Text>
        </Pressable>
      );
    },
    [selectedBookId, handleSelectBook, styles, colors],
  );

  const renderNumberGrid = useCallback(
    (numbers: number[], selected: number, onSelect: (n: number) => void) => {
      const paddedNumbers = padNumbers(numbers);
      return (
        <View style={styles.grid}>
          {paddedNumbers.map((value, index) => {
            if (value === -1) {
              return (
                <View
                  key={`empty-${index}`}
                  style={[styles.cell, styles.cellPlaceholder]}
                />
              );
            }
            const isSelected = value === selected;
            return (
              <Pressable
                key={value}
                onPress={() => onSelect(value)}
                style={[styles.cell, isSelected && styles.cellSelected]}
              >
                <Text
                  style={[
                    styles.cellLabel,
                    isSelected && styles.cellLabelSelected,
                  ]}
                >
                  {value}
                </Text>
              </Pressable>
            );
          })}
        </View>
      );
    },
    [padNumbers, styles],
  );

  const getTitle = () => {
    switch (step) {
      case "book":
        return "Select Book";
      case "chapter":
        return selectedBook?.name ?? "Select Chapter";
      case "verse":
        return `${selectedBook?.name ?? ""} ${selectedChapter}`;
    }
  };

  const enteringAnim = direction === "forward" ? SlideInRight : SlideInLeft;
  const exitingAnim = direction === "forward" ? SlideOutLeft : SlideOutRight;

  return (
    <BottomSheet
      ref={sheetRef}
      index={-1}
      snapPoints={snapPoints}
      enablePanDownToClose
      backgroundStyle={styles.sheetBackground}
      handleIndicatorStyle={styles.sheetHandle}
      onChange={handleSheetChanges}
      backdropComponent={renderBackdrop}
      keyboardBehavior="interactive"
      keyboardBlurBehavior="restore"
      animateOnMount={false}
    >
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Pressable
            style={[
              styles.backButton,
              step === "book" && styles.backButtonHidden,
            ]}
            onPress={handleBack}
            disabled={step === "book"}
          >
            <Ionicons
              name="arrow-back"
              size={18}
              color={colors.textSecondary}
            />
          </Pressable>
          <Text style={styles.title}>{getTitle()}</Text>
          {isOpen && (
            <Pressable
              style={styles.closeButton}
              onPress={() => sheetRef.current?.close()}
              testID="navigation-close-button"
            >
              <Ionicons name="close" size={18} color={colors.textSecondary} />
            </Pressable>
          )}
        </View>

        {/* Breadcrumb */}
        <View style={styles.breadcrumb}>
          <Pressable
            style={[
              styles.breadcrumbItem,
              step === "book" && styles.breadcrumbItemActive,
            ]}
            onPress={() => {
              setDirection("backward");
              setStep("book");
            }}
          >
            <Text
              style={[
                styles.breadcrumbText,
                step === "book" && styles.breadcrumbTextActive,
              ]}
            >
              {selectedBook?.name ?? "Book"}
            </Text>
          </Pressable>
          <Ionicons
            name="chevron-forward"
            size={14}
            color={colors.textSecondary}
          />
          <Pressable
            style={[
              styles.breadcrumbItem,
              step === "chapter" && styles.breadcrumbItemActive,
            ]}
            onPress={() => {
              if (selectedBookId) {
                setDirection(step === "verse" ? "backward" : "forward");
                setStep("chapter");
              }
            }}
            disabled={!selectedBookId}
          >
            <Text
              style={[
                styles.breadcrumbText,
                step === "chapter" && styles.breadcrumbTextActive,
              ]}
            >
              {selectedChapter || "Ch"}
            </Text>
          </Pressable>
          <Ionicons
            name="chevron-forward"
            size={14}
            color={colors.textSecondary}
          />
          <View
            style={[
              styles.breadcrumbItem,
              step === "verse" && styles.breadcrumbItemActive,
            ]}
          >
            <Text
              style={[
                styles.breadcrumbText,
                step === "verse" && styles.breadcrumbTextActive,
              ]}
            >
              Verse
            </Text>
          </View>
        </View>

        {/* Search - only for books */}
        {step === "book" && (
          <View
            style={[
              styles.searchContainer,
              getNeumorphShadowStyle("pressed", colors),
            ]}
          >
            <Ionicons
              name="search"
              size={18}
              color={colors.textSecondary}
              style={styles.searchIcon}
            />
            <TextInput
              style={styles.searchInput}
              placeholder="Search books..."
              placeholderTextColor={colors.textSecondary}
              value={searchQuery}
              onChangeText={setSearchQuery}
              autoCorrect={false}
              autoCapitalize="none"
              returnKeyType="search"
            />
            {searchQuery.length > 0 && (
              <Pressable
                style={styles.clearButton}
                onPress={() => setSearchQuery("")}
              >
                <Ionicons
                  name="close-circle"
                  size={18}
                  color={colors.textSecondary}
                />
              </Pressable>
            )}
          </View>
        )}
      </View>

      {/* Content based on step */}
      {step === "book" && (
        <Animated.View
          key="book-list"
          entering={enteringAnim.duration(200)}
          exiting={exitingAnim.duration(200)}
          style={styles.content}
        >
          <BottomSheetFlatList
            data={filteredBooks}
            keyExtractor={(item: BookMeta) => item.id}
            renderItem={renderBookItem}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>
                  {loadError ?? "No books found"}
                </Text>
              </View>
            }
            keyboardShouldPersistTaps="handled"
          />
        </Animated.View>
      )}

      {step === "chapter" && (
        <Animated.View
          key="chapter-grid"
          entering={enteringAnim.duration(200)}
          exiting={exitingAnim.duration(200)}
          style={styles.content}
        >
          <BottomSheetView style={styles.gridContainer}>
            <Text style={styles.gridTitle}>Select Chapter</Text>
            {chapterNumbers.length ? (
              renderNumberGrid(
                chapterNumbers,
                currentBookId === selectedBookId ? currentChapter : 0,
                handleSelectChapter,
              )
            ) : (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>No chapters available</Text>
              </View>
            )}
          </BottomSheetView>
        </Animated.View>
      )}

      {step === "verse" && (
        <Animated.View
          key="verse-grid"
          entering={enteringAnim.duration(200)}
          exiting={exitingAnim.duration(200)}
          style={styles.content}
        >
          <BottomSheetView style={styles.gridContainer}>
            <Text style={styles.gridTitle}>Select Verse</Text>
            {verseNumbers.length ? (
              renderNumberGrid(
                verseNumbers,
                currentBookId === selectedBookId &&
                  currentChapter === selectedChapter
                  ? currentVerse
                  : 0,
                handleSelectVerse,
              )
            ) : (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>No verses available</Text>
              </View>
            )}
          </BottomSheetView>
        </Animated.View>
      )}
    </BottomSheet>
  );
};
