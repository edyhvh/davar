import { useMemo } from "react";
import { Alert, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { AppIcon } from "@/src/components/ui/AppIcon";
import { PillToggle } from "@/src/components/ui/PillToggle";
import { OnOffButton } from "@/src/components/ui/OnOffButton";
import { SettingsDropdown } from "@/src/components/ui/SettingsDropdown";
import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { clearStorage } from "@/src/services/storage";
import { useTranslation } from "@/src/i18n/useTranslation";

const createStyles = (colors: ReturnType<typeof getColors>, isRTL: boolean) =>
  StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: colors.background,
    },
    container: {
      paddingHorizontal: spacing[6],
      paddingTop: spacing[4],
      paddingBottom: spacing[8],
    },
    header: {
      alignItems: "center",
      marginBottom: spacing[5],
    },
    title: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.h2,
      fontWeight: typography.weights.semibold,
      color: colors.textPrimary,
      textAlign: isRTL ? "right" : "left",
      writingDirection: isRTL ? "rtl" : "ltr",
    },
    sectionTitle: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      textTransform: "uppercase",
      letterSpacing: 1.5,
      marginBottom: spacing[3],
      textAlign: isRTL ? "right" : "left",
      writingDirection: isRTL ? "rtl" : "ltr",
    },
    divider: {
      height: StyleSheet.hairlineWidth,
      backgroundColor: colors.border,
      marginVertical: spacing[3],
    },
    row: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between",
      paddingVertical: spacing[2],
    },
    rowContent: {
      flexDirection: "row",
      alignItems: "center",
      flex: 1,
    },
    iconContainer: {
      width: 36,
      height: 36,
      borderRadius: radii.md,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.border,
      marginRight: spacing[3],
    },
    textContainer: {
      flex: 1,
    },
    label: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.body,
      fontWeight: typography.weights.medium,
      color: colors.textPrimary,
      textAlign: isRTL ? "right" : "left",
      writingDirection: isRTL ? "rtl" : "ltr",
    },
    subtitle: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      marginTop: 1,
      textAlign: isRTL ? "right" : "left",
      writingDirection: isRTL ? "rtl" : "ltr",
    },
  });

