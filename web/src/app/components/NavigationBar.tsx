import React, { useEffect, useRef, useState } from 'react';
import { BookOpen, Settings, Sun, Moon, ScrollText, Languages, Eye, Heart, Home, Lightbulb, ChevronUp, ChevronDown } from 'lucide-react';
import { NeumorphCard } from './NeumorphCard';
import { NeumorphicToggle } from './NeumorphicToggle';

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
  onPreviousVerse: () => void;
  onNextVerse: () => void;
  hasPreviousVerse: boolean;
  hasNextVerse: boolean;
  theme: 'light' | 'dark';
  onThemeChange: (theme: 'light' | 'dark') => void;
  language: 'en' | 'es' | 'he';
  onLanguageChange: (language: 'en' | 'es' | 'he') => void;
  showQumran: boolean;
  onQumranChange: (show: boolean) => void;
  showFullChapter: boolean;
  onFullChapterChange: (show: boolean) => void;
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
  onPreviousVerse,
  onNextVerse,
  hasPreviousVerse,
  hasNextVerse,
  theme,
  onThemeChange,
  language,
  onLanguageChange,
  showQumran,
  onQumranChange,
  showFullChapter,
  onFullChapterChange,
  hebrewOnly,
  onHebrewOnlyChange,
  showNikud,
  onNikudChange,
  showCantillation,
  onCantillationChange,
}: NavigationBarProps) {
  const [openMenu, setOpenMenu] = useState<'settings' | 'book' | 'chapter' | 'verse' | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpenMenu(null);
      }
    };

    if (openMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [openMenu]);

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Español' },
    { code: 'he', label: 'עברית' },
  ];

  const HebrewIcon = () => (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M8 6 L8 18 M12 6 L12 18 M16 6 L16 12 M8 12 L16 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );

  const chapters = Array.from({ length: chapterCount }, (_, i) => i + 1);
  const verses = Array.from({ length: verseCount }, (_, i) => i + 1);

  return (
    <div className="relative" ref={dropdownRef}>
      <NeumorphCard className="px-4 py-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={onHomeClick}
              className="rounded-full px-4 py-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                backgroundColor: 'var(--neomorph-bg)',
                border: '1px solid var(--neomorph-border)',
                boxShadow: '6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)',
              }}
              aria-label="Go to home"
            >
              <Home className="w-4 h-4 text-[var(--text-secondary)]" />
            </button>

            <button
              onClick={() => setOpenMenu(openMenu === 'book' ? null : 'book')}
              className="flex items-center gap-2 rounded-full px-4 py-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                boxShadow: 'inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)',
                backgroundColor: 'var(--neomorph-bg)',
              }}
              aria-label="Select book"
            >
              <BookOpen className="w-4 h-4 text-[var(--text-secondary)]" />
              <span className="text-[10px] tracking-[0.2em] uppercase text-[var(--text-secondary)]">
                {bookDisplayName} | <span style={{ fontFamily: "'Suez One', serif" }}>{bookHebrew}</span>
              </span>
            </button>

            <button
              onClick={() => setOpenMenu(openMenu === 'chapter' ? null : 'chapter')}
              className="flex items-center gap-2 rounded-full px-4 py-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                boxShadow: 'inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)',
                backgroundColor: 'var(--neomorph-bg)',
              }}
              aria-label="Select chapter"
            >
              <span className="text-[10px] tracking-[0.2em] uppercase text-[var(--text-secondary)]">CH</span>
              <span className="text-xs text-[var(--text-secondary)]">{chapter}</span>
            </button>

            <button
              onClick={() => setOpenMenu(openMenu === 'verse' ? null : 'verse')}
              className="flex items-center gap-2 rounded-full px-4 py-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                boxShadow: 'inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)',
                backgroundColor: 'var(--neomorph-bg)',
              }}
              aria-label="Select verse"
            >
              <span className="text-[10px] tracking-[0.2em] uppercase text-[var(--text-secondary)]">VS</span>
              <span className="text-xs text-[var(--text-secondary)]">{verse}</span>
            </button>

          </div>

          <div className="flex flex-1 items-center justify-center gap-2">
            <button
              onClick={onPreviousVerse}
              disabled={!hasPreviousVerse}
              className="rounded-full p-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                backgroundColor: 'var(--neomorph-bg)',
                border: '1px solid var(--neomorph-border)',
                boxShadow: '6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)',
              }}
              aria-label="Previous verse"
            >
              <ChevronUp
                className={`h-4 w-4 ${hasPreviousVerse ? 'text-[var(--text-secondary)]' : 'text-[var(--text-secondary)]/40'}`}
              />
            </button>
            <button
              onClick={onNextVerse}
              disabled={!hasNextVerse}
              className="rounded-full p-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                backgroundColor: 'var(--neomorph-bg)',
                border: '1px solid var(--neomorph-border)',
                boxShadow: '6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)',
              }}
              aria-label="Next verse"
            >
              <ChevronDown
                className={`h-4 w-4 ${hasNextVerse ? 'text-[var(--text-secondary)]' : 'text-[var(--text-secondary)]/40'}`}
              />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onFeaturesClick}
              className="flex items-center gap-2 rounded-full px-4 py-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                background: 'linear-gradient(135deg, rgba(198,143,85,0.85), rgba(176,122,60,0.65))',
                color: '#ffffff',
                border: '1px solid rgba(198,143,85,0.6)',
                boxShadow: '0 8px 20px rgba(13,39,80,0.16)',
                backdropFilter: 'blur(16px)',
              }}
              aria-label="Open features"
            >
              <span className="text-xs tracking-[0.2em] uppercase">Features</span>
            </button>

            <button
              onClick={onDonateClick}
              className="flex items-center gap-2 rounded-full px-4 py-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
              style={{
                fontFamily: "'Inter', sans-serif",
                backgroundColor: 'var(--accent-darker)',
                color: '#ffffff',
                boxShadow: '4px 4px 10px var(--neomorph-shadow-dark)',
              }}
              aria-label="Donate"
            >
              <Heart className="w-4 h-4" />
              <span className="text-xs tracking-[0.2em] uppercase">Donate</span>
            </button>

            <button
              onClick={() => setOpenMenu(openMenu === 'settings' ? null : 'settings')}
              className="rounded-full p-3 transition-all hover:scale-[1.05] active:scale-[0.98]"
              style={{
                backgroundColor: 'var(--neomorph-bg)',
                boxShadow: '6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)',
                border: '1px solid var(--neomorph-border)',
              }}
              aria-label="Open settings"
            >
              <Settings className="w-4 h-4 text-[var(--text-secondary)]" />
            </button>
          </div>
        </div>
      </NeumorphCard>

      {openMenu === 'settings' && (
        <div className="absolute right-0 mt-4 w-[320px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-5 z-30">
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {theme === 'dark' ? (
                  <Moon className="w-4 h-4 text-[var(--text-secondary)]" />
                ) : (
                  <Sun className="w-4 h-4 text-[var(--text-secondary)]" />
                )}
                <span className="text-sm text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Theme
                </span>
              </div>
              <NeumorphicToggle
                enabled={theme === 'dark'}
                onToggle={() => onThemeChange(theme === 'light' ? 'dark' : 'light')}
                ariaLabel="Toggle dark theme"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <ScrollText className="w-4 h-4 text-[var(--text-secondary)]" />
                <span className="text-sm text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Qumran variants
                </span>
              </div>
              <NeumorphicToggle
                enabled={showQumran}
                onToggle={() => onQumranChange(!showQumran)}
                ariaLabel="Toggle Qumran variants"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Eye className="w-4 h-4 text-[var(--text-secondary)]" />
                <span className="text-sm text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Hebrew only
                </span>
              </div>
              <NeumorphicToggle
                enabled={hebrewOnly}
                onToggle={() => onHebrewOnlyChange(!hebrewOnly)}
                ariaLabel="Toggle Hebrew only"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-[var(--text-secondary)]">
                  <HebrewIcon />
                </span>
                <span className="text-sm text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Nikud
                </span>
              </div>
              <NeumorphicToggle
                enabled={showNikud}
                onToggle={() => onNikudChange(!showNikud)}
                ariaLabel="Toggle nikud"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-[var(--text-secondary)]">
                  <HebrewIcon />
                </span>
                <span className="text-sm text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Cantillation
                </span>
              </div>
              <NeumorphicToggle
                enabled={showCantillation}
                onToggle={() => onCantillationChange(!showCantillation)}
                ariaLabel="Toggle cantillation"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <ScrollText className="w-4 h-4 text-[var(--text-secondary)]" />
                <span className="text-sm text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Full chapter
                </span>
              </div>
              <NeumorphicToggle
                enabled={showFullChapter}
                onToggle={() => onFullChapterChange(!showFullChapter)}
                ariaLabel="Toggle full chapter"
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Languages className="w-4 h-4 text-[var(--text-secondary)]" />
                <span className="text-sm text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Language
                </span>
              </div>
              <select
                value={language}
                onChange={(event) => onLanguageChange(event.target.value as 'en' | 'es' | 'he')}
                className="rounded-full px-3 py-2 text-xs text-[var(--text-primary)]"
                style={{
                  fontFamily: "'Inter', sans-serif",
                  backgroundColor: 'var(--neomorph-bg)',
                  border: '1px solid var(--neomorph-border)',
                  boxShadow: 'inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)',
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


      {openMenu === 'book' && (
        <div className="absolute left-0 mt-4 w-[280px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-4 z-30">
          <div className="max-h-[360px] overflow-y-auto space-y-2">
            {books.map((item) => (
              <button
                key={item.name}
                onClick={() => {
                  onBookChange(item.name);
                  setOpenMenu(null);
                }}
                className={`w-full flex items-center justify-between rounded-xl px-4 py-3 transition-all ${
                  item.name === book
                    ? 'bg-[var(--accent-strong)] text-white'
                    : 'bg-[var(--muted)] text-[var(--text-primary)]'
                }`}
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                <span className="text-xs tracking-[0.2em] uppercase">
                  {language === "es" ? item.spanish : item.name}
                </span>
                <span className="text-sm" style={{ fontFamily: "'Suez One', serif" }}>{item.hebrew}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {openMenu === 'chapter' && (
        <div className="absolute left-0 mt-4 w-[280px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-4 z-30">
          <div className="grid grid-cols-5 gap-2">
            {chapters.map((item) => (
              <button
                key={item}
                onClick={() => {
                  onChapterChange(item);
                  setOpenMenu(null);
                }}
                className={`rounded-xl px-2 py-2 text-xs transition-all ${
                  item === chapter
                    ? 'bg-[var(--accent-strong)] text-white'
                    : 'bg-[var(--muted)] text-[var(--text-primary)]'
                }`}
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}

      {openMenu === 'verse' && (
        <div className="absolute left-0 mt-4 w-[280px] rounded-2xl border border-[var(--glass-border)] bg-[var(--glass-surface)] backdrop-blur-[16px] shadow-[0_8px_32px_0_var(--glass-shadow)] p-4 z-30">
          <div className="grid grid-cols-5 gap-2 max-h-[320px] overflow-y-auto">
            {verses.map((item) => (
              <button
                key={item}
                onClick={() => {
                  onVerseChange(item);
                  setOpenMenu(null);
                }}
                className={`rounded-xl px-2 py-2 text-xs transition-all ${
                  item === verse
                    ? 'bg-[var(--accent-strong)] text-white'
                    : 'bg-[var(--muted)] text-[var(--text-primary)]'
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
