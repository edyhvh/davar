import { useEffect, useMemo } from "react";
import { StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withSequence,
  withTiming,
} from "react-native-reanimated";

import { getColors, spacing } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    container: {
      position: "absolute",
      left: 0,
      right: 0,
      alignItems: "center",
      opacity: 0.5,
    },
    top: {
      top: spacing[6],
    },
    bottom: {
      bottom: spacing[6],
    },
    icon: {
      color: colors.textSecondary,
    },
  });

export const SwipeIndicators = () => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const offset = useSharedValue(0);

  useEffect(() => {
    offset.value = withRepeat(
      withSequence(
        withTiming(-6, { duration: 700 }),
        withTiming(0, { duration: 700 }),
      ),
      -1,
      true,
    );
  }, [offset]);

  const topStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: offset.value }],
  }));

  const bottomStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: -offset.value }],
  }));

  return (
    <>
      <Animated.View style={[styles.container, styles.top, topStyle]}>
        <Ionicons name="chevron-up" size={20} style={styles.icon} />
        <Ionicons name="chevron-up" size={20} style={styles.icon} />
      </Animated.View>
      <Animated.View style={[styles.container, styles.bottom, bottomStyle]}>
        <Ionicons name="chevron-down" size={20} style={styles.icon} />
        <Ionicons name="chevron-down" size={20} style={styles.icon} />
      </Animated.View>
    </>
  );
};
