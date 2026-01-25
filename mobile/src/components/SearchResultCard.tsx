import { useMemo } from "react";
import { StyleSheet, Text, View } from "react-native";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import type { MockVerse } from "@/src/constants/mockData";

type SearchResultCardProps = {
  verse: MockVerse;
  query: string;
};

const highlightParts = (text: string, query: string) => {
  if (!query) {
    return [{ text, highlight: false }];
  }
  const isCombiningMark = (char: string) => /\p{M}/u.test(char);
  const splitGraphemes = (value: string) => {
    const graphemes: string[] = [];
    for (const char of Array.from(value)) {
      if (isCombiningMark(char) && graphemes.length) {
        graphemes[graphemes.length - 1] += char;
      } else {
        graphemes.push(char);
      }
    }
    return graphemes;
  };

  const textGraphemes = splitGraphemes(text);
  const queryGraphemes = splitGraphemes(query);
  if (!queryGraphemes.length) {
    return [{ text, highlight: false }];
  }

  const normalizedText = textGraphemes.map((part) => part.toLowerCase());
  const normalizedQuery = queryGraphemes.map((part) => part.toLowerCase());
  let matchIndex = -1;

  for (let i = 0; i <= normalizedText.length - normalizedQuery.length; i += 1) {
    let matched = true;
    for (let j = 0; j < normalizedQuery.length; j += 1) {
      if (normalizedText[i + j] !== normalizedQuery[j]) {
        matched = false;
        break;
      }
    }
    if (matched) {
      matchIndex = i;
      break;
    }
  }

  if (matchIndex === -1) {
    return [{ text, highlight: false }];
  }

  return [
    { text: textGraphemes.slice(0, matchIndex).join(""), highlight: false },
    {
      text: textGraphemes
        .slice(matchIndex, matchIndex + queryGraphemes.length)
        .join(""),
      highlight: true,
    },
    {
      text: textGraphemes
        .slice(matchIndex + queryGraphemes.length)
        .join(""),
      highlight: false,
    },
  ].filter((part) => part.text.length > 0);
};

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    container: {
      backgroundColor: colors.surface,
      borderRadius: radii.lg,
      padding: spacing[4],
      borderWidth: 1,
      borderColor: colors.border,
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    header: {
      flexDirection: "row",
      justifyContent: "space-between",
      marginBottom: spacing[2],
    },
    reference: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
    },
    hebrew: {
      fontFamily: typography.families.hebrewScripture,
      fontSize: 18,
      lineHeight: 18 * typography.lineHeights.hebrewScripture,
      color: colors.textPrimary,
      textAlign: "right",
      writingDirection: "rtl",
      marginBottom: spacing[2],
    },
    translation: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      lineHeight: typography.sizes.bodySmall * typography.lineHeights.body,
    },
    highlight: {
      backgroundColor: `${colors.accentCopper}4D`,
    },
  });

export const SearchResultCard = ({ verse, query }: SearchResultCardProps) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const hebrewParts = useMemo(
    () => highlightParts(verse.hebrew, query),
    [verse.hebrew, query],
  );
  const translationParts = useMemo(
    () => highlightParts(verse.translation, query),
    [verse.translation, query],
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.reference}>
          {verse.book} {verse.chapter}:{verse.verse}
        </Text>
      </View>
      <Text style={styles.hebrew} numberOfLines={2} ellipsizeMode="tail">
        {hebrewParts.map((part, index) => (
          <Text
            key={`${part.text}-${index}`}
            style={part.highlight ? styles.highlight : undefined}
          >
            {part.text}
          </Text>
        ))}
      </Text>
      <Text style={styles.translation} numberOfLines={2} ellipsizeMode="tail">
        {translationParts.map((part, index) => (
          <Text
            key={`${part.text}-${index}`}
            style={part.highlight ? styles.highlight : undefined}
          >
            {part.text}
          </Text>
        ))}
      </Text>
    </View>
  );
};
