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
  const normalized = query.toLowerCase();
  const lower = text.toLowerCase();
  const index = lower.indexOf(normalized);
  if (index === -1) {
    return [{ text, highlight: false }];
  }
  return [
    { text: text.slice(0, index), highlight: false },
    { text: text.slice(index, index + query.length), highlight: true },
    { text: text.slice(index + query.length), highlight: false },
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
