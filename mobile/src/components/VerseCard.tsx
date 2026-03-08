import { type JSX, useEffect, useMemo } from "react";
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
  getPrefixSegments,
  stripCantillation,
  stripNikud,
  stripMeteg,
  removeMaqafForDisplay,
  removeSofPasukForDisplay,
} from "@/src/utils/hebrew";
import { useTranslation } from "@/src/i18n/useTranslation";
import { getTranslationDisplayText } from "@/src/utils/translationDisplay";

const sanitizeEmTags = (value: string) => value.replace(/<\/?em>/gi, "");

const renderTranslationWithItalics = (
  translation: string,
  italicStyle: object,
) => {
  const segments: (string | JSX.Element)[] = [];
  const emPattern = /<em>(.*?)<\/em>/gi;
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  let index = 0;

  while ((match = emPattern.exec(translation)) !== null) {
    const start = match.index;
    const end = start + match[0].length;
    const plainText = translation.slice(lastIndex, start);

    if (plainText) {
      segments.push(sanitizeEmTags(plainText));
    }

    segments.push(
      <Text key={`em-${index}`} style={italicStyle}>
        {match[1]}
      </Text>,
    );

    lastIndex = end;
    index += 1;
  }

  const trailingText = translation.slice(lastIndex);
  if (trailingText) {
    segments.push(sanitizeEmTags(trailingText));
  }

  return segments;
};

type VerseCardProps = {
  verse: DisplayVerse;
  onWordPress?: (word: DisplayVerse["words"][number]) => void;
  onVersePress?: () => void;
  showWordHint?: boolean;
  variant?: "card" | "detail";
  isBesorah?: boolean;
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
      color: colors.textPrimary,
      marginTop: spacing[6],
      textAlign: "center",
    },
    translationItalic: {
      fontStyle: "italic",
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
    hebrewPrefixRow: {
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
    hebrewWordQumran: {
      fontFamily: typography.families.hebrewQumran,
      fontSize: typography.sizes.hebrewVerseMedium * hebrewScale * 1.9,
      lineHeight: typography.sizes.hebrewVerseMedium * hebrewScale * 1.5,
      color: colors.textPrimary,
      textDecorationLine: "underline",
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
  });

export const VerseCard = ({
  verse,
  onWordPress,
  onVersePress,
  showWordHint = false,
  variant = "card",
  isBesorah = false,
}: VerseCardProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const hebrewFontScale = useAppStore(
    (state: AppState) => state.hebrewFontScale,
  );
  const showQumran = useAppStore((state: AppState) => state.showQumran);
  const hebrewOnly = useAppStore((state: AppState) => state.hebrewOnly);
  const language = useAppStore((state: AppState) => state.language);
  const showCantillation = useAppStore(
    (state: AppState) => state.showCantillation,
  );
  const showNikud = useAppStore((state: AppState) => state.showNikud);
  const { t } = useTranslation();
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

  // Spanish fallback: when the user's language is Spanish but the verse has no
  // Spanish translation available yet, we show a localised placeholder message
  // ("verse.missingSpanishTranslation") instead of an empty string so the user
  // knows the translation is pending rather than missing by error.
  const missingSpanishTranslation = t("verse.missingSpanishTranslation");
  const translationText = getTranslationDisplayText({
    language,
    translation: verse.translation,
    missingTranslationText: missingSpanishTranslation,
  });

  const content = (
    <View style={variant === "detail" ? styles.containerDetail : undefined}>
      <View style={styles.hebrewRow}>
        {verse.words.map((word, index) => {
          const wordKey = `${verse.id}-${word.position ?? index}`;
          const isFirst = index === 0;
          const shouldHighlight = showWordHint && isFirst;

          const qumranWord = showQumran ? word.dssWord : undefined;

          // Apply nikud and cantillation settings
          let displayText = qumranWord ?? word.text;
          if (!showNikud) {
            displayText = stripNikud(displayText);
          }
          if (!showCantillation) {
            displayText = stripCantillation(displayText);
          }
          displayText = stripMeteg(displayText);
          displayText = displayText.replace(/\//g, "");
          displayText = removeMaqafForDisplay(displayText);
          if (isBesorah) {
            displayText = removeSofPasukForDisplay(displayText);
          }

          const prefixSegments =
            qumranWord || !word.prefixes?.length
              ? null
              : getPrefixSegments(displayText, word.prefixes);

          const wordStyles = [styles.hebrewWordPressable];

          const renderWordContent = () => {
            if (prefixSegments?.prefixes?.length) {
              return (
                <View style={styles.hebrewPrefixRow}>
                  <Text
                    style={[styles.hebrewWord, { color: colors.textSecondary }]}
                  >
                    {prefixSegments.prefixes.join("")}
                  </Text>
                  <Text
                    style={[styles.hebrewWord, { color: colors.textPrimary }]}
                  >
                    {prefixSegments.root}
                  </Text>
                </View>
              );
            }
            return (
              <Text
                style={
                  qumranWord
                    ? [styles.hebrewWord, styles.hebrewWordQumran]
                    : styles.hebrewWord
                }
              >
                {displayText}
              </Text>
            );
          };

          if (isFirst) {
            return (
              <View key={wordKey} style={styles.firstWordRow}>
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
              key={wordKey}
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
        <Text style={styles.translation}>
          {/<\/?em>/i.test(translationText)
            ? renderTranslationWithItalics(
                translationText,
                styles.translationItalic,
              )
            : translationText}
        </Text>
      )}
    </View>
  );

  return variant === "detail" ? (
    content
  ) : (
    <NeumorphCard>{content}</NeumorphCard>
  );
};
