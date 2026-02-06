import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import BottomSheet, {
  BottomSheetBackdrop,
  BottomSheetFlatList,
  type BottomSheetBackdropProps,
} from "@gorhom/bottom-sheet";
import { Ionicons } from "@expo/vector-icons";

import {
  getColors,
  getNeumorphShadowStyle,
  radii,
  spacing,
  typography,
} from "@/src/theme";
import { getBooks } from "@/src/services/api";
import type { BookResponse } from "@/src/types/api";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { useTranslation } from "@/src/i18n/useTranslation";

type BookSelectorSheetProps = {
  sheetRef: React.RefObject<BottomSheet | null>;
  currentBookId?: string;
  onSelectBook: (bookId: string) => void;
  onClose?: () => void;
};

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
    title: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.h3,
      color: colors.textPrimary,
      fontWeight: typography.weights.semibold,
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

export const BookSelectorSheet = ({
  sheetRef,
  currentBookId,
  onSelectBook,
  onClose,
}: BookSelectorSheetProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const snapPoints = useMemo(() => ["70%", "90%"], []);
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");
  const [booksMeta, setBooksMeta] = useState<BookResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loadBooks = async () => {
      try {
        const books = await getBooks();
        if (!isMounted) return;
        setBooksMeta(books);
        setErrorMessage(null);
      } catch (error) {
        console.error("Failed to load books:", error);
        if (!isMounted) return;
        setBooksMeta([]);
        setErrorMessage(t("errors.loadBooks"));
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadBooks();
    return () => {
      isMounted = false;
    };
  }, []);

  const filteredBooks = useMemo(() => {
    if (!searchQuery.trim()) {
      return booksMeta;
    }
    const query = searchQuery.toLowerCase();
    return booksMeta.filter(
      (book) =>
        book.name.toLowerCase().includes(query) ||
        book.hebrew_name.toLowerCase().includes(query) ||
        book.hebrew_transliteration.toLowerCase().includes(query) ||
        book.spanish_name.toLowerCase().includes(query),
    );
  }, [booksMeta, searchQuery]);

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
      console.debug("BookSelectorSheet onChange", { index });
      if (index === -1) {
        setSearchQuery("");
        setIsOpen(false);
        onClose?.();
      } else {
        setIsOpen(true);
      }
    },
    [onClose],
  );

  const handleSelectBook = useCallback(
    (bookId: string) => {
      onSelectBook(bookId);
      sheetRef.current?.close();
    },
    [onSelectBook, sheetRef],
  );

  const renderBookItem = useCallback(
    ({ item }: { item: BookResponse }) => {
      const isSelected = item.id === currentBookId;
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
          <Text style={styles.bookHebrew}>{item.hebrew_name}</Text>
        </Pressable>
      );
    },
    [currentBookId, handleSelectBook, styles, colors],
  );

  const renderListEmpty = useCallback(
    () => (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>
          {loading
            ? t("navigation.loadingBooks")
            : (errorMessage ?? t("navigation.noBooksFound"))}
        </Text>
      </View>
    ),
    [styles, loading, errorMessage, t],
  );

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
    >
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.title}>{t("navigation.selectBook")}</Text>
          {isOpen && (
            <Pressable
              style={styles.closeButton}
              onPress={() => sheetRef.current?.close()}
              testID="bookselector-close-button"
            >
              <Ionicons name="close" size={18} color={colors.textSecondary} />
            </Pressable>
          )}
        </View>
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
            placeholder={t("navigation.searchBooks")}
            placeholderTextColor={colors.textSecondary}
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCorrect={false}
            autoCapitalize="none"
            returnKeyType="search"
            showSoftInputOnFocus={true}
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
      </View>
      <BottomSheetFlatList
        data={filteredBooks}
        keyExtractor={(item: BookResponse) => item.id}
        renderItem={renderBookItem}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={renderListEmpty}
        keyboardShouldPersistTaps="handled"
      />
    </BottomSheet>
  );
};
