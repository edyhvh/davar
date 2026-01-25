import React, { useEffect, useRef, useState } from "react";
import { BookOpen, Settings, ScrollText, Eye, Heart, Home } from "lucide-react";
import { LuLightbulb } from "react-icons/lu";
import { TbAlphabetHebrew, TbLanguageHiragana } from "react-icons/tb";
import { FaThList } from "react-icons/fa";
import { NeumorphCard } from "./NeumorphCard";
import { NeumorphicToggle } from "./NeumorphicToggle";
import { useTranslation } from "../hooks/useTranslation";

interface NavigationBarProps {
  book: string;
  bookDisplayName: string;
  bookHebrew: string;
  chapter: number;
  verse: number;
  books: { name: string; hebrew: string; spanish: string }[];
  chapterCount: number;
  verseCount: number;
  onBookChange: (book: string) => void;
  onChapterChange: (chapter: number) => void;
  onVerseChange: (verse: number) => void;
  onHomeClick: () => void;
  onDonateClick: () => void;
  onFeaturesClick: () => void;
  theme: "light" | "dark";
  onThemeChange: (theme: "light" | "dark") => void;
  language: "en" | "es" | "he";
  onLanguageChange: (language: "en" | "es" | "he") => void;
  showQumran: boolean;
  onQumranChange: (show: boolean) => void;
  showFullChapter: boolean;
  onFullChapterChange: (show: boolean) => void;
  seferMode: boolean;
  onSeferModeChange: (show: boolean) => void;
  hebrewOnly: boolean;
  onHebrewOnlyChange: (show: boolean) => void;
  showNikud: boolean;
  onNikudChange: (show: boolean) => void;
  showCantillation: boolean;
  onCantillationChange: (show: boolean) => void;
}

