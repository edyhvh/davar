import { useEffect, useMemo } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import Animated, {
  interpolateColor,
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
  Easing,
} from "react-native-reanimated";

import { NeumorphCard } from "@/src/components/ui/NeumorphCard";
import { getColors, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import type { DisplayVerse } from "@/src/services/scripture";
import {
  parseHebrewWord,
  stripNikud,
  stripCantillation,
} from "@/src/utils/hebrew";

type VerseCardProps = {
  verse: DisplayVerse;
  onWordPress?: (word: DisplayVerse["words"][number]) => void;
  onVersePress?: () => void;
  showWordHint?: boolean;
  variant?: "card" | "detail";
};

const createStyles = (
  colors: ReturnType<typeof getColors>,
  hebrewScale: number,
) =>
  StyleSheet.create({
    containerDetail: {
      alignItems: "center",
    },
    translation: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      lineHeight: typography.sizes.body * typography.lineHeights.body,
      color: colors.textSecondary,
      marginTop: spacing[6],
      textAlign: "center",
    },
    hebrewRow: {
      flexDirection: "row-reverse",
      flexWrap: "wrap",
      justifyContent: "center",
    },
    firstWordRow: {
      flexDirection: "row-reverse",
      alignItems: "center",
    },
    verseNumberPressable: {
      paddingHorizontal: spacing[1],
      paddingVertical: 0,
      marginHorizontal: 0,
    },
    verseNumber: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.caption,
      color: colors.textSecondary,
      letterSpacing: 0.6,
    },
    hebrewWord: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: typography.sizes.hebrewVerseMedium * hebrewScale * 1.06,
      lineHeight: typography.sizes.hebrewVerseMedium * hebrewScale * 1.65,
      color: colors.textPrimary,
      textAlign: "right",
      writingDirection: "rtl",
    },
    hebrewWordPressable: {
      paddingHorizontal: spacing[2],
      paddingVertical: spacing[1],
      marginHorizontal: spacing[1],
      borderRadius: 6,
      overflow: "hidden",
    },
    wordHintHighlight: {
      borderWidth: 0,
    },
    qumranHighlight: {
      backgroundColor: `${colors.accentCopper}26`,
    },
  });

export const VerseCard = ({
  verse,
  onWordPress,
  onVersePress,
  showWordHint = false,
  variant = "card",
}: VerseCardProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const hebrewFontScale = useAppStore(
    (state: AppState) => state.hebrewFontScale,
  );
  const showQumran = useAppStore((state: AppState) => state.showQumran);
  const hebrewOnly = useAppStore((state: AppState) => state.hebrewOnly);
  const showCantillation = useAppStore(
    (state: AppState) => state.showCantillation,
  );
  const showNikud = useAppStore((state: AppState) => state.showNikud);
  const colors = getColors(themeMode);
  const styles = useMemo(
    () => createStyles(colors, hebrewFontScale),
    [colors, hebrewFontScale],
  );
  const highlightProgress = useSharedValue(0);

  useEffect(() => {
    // Smooth continuous copper pulse - runs indefinitely
    highlightProgress.value = withRepeat(
      withTiming(1, { duration: 4000, easing: Easing.inOut(Easing.ease) }),
      -1, // -1 means infinite repeats
      true, // reverse for smooth back-and-forth pulse
    );
  }, [highlightProgress]);

  // Subtle copper background pulse using rgba colors
  const highlightStyle = useAnimatedStyle(() => {
    "worklet";
    const backgroundColor = interpolateColor(
      highlightProgress.value,
      [0, 0.5, 1],
      [
        "rgba(198, 143, 85, 0.4)", // Subtle base
        "rgba(198, 143, 85, 0.9)", // Peak brightness
        "rgba(198, 143, 85, 0.4)", // Back to subtle
      ],
    );
    return { backgroundColor };
  });

  const content = (
    <View style={variant === "detail" ? styles.containerDetail : undefined}>
      <View style={styles.hebrewRow}>
        {verse.words.map((word, index) => {
          const isFirst = index === 0;
          const shouldHighlight = showWordHint && isFirst;

          // Apply nikud and cantillation settings
          let displayText = word.text;
          if (!showNikud) {
            displayText = stripNikud(displayText);
          }
          if (!showCantillation) {
            displayText = stripCantillation(displayText);
          }
          displayText = displayText.replace(/\//g, "");

          // Parse word for prefix visualization
          const parsedWord = parseHebrewWord(displayText);

          const wordStyles = [
            styles.hebrewWordPressable,
            showQumran && word.hasQumranVariant && styles.qumranHighlight,
            shouldHighlight && highlightStyle,
          ];

          const renderWordContent = () => {
            if (parsedWord.prefix) {
              return (
                <View style={{ flexDirection: "row" }}>
                  <Text
                    style={[styles.hebrewWord, { color: colors.textSecondary }]}
                  >
                    {parsedWord.prefix.text.replace(/\//g, "")}
                  </Text>
                  <Text
                    style={[styles.hebrewWord, { color: colors.textPrimary }]}
                  >
                    {parsedWord.root.replace(/\//g, "")}
                  </Text>
                </View>
              );
            }
            return (
              <Text style={styles.hebrewWord}>
                {displayText.replace(/\//g, "")}
              </Text>
            );
          };

          if (isFirst) {
            return (
              <View
                key={`${verse.id}-${word.text}`}
                style={styles.firstWordRow}
              >
                <Pressable
                  onPress={onVersePress}
                  style={styles.verseNumberPressable}
                >
                  <Text style={styles.verseNumber}>[{verse.verse}]</Text>
                </Pressable>
                <Pressable
                  onPress={() => onWordPress?.(word)}
                  hitSlop={8}
                  style={wordStyles}
                >
                  {shouldHighlight ? (
                    <Animated.View
                      pointerEvents="none"
                      style={[StyleSheet.absoluteFillObject, highlightStyle]}
                    />
                  ) : null}
                  {renderWordContent()}
                </Pressable>
              </View>
            );
          }

          return (
            <Pressable
              key={`${verse.id}-${word.text}`}
              onPress={() => onWordPress?.(word)}
              hitSlop={8}
              style={wordStyles}
            >
              {shouldHighlight ? (
                <Animated.View
                  pointerEvents="none"
                  style={[StyleSheet.absoluteFillObject, highlightStyle]}
                />
              ) : null}
              {renderWordContent()}
            </Pressable>
          );
        })}
      </View>
      {hebrewOnly ? null : (
        <Text style={styles.translation}>{verse.translation}</Text>
      )}
    </View>
  );

  return variant === "detail" ? (
    content
  ) : (
    <NeumorphCard>{content}</NeumorphCard>
  );
};
