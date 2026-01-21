import { useMemo } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { AppIcon } from "@/src/components/ui/AppIcon";
import { getColors, radii, spacing, typography } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import type { IconKey } from "@/src/constants/icons";

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
      backgroundColor: colors.surfaceElevated,
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
    actionSubtitle: {
      fontFamily: typography.families.latinUIMedium,
      fontSize: typography.sizes.bodySmall,
      color: colors.background,
      opacity: 0.85,
      marginTop: spacing[2],
    },
    actionIcon: {
      color: colors.background,
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
  const calendarDays = [
    { day: 10, label: "Sun", active: true },
    { day: 11, label: "Mon" },
    { day: 12, label: "Tue" },
    { day: 13, label: "Wed" },
  ];

  return (
    <SafeAreaView style={styles.safeArea} edges={["top"]}>
      <View style={styles.container}>
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.calendarCard}>
            <View style={styles.calendarBadge}>
              <Text style={styles.calendarBadgeText}>Today is</Text>
            </View>
            <Text style={styles.calendarTitle}>Aviv 10</Text>
            <View style={styles.dateRow}>
              {calendarDays.map((day) => (
                <View
                  key={`${day.day}-${day.label}`}
                  style={[styles.dateCard, day.active && styles.dateCardActive]}
                >
                  <Text
                    style={[
                      styles.dateNumber,
                      day.active && styles.dateNumberActive,
                    ]}
                  >
                    {day.day}
                  </Text>
                  <Text
                    style={[
                      styles.dateLabel,
                      day.active && styles.dateLabelActive,
                    ]}
                  >
                    {day.label}
                  </Text>
                  {day.active ? <View style={styles.datePip} /> : null}
                </View>
              ))}
            </View>
          </View>

          <View style={[styles.actionCard, styles.actionPrimary]}>
            <View>
              <Text style={styles.actionTitle}>Download Offline</Text>
              <Text style={styles.actionSubtitle}>
                Access Scripture without internet
              </Text>
            </View>
            <AppIcon
              name="download"
              size={24}
              color={styles.actionIcon.color}
            />
          </View>

          <View style={[styles.actionCard, styles.actionSecondary]}>
            <View>
              <Text style={styles.actionTitle}>Donate</Text>
              <Text style={styles.actionSubtitle}>
                Support Davar development
              </Text>
            </View>
            <AppIcon
              name="favorite"
              size={24}
              color={styles.actionIcon.color}
            />
          </View>

          <View style={styles.aboutCard}>
            <Text style={styles.aboutTitle}>About</Text>
            <View style={styles.aboutGrid}>
              {(
                [
                  { label: "Legal", icon: "balance" },
                  { label: "Terms", icon: "file" },
                  { label: "Privacy", icon: "shield" },
                  { label: "Support", icon: "chat" },
                  { label: "Bug", icon: "bug" },
                  { label: "GitHub", icon: "github" },
                  { label: "Feedback", icon: "feedback" },
                ] as { label: string; icon: IconKey }[]
              ).map((item) => (
                <View key={item.label} style={styles.aboutPill}>
                  <AppIcon name={item.icon} size={16} color="#E0E0E0" />
                  <Text style={styles.aboutText}>{item.label}</Text>
                </View>
              ))}
            </View>
          </View>
        </ScrollView>
      </View>
    </SafeAreaView>
  );
}
