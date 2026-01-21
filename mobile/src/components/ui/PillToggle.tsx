import { useEffect, useMemo } from "react";
import { Pressable, StyleSheet } from "react-native";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";

import { getColors, radii } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

type PillToggleProps = {
  value: boolean;
  onChange: (value: boolean) => void;
};

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    container: {
      width: 80,
      height: 40,
      borderRadius: radii.full,
      backgroundColor: colors.border,
      padding: 2,
      justifyContent: "center",
    },
    pill: {
      width: 38,
      height: 36,
      borderRadius: radii.full,
      borderWidth: 2,
      alignItems: "center",
      justifyContent: "center",
    },
    pillActive: {
      backgroundColor: colors.primary,
      borderColor: colors.primaryDeep,
    },
    pillInactive: {
      backgroundColor: colors.surface,
      borderColor: colors.border,
    },
    shadow: {
      shadowColor: colors.primary,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.3,
      shadowRadius: 4,
    },
  });

export const PillToggle = ({ value, onChange }: PillToggleProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const translateX = useSharedValue(value ? 40 : 0);

  useEffect(() => {
    translateX.value = withTiming(value ? 40 : 0, { duration: 300 });
  }, [translateX, value]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <Pressable onPress={() => onChange(!value)} style={styles.container}>
      <Animated.View
        style={[
          styles.pill,
          value ? styles.pillActive : styles.pillInactive,
          value && styles.shadow,
          animatedStyle,
        ]}
      />
    </Pressable>
  );
};
