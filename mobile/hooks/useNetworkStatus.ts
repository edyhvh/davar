import { useEffect } from "react";
import { AppState, type AppStateStatus } from "react-native";
import * as Network from "expo-network";
import { useAppStore } from "@/src/store/useAppStore";

/**
 * Monitors network connectivity and syncs to Zustand store.
 * Call once in the root layout so every screen can read `isConnected`.
 */
export const useNetworkStatus = () => {
  const setIsConnected = useAppStore((s) => s.setIsConnected);

  useEffect(() => {
    let mounted = true;

    // Check immediately on mount
    const checkNow = async () => {
      try {
        const state = await Network.getNetworkStateAsync();
        if (mounted) {
          setIsConnected(state.isInternetReachable ?? state.isConnected ?? true);
        }
      } catch {
        // Assume connected if we can't check
        if (mounted) setIsConnected(true);
      }
    };

    checkNow();

    // Poll every 10 seconds (expo-network doesn't have a listener API)
    let interval: ReturnType<typeof setInterval> | null = null;

    const startPolling = () => {
      if (!interval) interval = setInterval(checkNow, 10_000);
    };

    const stopPolling = () => {
      if (interval) {
        clearInterval(interval);
        interval = null;
      }
    };

    const handleAppStateChange = (nextState: AppStateStatus) => {
      if (nextState === "active") {
        checkNow();
        startPolling();
      } else {
        stopPolling();
      }
    };

    startPolling();
    const appStateListener = AppState.addEventListener(
      "change",
      handleAppStateChange,
    );

    return () => {
      mounted = false;
      stopPolling();
      appStateListener.remove();
    };
  }, [setIsConnected]);
};
