import { useMemo } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type OnOffButtonProps = {
  value: boolean;
  onChange: (value: boolean) => void;
};

const createStyles = (
  colors: ReturnType<typeof getColors>,
  active: boolean,
  activeColor: string,
) =>
  StyleSheet.create({
    container: {
      width: 64,
      alignItems: "center",
      gap: spacing[1],
    },
    circle: {
      width: 48,
      height: 48,
      borderRadius: radii.full,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: colors.surface,
      borderWidth: 1.5,
      borderColor: colors.border,
    },
    inner: {
      width: 16,
      height: 16,
      borderRadius: radii.full,
      backgroundColor: active ? activeColor : colors.border,
      // Shiny effect
      shadowColor: active ? activeColor : colors.border,
      shadowOffset: { width: 0, height: 0 },
      shadowOpacity: active ? 0.6 : 0.3,
      shadowRadius: 4,
      elevation: 4,
    },
    label: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      letterSpacing: 1,
      color: colors.textSecondary,
    },
  });

export const OnOffButton = ({ value, onChange }: OnOffButtonProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const activeColor = themeMode === "light" ? colors.accentCopper : colors.primary;
  const styles = useMemo(
    () => createStyles(colors, value, activeColor),
    [colors, value, activeColor],
  );

  return (
    <Pressable onPress={() => onChange(!value)} style={styles.container}>
      <View style={styles.circle}>
        <View style={styles.inner} />
      </View>
      <Text style={styles.label}>{value ? "ON" : "OFF"}</Text>
    </Pressable>
  );
};
