import { useMemo, useState } from "react";
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

import { AppIcon } from "@/src/components/ui/AppIcon";
import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import type { IconKey } from "@/src/constants/icons";
import { downloadTranslationBundle } from "@/src/services/offlineSync";
import {
  useTranslation,
  getSupportTelegramUrl,
} from "@/src/i18n/useTranslation";

const createStyles = (colors: ReturnType<typeof getColors>) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      flex: 1,
    },
    content: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[6],
      paddingBottom: spacing[12],
    },
    calendarCard: {
      borderRadius: radii.xl,
      borderWidth: 2,
      borderColor: colors.primary,
      padding: spacing[5],
      backgroundColor: colors.surface,
    },
    calendarBadge: {
      alignSelf: "flex-start",
      borderRadius: radii.full,
      borderWidth: 1,
      borderColor: colors.primary,
      paddingHorizontal: spacing[4],
      paddingVertical: spacing[2],
      marginBottom: spacing[4],
    },
    calendarBadgeText: {
      fontFamily: typography.families.latinUIMedium,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
    },
    calendarTitle: {
      fontFamily: typography.families.latinUIBold,
      fontSize: 70,
      color: colors.textPrimary,
      marginBottom: spacing[4],
    },
    dateRow: {
      flexDirection: "row",
      gap: spacing[3],
    },
    dateCard: {
      flex: 1,
      height: 120,
      borderRadius: radii.lg,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: colors.surfaceLightest,
    },
    dateCardActive: {
      backgroundColor: colors.primary,
    },
    dateNumber: {
      fontFamily: typography.families.latinUIBold,
      fontSize: typography.sizes.h2,
      color: colors.textPrimary,
    },
    dateNumberActive: {
      color: colors.background,
    },
    dateLabel: {
      fontFamily: typography.families.latinUIMedium,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      marginTop: spacing[1],
    },
    dateLabelActive: {
      color: colors.background,
    },
    datePip: {
      width: 20,
      height: 4,
      borderRadius: 999,
      backgroundColor: colors.background,
      marginTop: spacing[2],
    },
    actionCard: {
      borderRadius: radii.xl,
      padding: spacing[5],
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      marginTop: spacing[4],
    },
    actionPrimary: {
      backgroundColor: colors.secondary,
    },
    actionSecondary: {
      backgroundColor: colors.primaryDarker,
    },
    actionTitle: {
      fontFamily: typography.families.latinUIBold,
      fontSize: typography.sizes.h3,
      color: colors.background,
    },
    actionTitleDark: {
      color: colors.textTertiary,
    },
    actionSubtitle: {
      fontFamily: typography.families.latinUIMedium,
      fontSize: typography.sizes.bodySmall,
      color: colors.background,
      opacity: 0.85,
      marginTop: spacing[2],
    },
    actionSubtitleDark: {
      color: colors.textTertiary,
      opacity: 1,
    },
    actionIcon: {
      color: colors.background,
    },
    actionIconDark: {
      color: colors.textTertiary,
    },
    downloadList: {
      marginTop: spacing[4],
      gap: spacing[3],
    },
    downloadRow: {
      borderRadius: radii.lg,
      paddingHorizontal: spacing[4],
      paddingVertical: spacing[3],
      borderWidth: 1,
      borderColor: colors.background,
      backgroundColor: "rgba(255, 255, 255, 0.15)",
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
    },
    downloadRowPressed: {
      opacity: 0.85,
    },
    downloadRowText: {
      fontFamily: typography.families.latinUIBold,
      fontSize: typography.sizes.caption,
      color: colors.background,
      textTransform: "uppercase",
      letterSpacing: 1,
    },
    downloadStatus: {
      width: 24,
      height: 24,
      alignItems: "center",
      justifyContent: "center",
    },
    aboutCard: {
      borderRadius: radii.xl,
      padding: spacing[5],
      backgroundColor: colors.aboutBackground,
      marginTop: spacing[4],
    },
    aboutTitle: {
      fontFamily: typography.families.latinUIBold,
      fontSize: typography.sizes.h3,
      color: "#FFFFFF",
      marginBottom: spacing[4],
    },
    aboutGrid: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: spacing[3],
    },
    aboutPill: {
      flexDirection: "row",
      alignItems: "center",
      gap: spacing[2],
      paddingHorizontal: spacing[4],
      paddingVertical: spacing[3],
      borderRadius: radii.full,
      borderWidth: 0,
      backgroundColor: "#6B6B6B",
    },
    aboutPillInteractive: {
      borderWidth: 1,
      borderColor: "rgba(255, 255, 255, 0.12)",
    },
    aboutPillPressed: {
      opacity: 0.85,
      transform: [{ scale: 0.98 }],
    },
    aboutText: {
      fontFamily: typography.families.latinUIMedium,
      fontSize: typography.sizes.bodySmall,
      color: "#E0E0E0",
    },
  });

