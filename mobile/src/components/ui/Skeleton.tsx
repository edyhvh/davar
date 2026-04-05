import { useEffect } from "react";
import { View, type ViewStyle } from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  Easing,
} from "react-native-reanimated";

import { getColors, radii } from "@/src/theme";
import { useAppStore } from "@/src/store/useAppStore";

type SkeletonProps = {
  width: number | `${number}%`;
  height: number;
  borderRadius?: number;
  delay?: number;
  style?: ViewStyle;
};

export const Skeleton = ({
  width,
  height,
  borderRadius = radii.sm,
  delay = 0,
  style,
}: SkeletonProps) => {
  const themeMode = useAppStore((s) => s.themeMode);
  const colors = getColors(themeMode);
  const opacity = useSharedValue(0.3);

  useEffect(() => {
    const timeout = setTimeout(() => {
      opacity.value = withRepeat(
        withTiming(0.6, { duration: 800, easing: Easing.inOut(Easing.ease) }),
        -1,
        true,
      );
    }, delay);
    return () => clearTimeout(timeout);
  }, [delay, opacity]);

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: opacity.value,
  }));

  return (
    <Animated.View
      style={[
        {
          width,
          height,
          borderRadius,
          backgroundColor: colors.textSecondary,
        },
        animatedStyle,
        style,
      ]}
    />
  );
};
