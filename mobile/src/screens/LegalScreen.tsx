import { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import Markdown from "react-native-markdown-display";

import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { useTranslation } from "@/src/i18n/useTranslation";

interface LegalScreenProps {
  title: string;
  docUrl: string;
}

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      flex: 1,
    },
    header: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[6],
      paddingBottom: spacing[4],
    },
    backButton: {
      alignSelf: "flex-start",
      borderRadius: radii.full,
      borderWidth: 1,
      borderColor: colors.border,
      paddingHorizontal: spacing[4],
      paddingVertical: spacing[2],
      marginBottom: spacing[4],
      backgroundColor: colors.surface,
    },
    backText: {
      fontFamily: typography.families.latinUIMedium,
      fontSize: typography.sizes.bodySmall,
      color: colors.textPrimary,
      letterSpacing: 1,
      textTransform: "uppercase",
    },
    title: {
      fontFamily: typography.families.hebrewUI,
      fontSize: 30,
      color: colors.textPrimary,
      marginBottom: spacing[2],
    },
    subtitle: {
      fontFamily: typography.families.latinMeaning,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
    },
    content: {
      paddingHorizontal: spacing[6],
      paddingBottom: spacing[12],
    },
    status: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      textAlign: "center",
      paddingVertical: spacing[6],
    },
    card: {
      borderRadius: radii.xl,
      backgroundColor: colors.surface,
      padding: spacing[5],
      borderWidth: 1,
      borderColor: colors.border,
    },
  });

export function LegalScreen({ title, docUrl }: LegalScreenProps) {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const markdownStyles = useMemo(
    () => ({
      body: {
        fontFamily: typography.families.hebrewScripture,
        fontSize: typography.sizes.body,
        lineHeight: 26,
        color: colors.textPrimary,
      },
      heading1: {
        fontFamily: typography.families.hebrewUI,
        fontSize: 24,
        color: colors.textPrimary,
        marginTop: spacing[6],
        marginBottom: spacing[2],
      },
      heading2: {
        fontFamily: typography.families.hebrewUI,
        fontSize: 20,
        color: colors.textPrimary,
        marginTop: spacing[5],
        marginBottom: spacing[2],
      },
      heading3: {
        fontFamily: typography.families.hebrewUI,
        fontSize: 18,
        color: colors.textPrimary,
        marginTop: spacing[4],
        marginBottom: spacing[2],
      },
      paragraph: {
        marginBottom: spacing[3],
      },
      bullet_list: {
        marginVertical: spacing[2],
      },
      list_item: {
        marginBottom: spacing[2],
      },
      link: {
        color: colors.accentCopper,
        textDecorationLine: "underline",
      },
      table: {
        borderWidth: 1,
        borderColor: colors.border,
        marginVertical: spacing[3],
      },
      th: {
        borderWidth: 1,
        borderColor: colors.border,
        padding: spacing[2],
      },
      td: {
        borderWidth: 1,
        borderColor: colors.border,
        padding: spacing[2],
      },
    }),
    [colors],
  );
  const { t } = useTranslation();
  const router = useRouter();
  const [markdown, setMarkdown] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const loadDoc = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await fetch(docUrl, { signal: controller.signal });
        if (!response.ok) {
          throw new Error("Failed to load legal content.");
        }
        const text = await response.text();
        setMarkdown(text);
      } catch (err) {
        if ((err as { name?: string }).name === "AbortError") {
          return;
        }
        setError(t("errors.uiFallbackMessageMobile"));
      } finally {
        setIsLoading(false);
      }
    };

    void loadDoc();

    return () => controller.abort();
  }, [docUrl, t]);

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <View style={styles.container}>
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.header}>
            <Pressable
              onPress={() => router.back()}
              style={({ pressed }) => [
                styles.backButton,
                pressed && { opacity: 0.85 },
              ]}
            >
              <Text style={styles.backText}>{t("navigation.backToApp")}</Text>
            </Pressable>
            <Text style={styles.title}>{title}</Text>
            <Text style={styles.subtitle}>
              Quiet clarity for important agreements and commitments.
            </Text>
          </View>

          <View style={styles.card}>
            {isLoading && (
              <ActivityIndicator size="small" color={colors.textSecondary} />
            )}
            {!isLoading && error && <Text style={styles.status}>{error}</Text>}
            {!isLoading && !error && (
              <Markdown
                style={markdownStyles}
                onLinkPress={(url) => {
                  void Linking.openURL(url);
                  return false;
                }}
              >
                {markdown}
              </Markdown>
            )}
          </View>
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}
