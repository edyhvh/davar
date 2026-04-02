import React, { useCallback, useMemo, useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import BottomSheet, {
  BottomSheetBackdrop,
  BottomSheetScrollView,
  type BottomSheetBackdropProps,
} from "@gorhom/bottom-sheet";
import { Ionicons } from "@expo/vector-icons";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { useTranslation } from "@/src/i18n/useTranslation";

type VerseSelectorSheetProps = {
  sheetRef: React.RefObject<BottomSheet | null>;
  title: string;
  numbers: number[];
  selected: number;
  onSelect: (value: number) => void;
  onBack?: () => void;
  onClose?: () => void;
};

const COLUMN_COUNT = 5;

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    sheetContent: {
      paddingHorizontal: spacing[6],
      paddingBottom: spacing[8],
      flex: 1,
    },
    sheetBackground: {
      backgroundColor: colors.surface,
      borderTopLeftRadius: radii.xl,
      borderTopRightRadius: radii.xl,
    },
    handleIndicator: {
      backgroundColor: colors.border,
    },
    header: {
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
    title: {
      flex: 1,
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      letterSpacing: 1,
      textTransform: "uppercase",
      textAlign: "center",
    },
    placeholder: {
      width: 32,
    },
    searchContainer: {
      flexDirection: "row",
      alignItems: "center",
      backgroundColor: colors.neomorphBg,
      borderRadius: radii.full,
      paddingHorizontal: spacing[4],
      minHeight: 44,
      borderWidth: 1,
      borderColor: colors.neomorphBorder,
      marginBottom: spacing[4],
    },
    searchIcon: {
      marginRight: spacing[2],
    },
    searchInput: {
      flex: 1,
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
      paddingVertical: spacing[2],
    },
    clearButton: {
      padding: spacing[1],
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

export const VerseSelectorSheet = ({
  sheetRef,
  title,
  numbers,
  selected,
  onSelect,
  onBack,
  onClose,
}: VerseSelectorSheetProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const snapPoints = useMemo(() => ["65%"], []);
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredNumbers = useMemo(() => {
    if (!searchQuery.trim()) {
      return numbers;
    }
    const query = searchQuery.trim();
    return numbers.filter((num) => num.toString().includes(query));
  }, [numbers, searchQuery]);

  const paddedNumbers = useMemo(() => {
    const remainder = filteredNumbers.length % COLUMN_COUNT;
    if (remainder === 0) {
      return filteredNumbers;
    }
    const fillerCount = COLUMN_COUNT - remainder;
    return filteredNumbers.concat(
      Array.from({ length: fillerCount }, () => -1),
    );
  }, [filteredNumbers]);

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

  const handleBack = useCallback(() => {
    sheetRef.current?.close();
    onBack?.();
  }, [sheetRef, onBack]);

  return (
    <BottomSheet
      ref={sheetRef}
      index={-1}
      snapPoints={snapPoints}
      enablePanDownToClose
      enableContentPanningGesture={false}
      backgroundStyle={styles.sheetBackground}
      handleIndicatorStyle={styles.handleIndicator}
      backdropComponent={renderBackdrop}
      onChange={handleSheetChanges}
      keyboardBehavior="extend"
      keyboardBlurBehavior="none"
    >
      <BottomSheetScrollView
        style={styles.sheetContent}
        nestedScrollEnabled
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          {onBack ? (
            <Pressable style={styles.backButton} onPress={handleBack}>
              <Ionicons
                name="arrow-back"
                size={18}
                color={colors.textSecondary}
              />
            </Pressable>
          ) : (
            <View style={styles.placeholder} />
          )}
          <Text style={styles.title}>{title}</Text>
          <View style={styles.placeholder} />
        </View>

        <View style={styles.searchContainer}>
          <Ionicons
            name="search"
            size={18}
            color={colors.textSecondary}
            style={styles.searchIcon}
          />
          <TextInput
            style={styles.searchInput}
            placeholder={t("navigation.search")}
            placeholderTextColor={colors.textSecondary}
            value={searchQuery}
            onChangeText={setSearchQuery}
            keyboardType="number-pad"
            autoCorrect={false}
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

        {filteredNumbers.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>{t("navigation.noResults")}</Text>
          </View>
        ) : (
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
        )}
        </BottomSheetScrollView>
    </BottomSheet>
  );
};