export default function SettingsScreen() {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const toggleThemeMode = useAppStore(
    (state: AppState) => state.toggleThemeMode,
  );
  const language = useAppStore((state: AppState) => state.language);
  const setLanguage = useAppStore((state: AppState) => state.setLanguage);
  const showQumran = useAppStore((state: AppState) => state.showQumran);
  const setShowQumran = useAppStore((state: AppState) => state.setShowQumran);
  const showFullChapter = useAppStore(
    (state: AppState) => state.showFullChapter,
  );
  const setShowFullChapter = useAppStore(
    (state: AppState) => state.setShowFullChapter,
  );
  const seferMode = useAppStore((state: AppState) => state.seferMode);
  const setSeferMode = useAppStore((state: AppState) => state.setSeferMode);
  const hebrewOnly = useAppStore((state: AppState) => state.hebrewOnly);
  const setHebrewOnly = useAppStore((state: AppState) => state.setHebrewOnly);
  const showCantillation = useAppStore(
    (state: AppState) => state.showCantillation,
  );
  const setShowCantillation = useAppStore(
    (state: AppState) => state.setShowCantillation,
  );
  const showNikud = useAppStore((state: AppState) => state.showNikud);
  const setShowNikud = useAppStore((state: AppState) => state.setShowNikud);
  const colors = getColors(themeMode);
  const { t, isRTL } = useTranslation();
  const styles = useMemo(() => createStyles(colors, isRTL), [colors, isRTL]);
  const seferDisabled = !hebrewOnly;

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>{t("settings.title")}</Text>
        </View>

        {/* General Section */}
        <Text style={styles.sectionTitle}>
          {t("settings.sections.general")}
        </Text>

        {/* Theme */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="idea" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>{t("settings.theme.title")}</Text>
              <Text style={styles.subtitle}>
                {t("settings.theme.subtitle")}
              </Text>
            </View>
          </View>
          <PillToggle value={themeMode === "dark"} onChange={toggleThemeMode} />
        </View>

        <View style={styles.divider} />

        {/* Language */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="language" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>{t("settings.language.title")}</Text>
            </View>
          </View>
          <SettingsDropdown
            value={language}
            onChange={setLanguage}
            options={[
              { label: t("languages.en"), value: "en" },
              { label: t("languages.es"), value: "es" },
              { label: t("languages.he"), value: "he" },
            ]}
          />
        </View>

        <View style={styles.divider} />

        {/* Qumran Variants */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="scroll" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>{t("settings.qumran.title")}</Text>
              <Text style={styles.subtitle}>
                {t("settings.qumran.subtitle")}
              </Text>
            </View>
          </View>
          <OnOffButton value={showQumran} onChange={setShowQumran} />
        </View>

        <View style={styles.divider} />

        {/* Full Chapter */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="list" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>
                {t("settings.fullChapter.title")}
              </Text>
              <Text style={styles.subtitle}>
                {t("settings.fullChapter.subtitle")}
              </Text>
            </View>
          </View>
          <OnOffButton value={showFullChapter} onChange={setShowFullChapter} />
        </View>

        <View style={styles.divider} />

        {/* Hebrew Only */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="hebrew" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>{t("settings.hebrewOnly.title")}</Text>
              <Text style={styles.subtitle}>
                {t("settings.hebrewOnly.subtitle")}
              </Text>
            </View>
          </View>
          <OnOffButton value={hebrewOnly} onChange={setHebrewOnly} />
        </View>

        {showFullChapter ? (
          <>
            <View style={styles.divider} />

            {/* Sefer Style */}
            <View style={styles.row}>
              <View style={styles.rowContent}>
                <View style={styles.iconContainer}>
                  <AppIcon name="book" size={18} color={colors.textSecondary} />
                </View>
                <View style={styles.textContainer}>
                  <Text style={styles.label}>
                    {t("settings.seferStyle.title")}
                  </Text>
                  <Text style={styles.subtitle}>
                    {t("settings.seferStyle.subtitle")}
                  </Text>
                </View>
              </View>
              <OnOffButton
                value={seferMode}
                onChange={setSeferMode}
                disabled={seferDisabled}
                onDisabledPress={() =>
                  Alert.alert(
                    t("settings.seferStyle.warningTitle"),
                    t("settings.seferStyle.warningMessage"),
                  )
                }
              />
            </View>
          </>
        ) : null}

        <View style={styles.divider} />

        {/* Cantillation */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="hebrew" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>
                {t("settings.cantillation.title")}
              </Text>
              <Text style={styles.subtitle}>
                {t("settings.cantillation.subtitle")}
              </Text>
            </View>
          </View>
          <OnOffButton
            value={showCantillation}
            onChange={setShowCantillation}
          />
        </View>

        <View style={styles.divider} />

        {/* Nikud */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="hebrew" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>{t("settings.nikud.title")}</Text>
              <Text style={styles.subtitle}>
                {t("settings.nikud.subtitle")}
              </Text>
            </View>
          </View>
          <OnOffButton value={showNikud} onChange={setShowNikud} />
        </View>

        <View style={styles.divider} />

        {/* Clear Storage */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="download" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>
                {t("settings.clearStorage.title")}
              </Text>
              <Text style={styles.subtitle}>
                {t("settings.clearStorage.subtitle")}
              </Text>
            </View>
          </View>
          <OnOffButton
            value={false}
            onChange={() => {
              Alert.alert(
                t("settings.clearStorage.alertTitle"),
                t("settings.clearStorage.alertMessage"),
                [
                  { text: t("settings.clearStorage.cancel"), style: "cancel" },
                  {
                    text: t("settings.clearStorage.confirm"),
                    style: "destructive",
                    onPress: async () => {
                      await clearStorage();
                      useAppStore.getState().setHebrewFontScale(1);
                      useAppStore.getState().setShowQumran(false);
                      useAppStore.getState().setShowFullChapter(false);
                      useAppStore.getState().setSeferMode(false);
                      useAppStore.getState().setHebrewOnly(false);
                      useAppStore.getState().setLanguage("en");
                      if (themeMode === "dark") {
                        toggleThemeMode();
                      }
                    },
                  },
                ],
              );
            }}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
