import { useEffect, useMemo, useState } from "react";
import { Alert, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import * as FileSystem from "expo-file-system";

import { AppIcon } from "@/src/components/ui/AppIcon";
import { PillToggle } from "@/src/components/ui/PillToggle";
import { OnOffButton } from "@/src/components/ui/OnOffButton";
import { SettingsDropdown } from "@/src/components/ui/SettingsDropdown";
import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import { clearStorage } from "@/src/services/storage";

const createStyles = (colors: ReturnType<typeof getColors>) =>
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
    },
    sectionTitle: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      textTransform: "uppercase",
      letterSpacing: 1.5,
      marginBottom: spacing[3],
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
    },
    subtitle: {
      fontFamily: typography.families.latinUI,
      fontSize: typography.sizes.bodySmall,
      color: colors.textSecondary,
      marginTop: 1,
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
  const styles = useMemo(() => createStyles(colors), [colors]);
  const [offlineStatus, setOfflineStatus] = useState({
    dictionary: false,
    english: false,
    spanish: false,
  });

  useEffect(() => {
    const loadStatus = async () => {
      const basePath = `${FileSystem.documentDirectory}offline`;
      const dictionary = await FileSystem.getInfoAsync(
        `${basePath}/dictionary.json`,
      );
      const english = await FileSystem.getInfoAsync(
        `${basePath}/translations-en.json`,
      );
      const spanish = await FileSystem.getInfoAsync(
        `${basePath}/translations-es.json`,
      );

      setOfflineStatus({
        dictionary: dictionary.exists,
        english: english.exists,
        spanish: spanish.exists,
      });
    };
    loadStatus();
  }, []);

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Settings</Text>
        </View>

        {/* General Section */}
        <Text style={styles.sectionTitle}>General</Text>

        {/* Theme */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="idea" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>Theme</Text>
              <Text style={styles.subtitle}>Dark Mode</Text>
            </View>
          </View>
          <PillToggle value={themeMode === "dark"} onChange={toggleThemeMode} />
        </View>

        <View style={styles.divider} />

        <Text style={styles.sectionTitle}>Offline</Text>

        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="download" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>Dictionary</Text>
              <Text style={styles.subtitle}>
                {offlineStatus.dictionary ? "Downloaded" : "Not downloaded"}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="language" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>English Translation</Text>
              <Text style={styles.subtitle}>
                {offlineStatus.english ? "Downloaded" : "Not downloaded"}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="language" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>Spanish Translation</Text>
              <Text style={styles.subtitle}>
                {offlineStatus.spanish ? "Downloaded" : "Not downloaded"}
              </Text>
            </View>
          </View>
        </View>

        <View style={styles.divider} />

        {/* Language */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="language" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>Language</Text>
            </View>
          </View>
          <SettingsDropdown
            value={language}
            onChange={setLanguage}
            options={[
              { label: "English", value: "en" },
              { label: "Español", value: "es" },
              { label: "עברית", value: "he" },
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
              <Text style={styles.label}>Qumran Variants</Text>
              <Text style={styles.subtitle}>Show Dead Sea Scrolls text</Text>
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
              <Text style={styles.label}>Full Chapter</Text>
              <Text style={styles.subtitle}>Show full chapter text</Text>
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
              <Text style={styles.label}>Hebrew Only</Text>
              <Text style={styles.subtitle}>Show text in Hebrew only</Text>
            </View>
          </View>
          <OnOffButton value={hebrewOnly} onChange={setHebrewOnly} />
        </View>

        <View style={styles.divider} />

        {/* Cantillation */}
        <View style={styles.row}>
          <View style={styles.rowContent}>
            <View style={styles.iconContainer}>
              <AppIcon name="hebrew" size={18} color={colors.textSecondary} />
            </View>
            <View style={styles.textContainer}>
              <Text style={styles.label}>Cantillation</Text>
              <Text style={styles.subtitle}>Show cantillation marks</Text>
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
              <Text style={styles.label}>Nikud</Text>
              <Text style={styles.subtitle}>Show vowel pointing</Text>
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
              <Text style={styles.label}>Clear Storage</Text>
              <Text style={styles.subtitle}>Reset all settings and data</Text>
            </View>
          </View>
          <OnOffButton
            value={false}
            onChange={() => {
              Alert.alert(
                "Clear Storage",
                "This will reset all settings and data. The app will reload.",
                [
                  { text: "Cancel", style: "cancel" },
                  {
                    text: "Clear",
                    style: "destructive",
                    onPress: async () => {
                      await clearStorage();
                      useAppStore.getState().setHebrewFontScale(1);
                      useAppStore.getState().setShowQumran(false);
                      useAppStore.getState().setShowFullChapter(false);
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