export default function HomeScreen() {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const styles = useMemo(() => createStyles(colors), [colors]);
  const { t, language } = useTranslation();
  const router = useRouter();
  type DownloadLanguage = "en" | "es";
  type DownloadStatus = "idle" | "downloading" | "completed";
  const downloadItems = useMemo(
    () => [
      { language: "en" as DownloadLanguage, label: t("home.download.english") },
      { language: "es" as DownloadLanguage, label: t("home.download.spanish") },
    ],
    [t],
  );
  const [downloadStatus, setDownloadStatus] = useState<
    Record<DownloadLanguage, DownloadStatus>
  >({ en: "idle", es: "idle" });
  const activeDownload = (
    Object.entries(downloadStatus) as [DownloadLanguage, DownloadStatus][]
  ).find(([, status]) => status === "downloading");
  const downloadLabelMap: Record<DownloadLanguage, string> = {
    en: t("home.download.english"),
    es: t("home.download.spanish"),
  };
  const activeLabel = activeDownload
    ? downloadLabelMap[activeDownload[0]]
    : null;

  const handleDownloadPress = async (language: DownloadLanguage) => {
    if (downloadStatus[language] === "downloading") {
      return;
    }

    setDownloadStatus((prev) => ({ ...prev, [language]: "downloading" }));
    try {
      await downloadTranslationBundle(language);
      setDownloadStatus((prev) => ({ ...prev, [language]: "completed" }));
    } catch {
      setDownloadStatus((prev) => ({ ...prev, [language]: "idle" }));
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <View style={styles.container}>
        <ScrollView contentContainerStyle={styles.content}>
          <View style={[styles.actionCard, styles.actionPrimary]}>
            <View>
              <Text
                style={[
                  styles.actionTitle,
                  themeMode === "dark" && styles.actionTitleDark,
                ]}
              >
                {t("home.download.title")}
              </Text>
              <Text
                style={[
                  styles.actionSubtitle,
                  themeMode === "dark" && styles.actionSubtitleDark,
                ]}
              >
                {activeLabel
                  ? t("home.download.downloading", { item: activeLabel })
                  : t("home.download.idle")}
              </Text>
              <View style={styles.downloadList}>
                {downloadItems.map((item) => {
                  const status = downloadStatus[item.language];
                  return (
                    <Pressable
                      key={item.language}
                      onPress={() => handleDownloadPress(item.language)}
                      style={({ pressed }) => [
                        styles.downloadRow,
                        pressed && styles.downloadRowPressed,
                      ]}
                    >
                      <Text style={styles.downloadRowText}>{item.label}</Text>
                      <View style={styles.downloadStatus}>
                        {status === "downloading" ? (
                          <ActivityIndicator
                            size="small"
                            color={colors.background}
                          />
                        ) : (
                          <AppIcon
                            name={
                              status === "completed"
                                ? "download-done"
                                : "download"
                            }
                            size={20}
                            color={colors.background}
                          />
                        )}
                      </View>
                    </Pressable>
                  );
                })}
              </View>
            </View>
          </View>

          <View style={[styles.actionCard, styles.actionSecondary]}>
            <View>
              <Text
                style={[
                  styles.actionTitle,
                  themeMode === "dark" && styles.actionTitleDark,
                ]}
              >
                {t("home.donate.title")}
              </Text>
              <Text
                style={[
                  styles.actionSubtitle,
                  themeMode === "dark" && styles.actionSubtitleDark,
                ]}
              >
                {t("home.donate.subtitle")}
              </Text>
            </View>
            <AppIcon
              name="favorite"
              size={24}
              color={
                themeMode === "dark"
                  ? styles.actionIconDark.color
                  : styles.actionIcon.color
              }
            />
          </View>

          <View style={styles.aboutCard}>
            <Text style={styles.aboutTitle}>{t("home.about.title")}</Text>
            <View style={styles.aboutGrid}>
              {(
                [
                  {
                    label: t("home.about.items.terms"),
                    icon: "file",
                    onPress: () => router.push("/terms"),
                  },
                  {
                    label: t("home.about.items.privacy"),
                    icon: "shield",
                    onPress: () => router.push("/privacy"),
                  },
                  {
                    label: t("home.about.items.support"),
                    icon: "chat",
                    onPress: () =>
                      Linking.openURL(getSupportTelegramUrl(language)),
                  },
                  {
                    label: t("home.about.items.bug"),
                    icon: "bug",
                    onPress: () =>
                      Linking.openURL(
                        "https://github.com/edyhvh/davar/issues/new",
                      ),
                  },
                  {
                    label: t("home.about.items.github"),
                    icon: "github",
                    onPress: () =>
                      Linking.openURL("https://github.com/edyhvh/davar"),
                  },
                  {
                    label: t("home.about.items.feedback"),
                    icon: "feedback",
                    onPress: () =>
                      Linking.openURL("https://davar.bible/feedback"),
                  },
                ] as { label: string; icon: IconKey; onPress?: () => void }[]
              ).map((item) => (
                <Pressable
                  key={item.label}
                  onPress={item.onPress}
                  disabled={!item.onPress}
                  style={({ pressed }) => [
                    styles.aboutPill,
                    item.onPress && styles.aboutPillInteractive,
                    pressed && item.onPress && styles.aboutPillPressed,
                  ]}
                >
                  <AppIcon name={item.icon} size={16} color="#E0E0E0" />
                  <Text style={styles.aboutText}>{item.label}</Text>
                </Pressable>
              ))}
            </View>
          </View>
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}
