import { create } from "zustand";

import type { MockVerse } from "@/src/constants/mockData";
import type { ThemeMode } from "@/src/theme";
import type { AppLanguage } from "@/src/services/storage";
import type { DownloadProgress, BundleVersions } from "@/src/services/offlineSync";

export type OfflineStatus = "idle" | "downloading" | "ready";

export type AppState = {
  themeMode: ThemeMode;
  setThemeMode: (mode: ThemeMode) => void;
  toggleThemeMode: () => void;
  hebrewFontScale: number;
  setHebrewFontScale: (scale: number) => void;
  language: AppLanguage;
  setLanguage: (language: AppLanguage) => void;
  showQumran: boolean;
  setShowQumran: (value: boolean) => void;
  showFullChapter: boolean;
  setShowFullChapter: (value: boolean) => void;
  seferMode: boolean;
  setSeferMode: (value: boolean) => void;
  hebrewOnly: boolean;
  setHebrewOnly: (value: boolean) => void;
  showCantillation: boolean;
  setShowCantillation: (value: boolean) => void;
  showNikud: boolean;
  setShowNikud: (value: boolean) => void;
  currentVerseId: string;
  setCurrentVerseId: (id: string) => void;
  bookmarks: string[];
  addBookmark: (id: string) => void;
  removeBookmark: (id: string) => void;
  setBookmarks: (ids: string[]) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  searchResults: MockVerse[];
  setSearchResults: (results: MockVerse[]) => void;
  // Offline download state
  offlineStatus: OfflineStatus;
  setOfflineStatus: (status: OfflineStatus) => void;
  offlineUpdateAvailable: boolean;
  setOfflineUpdateAvailable: (value: boolean) => void;
  downloadProgress: DownloadProgress | null;
  setDownloadProgress: (progress: DownloadProgress | null) => void;
  localBundleVersions: BundleVersions;
  setLocalBundleVersions: (versions: BundleVersions) => void;
  isConnected: boolean;
  setIsConnected: (connected: boolean) => void;
};

export const useAppStore = create<AppState>((set) => ({
  themeMode: "light",
  setThemeMode: (mode) => set({ themeMode: mode }),
  toggleThemeMode: () =>
    set((state) => ({
      themeMode: state.themeMode === "light" ? "dark" : "light",
    })),
  hebrewFontScale: 1,
  setHebrewFontScale: (scale) => set({ hebrewFontScale: scale }),
  language: "en",
  setLanguage: (language) => set({ language }),
  showQumran: false,
  setShowQumran: (value) => set({ showQumran: value }),
  showFullChapter: false,
  setShowFullChapter: (value) =>
    set((state) => ({
      showFullChapter: value,
      seferMode: value ? state.seferMode : false,
    })),
  seferMode: false,
  setSeferMode: (value) =>
    set((state) => ({
      seferMode: value && state.showFullChapter && state.hebrewOnly,
    })),
  hebrewOnly: false,
  setHebrewOnly: (value) =>
    set((state) => ({
      hebrewOnly: value,
      seferMode: value ? state.seferMode : false,
    })),
  showCantillation: false,
  setShowCantillation: (value) => set({ showCantillation: value }),
  showNikud: true,
  setShowNikud: (value) => set({ showNikud: value }),
  currentVerseId: "genesis-1-1",
  setCurrentVerseId: (id) => set({ currentVerseId: id }),
  bookmarks: [],
  addBookmark: (id) =>
    set((state) => ({ bookmarks: [...new Set([...state.bookmarks, id])] })),
  removeBookmark: (id) =>
    set((state) => ({
      bookmarks: state.bookmarks.filter((item) => item !== id),
    })),
  setBookmarks: (ids) => set({ bookmarks: ids }),
  searchQuery: "",
  setSearchQuery: (query) => set({ searchQuery: query }),
  searchResults: [],
  setSearchResults: (results) => set({ searchResults: results }),
  // Offline download state
  offlineStatus: "idle",
  setOfflineStatus: (status) => set({ offlineStatus: status }),
  offlineUpdateAvailable: false,
  setOfflineUpdateAvailable: (value) => set({ offlineUpdateAvailable: value }),
  downloadProgress: null,
  setDownloadProgress: (progress) => set({ downloadProgress: progress }),
  localBundleVersions: {},
  setLocalBundleVersions: (versions) =>
    set({ localBundleVersions: versions }),
  isConnected: true,
  setIsConnected: (connected) => set({ isConnected: connected }),
}));
