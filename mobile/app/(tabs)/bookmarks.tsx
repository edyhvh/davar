import { useMemo } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";

import { VerseCard } from "@/src/components/VerseCard";
import { getColors, spacing, typography } from "@/src/theme";
import { mockVerses } from "@/src/constants/mockData";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { useTranslation } from "@/src/i18n/useTranslation";

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[6],
    },
    title: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.h2,
      color: colors.textPrimary,
      marginBottom: spacing[6],
    },
    emptyState: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
    },
    listContent: {
      paddingBottom: spacing[12],
    },
    verseItem: {
      marginBottom: spacing[6],
    },
  });

export default function BookmarksScreen() {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const bookmarks = useAppStore((state: AppState) => state.bookmarks);
  const { t } = useTranslation();

  const bookmarkedVerses = mockVerses.filter((verse) =>
    bookmarks.includes(verse.id),
  );

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <View style={styles.container}>
        <Text style={styles.title}>{t("bookmarks.title")}</Text>
        {bookmarkedVerses.length === 0 ? (
          <Text style={styles.emptyState}>
            {t("bookmarks.emptyState")}
          </Text>
        ) : (
          <FlatList
            data={bookmarkedVerses}
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
                <VerseCard verse={item} />
              </Pressable>
            )}
            contentContainerStyle={styles.listContent}
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>
    </SafeAreaView>
  );
}
