import React, { useCallback, useMemo, useState } from "react";
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
import { mockBooks, type MockBook } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type BookSelectorSheetProps = {
  sheetRef: React.RefObject<BottomSheet | null>;
  currentBookId?: string;
  onSelectBook: (bookId: string) => void;
  onClose?: () => void;
};

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
  const [searchQuery, setSearchQuery] = useState("");

  const filteredBooks = useMemo(() => {
    if (!searchQuery.trim()) {
      return mockBooks;
    }
    const query = searchQuery.toLowerCase();
    return mockBooks.filter(
      (book) =>
        book.name.toLowerCase().includes(query) ||
        stripNikud(book.hebrewName).includes(query) ||
        book.hebrewName.includes(query),
    );
  }, [searchQuery]);

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
        setSearchQuery("");
        onClose?.();
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
    ({ item }: { item: MockBook }) => {
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
          <Text style={styles.bookHebrew}>{stripNikud(item.hebrewName)}</Text>
        </Pressable>
      );
    },
    [currentBookId, handleSelectBook, styles, colors],
  );

  const renderListEmpty = useCallback(
    () => (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No books found</Text>
      </View>
    ),
    [styles],
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
          <Text style={styles.title}>Select Book</Text>
          <Pressable
            style={styles.closeButton}
            onPress={() => sheetRef.current?.close()}
          >
            <Ionicons name="close" size={18} color={colors.textSecondary} />
          </Pressable>
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
            placeholder="Search books..."
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
        keyExtractor={(item: MockBook) => item.id}
        renderItem={renderBookItem}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={renderListEmpty}
        keyboardShouldPersistTaps="handled"
      />
    </BottomSheet>
  );
};