export function NavigationBar({
  book,
  bookDisplayName,
  bookHebrew,
  chapter,
  verse,
  books,
  chapterCount,
  verseCount,
  onBookChange,
  onChapterChange,
  onVerseChange,
  onHomeClick,
  onDonateClick,
  onFeaturesClick,
  theme,
  onThemeChange,
  language,
  onLanguageChange,
  showQumran,
  onQumranChange,
  showFullChapter,
  onFullChapterChange,
  seferMode,
  onSeferModeChange,
  hebrewOnly,
  onHebrewOnlyChange,
  showNikud,
  onNikudChange,
  showCantillation,
  onCantillationChange,
}: NavigationBarProps) {
  const [openMenu, setOpenMenu] = useState<
    "settings" | "book" | "chapter" | "verse" | null
  >(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const bookSearchRef = useRef<HTMLInputElement>(null);
  const chapterSearchRef = useRef<HTMLInputElement>(null);
  const verseSearchRef = useRef<HTMLInputElement>(null);
  const [bookSearch, setBookSearch] = useState("");
  const [chapterSearch, setChapterSearch] = useState("");
  const [verseSearch, setVerseSearch] = useState("");
  const { t } = useTranslation(language);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setOpenMenu(null);
      }
    };

    if (openMenu) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [openMenu]);

  useEffect(() => {
    if (!openMenu) return;
    if (openMenu === "book") {
      setBookSearch("");
      window.setTimeout(() => bookSearchRef.current?.focus(), 0);
    }
    if (openMenu === "chapter") {
      setChapterSearch("");
      window.setTimeout(() => chapterSearchRef.current?.focus(), 0);
    }
    if (openMenu === "verse") {
      setVerseSearch("");
      window.setTimeout(() => verseSearchRef.current?.focus(), 0);
    }
  }, [openMenu]);

  const languages = [
    { code: "en", label: t("languages.en") },
    { code: "es", label: t("languages.es") },
    { code: "he", label: t("languages.he") },
  ];

  const chapters = Array.from({ length: chapterCount }, (_, i) => i + 1);
  const verses = Array.from({ length: verseCount }, (_, i) => i + 1);

  const normalizedBookSearch = bookSearch.trim().toLowerCase();
  const filteredBooks = normalizedBookSearch
    ? books.filter((item) => {
        const haystack = [item.name, item.spanish, item.hebrew]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        return haystack.includes(normalizedBookSearch);
      })
    : books;

  const normalizedChapterSearch = chapterSearch.trim();
  const filteredChapters = normalizedChapterSearch
    ? chapters.filter((item) =>
        String(item).startsWith(normalizedChapterSearch),
      )
    : chapters;

  const normalizedVerseSearch = verseSearch.trim();
  const filteredVerses = normalizedVerseSearch
    ? verses.filter((item) => String(item).startsWith(normalizedVerseSearch))
    : verses;
  const seferDisabled = !hebrewOnly;

  return (
    <div className="relative" ref={dropdownRef}>
      <NeumorphCard className="inline-flex px-3 py-2">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={onHomeClick}
              className="rounded-full p-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                backgroundColor: "var(--neomorph-bg)",
                border: "1px solid var(--neomorph-border)",
                boxShadow:
                  "6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)",
              }}
              aria-label={t("navigation.goHome")}
            >
              <Home className="w-3 h-3 text-[var(--text-primary)]" />
            </button>

            <button
              onClick={() => setOpenMenu(openMenu === "book" ? null : "book")}
              className="flex items-center gap-2 rounded-full px-3 py-1.5 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                boxShadow:
                  "inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
                backgroundColor: "var(--neomorph-bg)",
              }}
              aria-label={t("navigation.selectBook")}
            >
              <BookOpen className="w-3 h-3 text-[var(--text-primary)]" />
              <span className="text-[11px] text-[var(--text-primary)]">
                {bookDisplayName} |{" "}
                <span style={{ fontFamily: "'Suez One', serif" }}>
                  {bookHebrew}
                </span>
              </span>
            </button>

            <button
              onClick={() =>
                setOpenMenu(openMenu === "chapter" ? null : "chapter")
              }
              className="flex items-center gap-2 rounded-full px-3 py-1.5 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                boxShadow:
                  "inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
                backgroundColor: "var(--neomorph-bg)",
              }}
              aria-label={t("navigation.selectChapter")}
            >
              <span className="text-[10px] tracking-[0.2em] uppercase text-[var(--text-primary)]">
                {t("navigation.chapterShort")}
              </span>
              <span className="text-[11px] text-[var(--text-primary)]">
                {chapter}
              </span>
            </button>

            <button
              onClick={() => setOpenMenu(openMenu === "verse" ? null : "verse")}
              className="flex items-center gap-2 rounded-full px-3 py-1.5 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                boxShadow:
                  "inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
                backgroundColor: "var(--neomorph-bg)",
              }}
              aria-label={t("navigation.selectVerse")}
            >
              <span className="text-[10px] tracking-[0.2em] uppercase text-[var(--text-primary)]">
                {t("navigation.verseShort")}
              </span>
              <span className="text-[11px] text-[var(--text-primary)]">
                {verse}
              </span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onFeaturesClick}
              className="flex items-center gap-2 rounded-full px-3 py-1.5 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                background:
                  "linear-gradient(135deg, rgba(198,143,85,0.85), rgba(176,122,60,0.65))",
                color: "#ffffff",
                border: "1px solid rgba(198,143,85,0.6)",
                boxShadow: "0 8px 20px rgba(13,39,80,0.16)",
                backdropFilter: "blur(16px)",
              }}
              aria-label={t("navigation.openFeatures")}
            >
              <span className="text-[11px] tracking-[0.2em] uppercase">
                {t("navigation.features")}
              </span>
            </button>

            <button
              onClick={onDonateClick}
              className="flex items-center gap-2 rounded-full px-3 py-1.5 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                backgroundColor: "var(--accent-darker)",
                color: "#faf4e6",
                boxShadow: "4px 4px 10px var(--neomorph-shadow-dark)",
              }}
              aria-label={t("navigation.donate")}
            >
              <Heart className="w-3 h-3" />
              <span className="text-[11px] tracking-[0.2em] uppercase">
                {t("navigation.donate")}
              </span>
            </button>

            <button
              onClick={() =>
                setOpenMenu(openMenu === "settings" ? null : "settings")
              }
              className="rounded-full p-2 transition-all hover:scale-[1.05] active:scale-[0.98]"
              style={{
                backgroundColor: "var(--neomorph-bg)",
                boxShadow:
                  "6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)",
                border: "1px solid var(--neomorph-border)",
              }}
              aria-label={t("navigation.openSettings")}
            >
              <Settings className="w-3 h-3 text-[var(--text-primary)]" />
            </button>
          </div>
        </div>
      </NeumorphCard>

      {openMenu === "settings" && (
        <div className="absolute right-0 mt-4 w-[320px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-5 z-30">
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <LuLightbulb className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("settings.theme")}
                </span>
              </div>
              <NeumorphicToggle
                enabled={theme === "dark"}
                onToggle={() =>
                  onThemeChange(theme === "light" ? "dark" : "light")
                }
                ariaLabel={t("navigation.toggleDarkTheme")}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <ScrollText className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("settings.qumranVariants")}
                </span>
              </div>
              <NeumorphicToggle
                enabled={showQumran}
                onToggle={() => onQumranChange(!showQumran)}
                ariaLabel={t("navigation.toggleQumran")}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TbAlphabetHebrew className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("settings.hebrewOnly")}
                </span>
              </div>
              <NeumorphicToggle
                enabled={hebrewOnly}
                onToggle={() => onHebrewOnlyChange(!hebrewOnly)}
                ariaLabel={t("navigation.toggleHebrewOnly")}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TbAlphabetHebrew className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("settings.showNikud")}
                </span>
              </div>
              <NeumorphicToggle
                enabled={showNikud}
                onToggle={() => onNikudChange(!showNikud)}
                ariaLabel={t("navigation.toggleNikud")}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TbAlphabetHebrew className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("settings.showCantillation")}
                </span>
              </div>
              <NeumorphicToggle
                enabled={showCantillation}
                onToggle={() => onCantillationChange(!showCantillation)}
                ariaLabel={t("navigation.toggleCantillation")}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FaThList className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("settings.fullChapter")}
                </span>
              </div>
              <NeumorphicToggle
                enabled={showFullChapter}
                onToggle={() => onFullChapterChange(!showFullChapter)}
                ariaLabel={t("navigation.toggleFullChapter")}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TbAlphabetHebrew className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("settings.hebrewOnly")}
                </span>
              </div>
              <NeumorphicToggle
                enabled={hebrewOnly}
                onToggle={() => onHebrewOnlyChange(!hebrewOnly)}
                ariaLabel={t("navigation.toggleHebrewOnly")}
              />
            </div>

            {showFullChapter && (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BookOpen className="w-4 h-4 text-[var(--text-secondary)]" />
                  <span
                    className="text-sm text-[var(--text-primary)]"
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    {t("settings.seferStyle")}
                  </span>
                </div>
                <div className="relative group">
                  <NeumorphicToggle
                    enabled={seferMode}
                    onToggle={() => onSeferModeChange(!seferMode)}
                    ariaLabel={t("navigation.toggleSeferStyle")}
                    disabled={seferDisabled}
                    disabledReason={t("settings.seferStyleWarning")}
                  />
                  {seferDisabled && (
                    <div className="absolute right-0 mt-2 w-48 rounded-lg bg-[var(--neomorph-bg)] border border-[var(--neomorph-border)] px-3 py-2 text-[10px] text-[var(--text-secondary)] shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
                      {t("settings.seferStyleWarning")}
                    </div>
                  )}
                </div>
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <TbLanguageHiragana className="w-4 h-4 text-[var(--text-secondary)]" />
                <span
                  className="text-sm text-[var(--text-primary)]"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {t("navigation.languageLabel")}
                </span>
              </div>
              <select
                value={language}
                onChange={(event) =>
                  onLanguageChange(event.target.value as "en" | "es" | "he")
                }
                className="rounded-full px-3 py-2 text-xs text-[var(--text-primary)]"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  backgroundColor: "var(--neomorph-bg)",
                  border: "1px solid var(--neomorph-border)",
                  boxShadow:
                    "inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
                }}
              >
                {languages.map((lang) => (
                  <option key={lang.code} value={lang.code}>
                    {lang.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {openMenu === "book" && (
        <div className="absolute left-0 mt-4 w-[280px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-4 z-30">
          <div className="mb-3">
            <input
              ref={bookSearchRef}
              value={bookSearch}
              onChange={(event) => setBookSearch(event.target.value)}
              placeholder="Search book"
              className="w-full rounded-full px-4 py-2 text-xs text-[var(--text-primary)]"
              style={{
                fontFamily: "'Inter', sans-serif",
                backgroundColor: "var(--neomorph-bg)",
                border: "1px solid var(--neomorph-border)",
                boxShadow:
                  "inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
              }}
            />
          </div>
          <div className="max-h-[320px] overflow-y-auto space-y-2">
            {filteredBooks.map((item) => (
              <button
                key={item.name}
                onClick={() => {
                  onBookChange(item.name);
                  setOpenMenu(null);
                }}
                className={`w-full flex items-center justify-between rounded-xl px-4 py-3 transition-all ${
                  item.name === book
                    ? "bg-[var(--accent-strong)] text-white"
                    : "bg-[var(--muted)] text-[var(--text-primary)]"
                }`}
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                <span className="text-xs tracking-[0.2em] uppercase">
                  {language === "es" ? item.spanish : item.name}
                </span>
                <span
                  className="text-sm"
                  style={{ fontFamily: "'Suez One', serif" }}
                >
                  {item.hebrew}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {openMenu === "chapter" && (
        <div className="absolute left-0 mt-4 w-[280px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-4 z-30">
          <div className="mb-3">
            <input
              ref={chapterSearchRef}
              value={chapterSearch}
              onChange={(event) =>
                setChapterSearch(event.target.value.replace(/[^0-9]/g, ""))
              }
              placeholder={t("navigation.chapterShort")}
              inputMode="numeric"
              className="w-full rounded-full px-4 py-2 text-xs text-[var(--text-primary)]"
              style={{
                fontFamily: "'Inter', sans-serif",
                backgroundColor: "var(--neomorph-bg)",
                border: "1px solid var(--neomorph-border)",
                boxShadow:
                  "inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
              }}
            />
          </div>
          <div className="grid grid-cols-5 gap-2">
            {filteredChapters.map((item) => (
              <button
                key={item}
                onClick={() => {
                  onChapterChange(item);
                  setOpenMenu(null);
                }}
                className={`rounded-xl px-2 py-2 text-xs transition-all ${
                  item === chapter
                    ? "bg-[var(--accent-strong)] text-white"
                    : "bg-[var(--muted)] text-[var(--text-primary)]"
                }`}
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}

      {openMenu === "verse" && (
        <div className="absolute left-0 mt-4 w-[280px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-4 z-30">
          <div className="mb-3">
            <input
              ref={verseSearchRef}
              value={verseSearch}
              onChange={(event) =>
                setVerseSearch(event.target.value.replace(/[^0-9]/g, ""))
              }
              placeholder={t("navigation.verseShort")}
              inputMode="numeric"
              className="w-full rounded-full px-4 py-2 text-xs text-[var(--text-primary)]"
              style={{
                fontFamily: "'Inter', sans-serif",
                backgroundColor: "var(--neomorph-bg)",
                border: "1px solid var(--neomorph-border)",
                boxShadow:
                  "inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
              }}
            />
          </div>
          <div className="grid grid-cols-5 gap-2 max-h-[320px] overflow-y-auto">
            {filteredVerses.map((item) => (
              <button
                key={item}
                onClick={() => {
                  onVerseChange(item);
                  setOpenMenu(null);
                }}
                className={`rounded-xl px-2 py-2 text-xs transition-all ${
                  item === verse
                    ? "bg-[var(--accent-strong)] text-white"
                    : "bg-[var(--muted)] text-[var(--text-primary)]"
                }`}
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
