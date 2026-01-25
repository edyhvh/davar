import React, { createContext, useEffect, useMemo } from "react";
import {
  DarkTheme,
  DefaultTheme,
  ThemeProvider,
} from "@react-navigation/native";

import { getColors } from "@/src/theme";
import { useAppStore, type AppState } from "@/src/store/useAppStore";
import {
  type AppLanguage,
  loadBookmarks,
  loadHebrewFontScale,
  loadHebrewOnly,
  loadLanguage,
  loadSeferMode,
  loadShowFullChapter,
  loadShowQumran,
  loadThemeMode,
  saveBookmarks,
  saveHebrewFontScale,
  saveHebrewOnly,
  saveLanguage,
  saveSeferMode,
  saveShowFullChapter,
  saveShowQumran,
  saveThemeMode,
} from "@/src/services/storage";

export type AppTheme = {
  mode: "light" | "dark";
  colors: ReturnType<typeof getColors>;
};

export const AppThemeContext = createContext<AppTheme>({
  mode: "light",
  colors: getColors("light"),
});

const getNavigationTheme = (mode: "light" | "dark") => {
  const colors = getColors(mode);
  const baseTheme = mode === "dark" ? DarkTheme : DefaultTheme;

  return {
    ...baseTheme,
    colors: {
      ...baseTheme.colors,
      primary: colors.primary,
      background: colors.background,
      card: colors.surface,
      text: colors.textPrimary,
      border: colors.border,
      notification: colors.secondary,
    },
  };
};

export const AppProvider = ({ children }: { children: React.ReactNode }) => {
  const themeMode = useAppStore((state: AppState) => state.themeMode);
  const setThemeMode = useAppStore((state: AppState) => state.setThemeMode);
  const hebrewFontScale = useAppStore(
    (state: AppState) => state.hebrewFontScale,
  );
  const setHebrewFontScale = useAppStore(
    (state: AppState) => state.setHebrewFontScale,
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
  const bookmarks = useAppStore((state: AppState) => state.bookmarks);
  const setBookmarks = useAppStore((state: AppState) => state.setBookmarks);

  const value = useMemo(
    () => ({
      mode: themeMode,
      colors: getColors(themeMode),
    }),
    [themeMode],
  );

  useEffect(() => {
    const hydrate = async () => {
      const [
        savedTheme,
        savedScale,
        savedBookmarks,
        savedLanguage,
        savedShowQumran,
        savedShowFullChapter,
        savedSeferMode,
        savedHebrewOnly,
      ] = await Promise.all([
        loadThemeMode(),
        loadHebrewFontScale(),
        loadBookmarks(),
        loadLanguage(),
        loadShowQumran(),
        loadShowFullChapter(),
        loadSeferMode(),
        loadHebrewOnly(),
      ]);
      setThemeMode(savedTheme);
      setHebrewFontScale(savedScale);
      setBookmarks(savedBookmarks);
      setLanguage(savedLanguage as AppLanguage);
      setShowQumran(savedShowQumran);
      setShowFullChapter(savedShowFullChapter);
      setHebrewOnly(savedHebrewOnly);
      setSeferMode(savedSeferMode);
    };

    hydrate();
  }, [
    setThemeMode,
    setHebrewFontScale,
    setBookmarks,
    setLanguage,
    setShowQumran,
    setShowFullChapter,
    setSeferMode,
    setHebrewOnly,
  ]);

  useEffect(() => {
    saveThemeMode(themeMode);
  }, [themeMode]);

  useEffect(() => {
    saveHebrewFontScale(hebrewFontScale);
  }, [hebrewFontScale]);

  useEffect(() => {
    saveLanguage(language);
  }, [language]);

  useEffect(() => {
    saveShowQumran(showQumran);
  }, [showQumran]);

  useEffect(() => {
    saveShowFullChapter(showFullChapter);
  }, [showFullChapter]);

  useEffect(() => {
    saveSeferMode(seferMode);
  }, [seferMode]);

  useEffect(() => {
    saveHebrewOnly(hebrewOnly);
  }, [hebrewOnly]);

  useEffect(() => {
    saveBookmarks(bookmarks);
  }, [bookmarks]);

  return (
    <AppThemeContext.Provider value={value}>
      <ThemeProvider value={getNavigationTheme(themeMode)}>
        {children}
      </ThemeProvider>
    </AppThemeContext.Provider>
  );
};
