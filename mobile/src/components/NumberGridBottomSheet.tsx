import React, { useCallback, useMemo } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import BottomSheet, {
  BottomSheetBackdrop,
  BottomSheetView,
  type BottomSheetBackdropProps,
} from "@gorhom/bottom-sheet";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type NumberGridBottomSheetProps = {
  sheetRef: React.RefObject<BottomSheet | null>;
  title: string;
  numbers: number[];
  selected: number;
  onSelect: (value: number) => void;
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
      borderTopLeftRadius: 24,
      borderTopRightRadius: 24,
    },
    handleIndicator: {
      backgroundColor: colors.border,
    },
    title: {
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
  });

export const NumberGridBottomSheet = ({
  sheetRef,
  title,
  numbers,
  selected,
  onSelect,
}: NumberGridBottomSheetProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const snapPoints = useMemo(() => ["55%"], []);

  const paddedNumbers = useMemo(() => {
    const remainder = numbers.length % COLUMN_COUNT;
    if (remainder === 0) {
      return numbers;
    }
    const fillerCount = COLUMN_COUNT - remainder;
    return numbers.concat(Array.from({ length: fillerCount }, () => -1));
  }, [numbers]);

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
      keyboardBehavior="extend"
      keyboardBlurBehavior="none"
    >
      <BottomSheetView style={styles.sheetContent}>
        <Text style={styles.title}>{title}</Text>
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
      </BottomSheetView>
    </BottomSheet>
  );
};
