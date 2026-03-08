import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { getFocusedRouteNameFromRoute } from "@react-navigation/native";
import { useEffect, useCallback } from "react";
import { StyleSheet } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import "react-native-reanimated";
import * as SplashScreen from "expo-splash-screen";
import { useFonts } from "expo-font";
import { Cardo_400Regular } from "@expo-google-fonts/cardo";
import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
} from "@expo-google-fonts/inter";
import { Jost_400Regular } from "@expo-google-fonts/jost";
import { Arimo_400Regular, Arimo_700Bold } from "@expo-google-fonts/arimo";
import { SuezOne_400Regular } from "@expo-google-fonts/suez-one";
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { BottomSheetModalProvider } from "@gorhom/bottom-sheet";

import { AppProvider } from "@/src/providers/AppProvider";
import { ErrorBoundary } from "@/src/components/ErrorBoundary";
import { useTranslation } from "@/src/i18n/useTranslation";

export const unstable_settings = {
  anchor: "(tabs)",
};

// Keep native splash visible while we prepare the app
void SplashScreen.preventAutoHideAsync().catch(() => {});

export default function RootLayout() {
  const [fontsLoaded, fontError] = useFonts({
    Cardo_400Regular,
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
    Jost_400Regular,
    Arimo_400Regular,
    Arimo_700Bold,
    SuezOne_400Regular,
    DeadSeaScrolls_400Regular: require("../assets/fonts/Deadseascrolls-Regular.ttf"),
  });

  const { t } = useTranslation();
  const appReady = fontsLoaded || !!fontError;

  // Hide the native splash screen
  const hideSplash = useCallback(async () => {
    if (!appReady) return;

    try {
      await SplashScreen.hideAsync();
    } catch {
      // Ignore errors
    }
  }, [appReady]);

  useEffect(() => {
    void hideSplash();
  }, [hideSplash]);

  // Don't render anything until fonts are ready
  if (!appReady) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <GestureHandlerRootView style={styles.flex}>
        <BottomSheetModalProvider>
          <ErrorBoundary>
            <AppProvider>
              <Stack initialRouteName="splash">
                <Stack.Screen
                  name="splash"
                  options={{ headerShown: false }}
                />
                <Stack.Screen
                  name="(tabs)"
                  options={({ route }) => {
                    const focusedTab = getFocusedRouteNameFromRoute(route) ?? "home";
                    const tabTitles: Record<string, string> = {
                      home: t("tabs.home"),
                      verse: t("tabs.verse"),
                      settings: t("tabs.settings"),
                    };

                    return {
                      headerShown: false,
                      title: tabTitles[focusedTab] ?? t("tabs.home"),
                    };
                  }}
                />
                <Stack.Screen
                  name="modal"
                  options={{
                    presentation: "modal",
                    title: t("navigation.modal"),
                  }}
                />
              </Stack>
              <StatusBar style="auto" />
            </AppProvider>
          </ErrorBoundary>
        </BottomSheetModalProvider>
      </GestureHandlerRootView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  flex: {
    flex: 1,
  },
});
