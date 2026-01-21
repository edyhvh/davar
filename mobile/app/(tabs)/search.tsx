import { useEffect, useMemo, useState } from "react";
import {
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { SearchResultCard } from "@/src/components/SearchResultCard";
import { AppIcon } from "@/src/components/ui/AppIcon";
import { getColors, spacing, typography } from "@/src/theme";
import { mockVerses } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      flex: 1,
      backgroundColor: colors.background,
    },
    header: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[6],
      paddingBottom: spacing[4],
      borderBottomWidth: 1,
      borderBottomColor: colors.border,
    },
    title: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.h2,
      color: colors.textPrimary,
    },
    input: {
      flex: 1,
      borderWidth: 1,
      borderColor: colors.border,
      borderRadius: 12,
      paddingHorizontal: spacing[4],
      paddingVertical: spacing[3],
      backgroundColor: colors.surface,
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      color: colors.textPrimary,
    },
    inputRow: {
      marginTop: spacing[4],
      flexDirection: "row",
      alignItems: "center",
      gap: spacing[2],
    },
    inputContainer: {
      flex: 1,
      flexDirection: "row",
      alignItems: "center",
      gap: spacing[2],
    },
    inputFocused: {
      borderColor: colors.primary,
      shadowColor: colors.primary,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.2,
      shadowRadius: 6,
    },
    inputRtl: {
      textAlign: "right",
      writingDirection: "rtl",
    },
    inputLtr: {
      textAlign: "left",
      writingDirection: "ltr",
    },
    icon: {
      color: colors.textSecondary,
    },
    clearButton: {
      width: 32,
      height: 32,
      borderRadius: 16,
      alignItems: "center",
      justifyContent: "center",
      borderWidth: 1,
      borderColor: colors.border,
      backgroundColor: colors.surface,
    },
    hint: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      marginTop: spacing[3],
    },
    listContent: {
      paddingHorizontal: spacing[6],
      paddingBottom: spacing[12],
    },
    verseItem: {
      marginBottom: spacing[6],
    },
    emptyState: {
      marginTop: spacing[8],
      alignItems: "center",
      gap: spacing[3],
    },
    emptyText: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
    },
  });

export default function SearchScreen() {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const searchQuery = useAppStore((state: AppState) => state.searchQuery);
  const setSearchQuery = useAppStore((state: AppState) => state.setSearchQuery);
  const setSearchResults = useAppStore(
    (state: AppState) => state.setSearchResults,
  );
  const [draftQuery, setDraftQuery] = useState(searchQuery);
  const [isFocused, setIsFocused] = useState(false);
  const isHebrew = useMemo(
    () => /[\u0590-\u05FF]/.test(draftQuery),
    [draftQuery],
  );

  const results = useMemo(() => {
    const normalized = searchQuery.trim().toLowerCase();
    if (!normalized) {
      return [];
    }

    return mockVerses.filter((verse) => {
      const inTranslation = verse.translation
        .toLowerCase()
        .includes(normalized);
      const inHebrew = verse.hebrew.includes(normalized);
      return inTranslation || inHebrew;
    });
  }, [searchQuery]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setSearchQuery(draftQuery);
    }, 300);

    return () => clearTimeout(timeout);
  }, [draftQuery, setSearchQuery]);

  useEffect(() => {
    setSearchResults(results);
  }, [results, setSearchResults]);

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Search</Text>
          <View style={styles.inputRow}>
            <View style={styles.inputContainer}>
              <AppIcon name="search" size={18} color={styles.icon.color} />
              <TextInput
                value={draftQuery}
                onChangeText={setDraftQuery}
                placeholder="Search a word, phrase, or verse"
                placeholderTextColor={colors.textSecondary}
                style={[
                  styles.input,
                  isFocused && styles.inputFocused,
                  isHebrew ? styles.inputRtl : styles.inputLtr,
                ]}
                autoCapitalize="none"
                autoCorrect={false}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
              />
            </View>
            {draftQuery ? (
              <Pressable
                style={styles.clearButton}
                onPress={() => setDraftQuery("")}
              >
                <Ionicons name="close" size={16} color={colors.textSecondary} />
              </Pressable>
            ) : null}
          </View>
          {!draftQuery ? (
            <Text style={styles.hint}>Begin typing to explore Scripture.</Text>
          ) : null}
        </View>
        {draftQuery && results.length === 0 ? (
          <View style={styles.emptyState}>
            <AppIcon name="book" size={24} color={colors.textSecondary} />
            <Text style={styles.emptyText}>No results found.</Text>
          </View>
        ) : null}
        <FlatList
          data={results}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <Pressable
              style={styles.verseItem}
              onPress={() =>
                router.push({
                  pathname: "/verse-detail",
                  params: { id: item.id },
                })
              }
            >
              <SearchResultCard verse={item} query={searchQuery} />
            </Pressable>
          )}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
        />
      </View>
    </SafeAreaView>
  );
}
