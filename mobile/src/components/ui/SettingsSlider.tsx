import { useMemo } from "react";
import { StyleSheet, Text, View } from "react-native";
import Slider from "@react-native-community/slider";

import { getColors, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type SettingsSliderProps = {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
  helper?: string;
  previewText?: string;
};

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    container: {
      paddingHorizontal: spacing[6],
      paddingVertical: spacing[4],
    },
    label: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
    },
    helper: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      marginTop: spacing[2],
    },
    sliderRow: {
      marginTop: spacing[4],
    },
    value: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      color: colors.textSecondary,
      textAlign: "right",
    },
    preview: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: typography.sizes.hebrewVerseMedium,
      color: colors.textPrimary,
      textAlign: "right",
      writingDirection: "rtl",
      marginTop: spacing[4],
    },
  });

export const SettingsSlider = ({
  label,
  value,
  min,
  max,
  step,
  onChange,
  helper,
  previewText,
}: SettingsSliderProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);

  return (
    <View style={styles.container}>
      <Text style={styles.label}>{label}</Text>
      {helper ? <Text style={styles.helper}>{helper}</Text> : null}
      <View style={styles.sliderRow}>
        <Slider
          value={value}
          minimumValue={min}
          maximumValue={max}
          step={step}
          onValueChange={onChange}
          minimumTrackTintColor={colors.primary}
          maximumTrackTintColor={colors.border}
          thumbTintColor={colors.primaryDark}
        />
        <Text style={styles.value}>{Math.round(value)}pt</Text>
      </View>
      {previewText ? <Text style={styles.preview}>{previewText}</Text> : null}
    </View>
  );
};
