import { Tabs } from "expo-router";
import { useMemo } from "react";
import { Platform, StyleSheet, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { HapticTab } from "@/components/haptic-tab";
import { AppIcon } from "@/src/components/ui/AppIcon";
import { getColors } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";

const createStyles = (
  colors: ReturnType<typeof getColors>,
  bottomInset: number,
) =>
  StyleSheet.create({
    tabBar: {
      backgroundColor: colors.surface,
      borderTopColor: "#999999",
      borderTopWidth: 0.4,
      height: 70 + bottomInset,
      paddingTop: 8,
      paddingBottom: bottomInset,
    },
    centerIconWrapper: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
    },
    centerIcon: {
      width: 44,
      height: 44,
      borderRadius: 22,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: colors.primary,
      shadowColor: colors.primary,
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.2,
      shadowRadius: 4,
    },
    tabItem: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
    },
  });

export const AppNavigator = () => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const colors = getColors(themeMode);
  const insets = useSafeAreaInsets();
  const bottomInset = Platform.OS === "ios" ? insets.bottom : 0;
  const styles = useMemo(
    () => createStyles(colors, bottomInset),
    [colors, bottomInset],
  );

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textSecondary,
        tabBarStyle: styles.tabBar,
        tabBarButton: HapticTab,
        tabBarShowLabel: false,
        tabBarItemStyle: styles.tabItem,
      }}
      initialRouteName="verse"
    >
      <Tabs.Screen
        name="home"
        options={{
          title: "Home",
          tabBarIcon: ({ color }) => (
            <AppIcon name="home" color={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen
        name="verse"
        options={{
          title: "Verse",
          tabBarIcon: ({ focused }) => (
            <View style={styles.centerIconWrapper}>
              <View style={styles.centerIcon}>
                <AppIcon
                  name={focused ? "search" : "book"}
                  color={colors.background}
                  size={22}
                />
              </View>
            </View>
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: "Settings",
          tabBarIcon: ({ color }) => (
            <AppIcon name="settings" color={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen name="index" options={{ href: null }} />
      <Tabs.Screen name="search" options={{ href: null }} />
      <Tabs.Screen name="bookmarks" options={{ href: null }} />
      <Tabs.Screen name="explore" options={{ href: null }} />
    </Tabs>
  );
};
