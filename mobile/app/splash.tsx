import { useEffect } from "react";
import { Dimensions, Image, StyleSheet, View } from "react-native";
import { useRootNavigationState, useRouter } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import Animated, {
  Easing,
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withSequence,
  withTiming,
} from "react-native-reanimated";

// ---------------------------------------------------------------------------
// Dreamy gradient splash — multiple full-screen gradient layers
// overlapping at different angles to create depth and color variation.
// No clipped blob Views — just stacked transparent LinearGradients.
// ---------------------------------------------------------------------------

const { width: W, height: H } = Dimensions.get("window");

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: "#B8CEEB", // soft blue-gray base
  },
  gradientLayer: {
    ...StyleSheet.absoluteFillObject,
  },
  noiseWrap: {
    ...StyleSheet.absoluteFillObject,
  },
  noiseImage: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.6,
  },
  logoWrap: {
    ...StyleSheet.absoluteFillObject,
    alignItems: "center",
    justifyContent: "center",
  },
  logo: {
    width: 110,
    height: 110,
    tintColor: "#2E3A50",
  },
});

export default function SplashScreen() {
  const router = useRouter();
  const rootNavigationState = useRootNavigationState();
  const scale = useSharedValue(1);
  const logoOpacity = useSharedValue(1);

  useEffect(() => {
    if (!rootNavigationState?.key) return;

    scale.value = withRepeat(
      withSequence(
        withTiming(1.05, { duration: 800, easing: Easing.inOut(Easing.quad) }),
        withTiming(1, { duration: 800, easing: Easing.inOut(Easing.quad) }),
      ),
      -1,
      true,
    );

    const fadeOut = setTimeout(() => {
      logoOpacity.value = withTiming(0, {
        duration: 400,
        easing: Easing.in(Easing.quad),
      });
    }, 1600);

    const navigate = setTimeout(() => {
      router.replace("/verse");
    }, 2100);

    return () => {
      clearTimeout(fadeOut);
      clearTimeout(navigate);
    };
  }, [logoOpacity, rootNavigationState?.key, router, scale]);

  const animatedLogo = useAnimatedStyle(() => ({
    opacity: logoOpacity.value,
    transform: [{ scale: scale.value }],
  }));

  return (
    <View style={styles.root}>
      {/* Layer 1: top-left deep blue → bottom-right warm copper */}
      <LinearGradient
        colors={["#6389BF", "#A8C8F0", "#C68F55"]}
        locations={[0, 0.5, 1]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.gradientLayer}
      />

      {/* Layer 2: top-right copper glow (transparent center/left) */}
      <LinearGradient
        colors={[
          "transparent",
          "transparent",
          "rgba(198, 143, 85, 0.6)",
        ]}
        locations={[0, 0.4, 1]}
        start={{ x: 0, y: 1 }}
        end={{ x: 1, y: 0 }}
        style={styles.gradientLayer}
      />

      {/* Layer 3: bottom-left deep blue glow */}
      <LinearGradient
        colors={[
          "rgba(61, 90, 140, 0.7)",
          "transparent",
          "transparent",
        ]}
        locations={[0, 0.5, 1]}
        start={{ x: 0, y: 1 }}
        end={{ x: 1, y: 0 }}
        style={styles.gradientLayer}
      />

      {/* Layer 4: soft light wash across center for dreamy feel */}
      <LinearGradient
        colors={[
          "transparent",
          "rgba(200, 216, 240, 0.35)",
          "transparent",
        ]}
        locations={[0.15, 0.5, 0.85]}
        start={{ x: 0.5, y: 0 }}
        end={{ x: 0.5, y: 1 }}
        style={styles.gradientLayer}
      />

      {/* Layer 5: noise / grain overlay */}
      <View pointerEvents="none" style={styles.noiseWrap}>
        <Image
          source={require("@/assets/images/noise-texture.png")}
          resizeMode="repeat"
          style={styles.noiseImage}
        />
      </View>

      {/* Layer 6: logo */}
      <View style={styles.logoWrap}>
        <Animated.Image
          source={require("@/assets/images/davar_nobackground.png")}
          resizeMode="contain"
          style={[styles.logo, animatedLogo]}
        />
      </View>
    </View>
  );
}
