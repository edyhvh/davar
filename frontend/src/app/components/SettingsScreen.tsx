import React from 'react';
import { GlassCard } from './GlassCard';
import { Moon, Sun, Globe, BookOpen, Scroll, Type } from 'lucide-react';

interface SettingsScreenProps {
  theme: 'light' | 'dark';
  onThemeChange: (theme: 'light' | 'dark') => void;
  language: string;
  onLanguageChange: (language: string) => void;
  showQumran: boolean;
  onQumranChange: (show: boolean) => void;
  showFullChapter: boolean;
  onFullChapterChange: (show: boolean) => void;
  hebrewOnly: boolean;
  onHebrewOnlyChange: (show: boolean) => void;
}

const languages = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'es', name: 'Spanish', nativeName: 'Español' },
  { code: 'he', name: 'Hebrew', nativeName: 'עברית' },
];

const translations = {
  en: {
    general: 'General',
    theme: 'Theme',
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    language: 'Language',
    qumranVariants: 'Qumran Variants',
    qumranDescription: 'Show Dead Sea Scrolls text',
    fullChapter: 'Full Chapter',
    fullChapterDescription: 'Show full chapter text',
    hebrewOnly: 'Hebrew Only',
    hebrewOnlyDescription: 'Show text in Hebrew only',
  },
  es: {
    general: 'General',
    theme: 'Tema',
    darkMode: 'Modo Oscuro',
    lightMode: 'Modo Claro',
    language: 'Idioma',
    qumranVariants: 'Variantes de Qumrán',
    qumranDescription: 'Mostrar texto de los Rollos del Mar Muerto',
    fullChapter: 'Capítulo Completo',
    fullChapterDescription: 'Mostrar texto completo del capítulo',
    hebrewOnly: 'Sólo Hebreo',
    hebrewOnlyDescription: 'Mostrar texto solo en hebreo',
  },
  he: {
    general: 'כללי',
    theme: 'עיצוב',
    darkMode: 'מצב כהה',
    lightMode: 'מצב בהיר',
    language: 'שפה',
    qumranVariants: 'גרסאות קומראן',
    qumranDescription: 'הצג טקסט מגילות מדבר יהודה',
    fullChapter: 'פרק كامل',
    fullChapterDescription: 'הצג טקסט של פרק كامل',
    hebrewOnly: 'עברית בלבד',
    hebrewOnlyDescription: 'הצג טקסט רק בעברית',
  },
};

export function SettingsScreen({
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
}: SettingsScreenProps) {
  const [isLanguageOpen, setIsLanguageOpen] = React.useState(false);
  const selectedLanguage = languages.find(lang => lang.code === language) || languages[0];
  const dropdownRef = React.useRef<HTMLDivElement>(null);
  const t = translations[language as keyof typeof translations] || translations.en;

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsLanguageOpen(false);
      }
    };

    if (isLanguageOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isLanguageOpen]);

  return (
    <div className="space-y-6 pb-24">
      {/* General Section */}
      <div className="space-y-4">
        <h3 className="text-sm text-[var(--text-secondary)] px-2 uppercase tracking-wider" style={{ fontFamily: "'Inter', sans-serif" }}>
          {t.general}
        </h3>
        
        {/* Theme Toggle - NEUTRAL GLASS, Tekhelet ONLY on icon + toggle */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Icon container - Tekhelet accent */}
              <div className="p-3 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20">
                {theme === 'dark' ? (
                  <Moon className="w-6 h-6 text-[var(--accent)]" />
                ) : (
                  <Sun className="w-6 h-6 text-[var(--accent)]" />
                )}
              </div>
              <div>
                <div className="text-base font-medium mb-1" style={{ fontFamily: "'Inter', sans-serif" }}>{t.theme}</div>
                <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  {theme === 'dark' ? t.darkMode : t.lightMode}
                </div>
              </div>
            </div>
            {/* Toggle - Tekhelet ONLY when active */}
            <button
              onClick={() => onThemeChange(theme === 'light' ? 'dark' : 'light')}
              className={`
                relative w-20 h-11 rounded-full transition-all duration-300 shadow-[inset_0_2px_8px_rgba(0,0,0,0.15)] border border-[var(--glass-border)]
                ${theme === 'dark' ? 'bg-[var(--accent)]' : 'bg-gray-300'}
              `}
            >
              <div
                className={`
                  absolute top-1.5 w-8 h-8 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.2)] transition-transform duration-300 flex items-center justify-center
                  ${theme === 'dark' ? 'translate-x-10' : 'translate-x-1.5'}
                `}
              >
                {theme === 'dark' ? (
                  <Moon className="w-4 h-4 text-[var(--accent)]" />
                ) : (
                  <Sun className="w-4 h-4 text-gray-600" />
                )}
              </div>
            </button>
          </div>
        </GlassCard>

        {/* Language Selector */}
        <GlassCard className={`p-6 relative ${isLanguageOpen ? 'z-50' : 'z-10'}`}>
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              {/* Icon container - Tekhelet accent */}
              <div className="p-3 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20">
                <Globe className="w-6 h-6 text-[var(--accent)]" />
              </div>
              <div>
                <div className="text-base font-medium mb-1" style={{ fontFamily: "'Inter', sans-serif" }}>
                  {t.language}
                </div>
              </div>
            </div>

            {/* Custom Dropdown */}
            <div className="relative flex-shrink-0" ref={dropdownRef} style={{ minWidth: '160px' }}>
              <button
                onClick={() => setIsLanguageOpen(!isLanguageOpen)}
                className="w-full bg-[var(--glass-surface)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] rounded-2xl px-5 py-3 flex items-center justify-between hover:bg-[var(--glass-surface-elevated)] transition-all shadow-[0_4px_16px_0_var(--glass-shadow),inset_0_1px_0_0_var(--glass-highlight)]"
              >
                <span className="text-base text-[var(--foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  {selectedLanguage.nativeName}
                </span>
                <svg 
                  className={`w-5 h-5 text-[var(--text-secondary)] transition-transform ${isLanguageOpen ? 'rotate-180' : ''}`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown List */}
              {isLanguageOpen && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-[var(--glass-surface-elevated)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] rounded-2xl shadow-[0_12px_48px_var(--glass-shadow)] overflow-hidden z-[100]">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        onLanguageChange(lang.code);
                        setIsLanguageOpen(false);
                      }}
                      className={`w-full px-5 py-4 flex items-center justify-between hover:bg-[var(--muted)] transition-all ${
                        lang.code === language ? 'bg-[var(--muted)]' : ''
                      }`}
                    >
                      <span className="text-base text-[var(--foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                        {lang.nativeName}
                      </span>
                      {lang.code === language && (
                        <svg className="w-5 h-5 text-[var(--accent)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </GlassCard>

        {/* Qumran Toggle - NEUTRAL GLASS, Tekhelet ONLY on icon + toggle */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Icon container - Tekhelet accent */}
              <div className="p-3 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20">
                <BookOpen className="w-6 h-6 text-[var(--accent)]" />
              </div>
              <div>
                <div className="text-base font-medium mb-1" style={{ fontFamily: "'Inter', sans-serif" }}>{t.qumranVariants}</div>
                <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  {t.qumranDescription}
                </div>
              </div>
            </div>
            {/* Toggle - Tekhelet ONLY when active */}
            <button
              onClick={() => onQumranChange(!showQumran)}
              className={`
                relative w-20 h-11 rounded-full transition-all duration-300 shadow-[inset_0_2px_8px_rgba(0,0,0,0.15)] border border-[var(--glass-border)]
                ${showQumran ? 'bg-[var(--accent)]' : 'bg-gray-300'}
              `}
            >
              <div
                className={`
                  absolute top-1.5 w-8 h-8 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.2)] transition-transform duration-300 flex items-center justify-center
                  ${showQumran ? 'translate-x-10' : 'translate-x-1.5'}
                `}
              >
                <BookOpen className={`w-4 h-4 ${showQumran ? 'text-[var(--accent)]' : 'text-gray-600'}`} />
              </div>
            </button>
          </div>
        </GlassCard>

        {/* Full Chapter Toggle - NEUTRAL GLASS, Tekhelet ONLY on icon + toggle */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Icon container - Tekhelet accent */}
              <div className="p-3 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20">
                <Scroll className="w-6 h-6 text-[var(--accent)]" />
              </div>
              <div>
                <div className="text-base font-medium mb-1" style={{ fontFamily: "'Inter', sans-serif" }}>{t.fullChapter}</div>
                <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  {t.fullChapterDescription}
                </div>
              </div>
            </div>
            {/* Toggle - Tekhelet ONLY when active */}
            <button
              onClick={() => onFullChapterChange(!showFullChapter)}
              className={`
                relative w-20 h-11 rounded-full transition-all duration-300 shadow-[inset_0_2px_8px_rgba(0,0,0,0.15)] border border-[var(--glass-border)]
                ${showFullChapter ? 'bg-[var(--accent)]' : 'bg-gray-300'}
              `}
            >
              <div
                className={`
                  absolute top-1.5 w-8 h-8 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.2)] transition-transform duration-300 flex items-center justify-center
                  ${showFullChapter ? 'translate-x-10' : 'translate-x-1.5'}
                `}
              >
                <Scroll className={`w-4 h-4 ${showFullChapter ? 'text-[var(--accent)]' : 'text-gray-600'}`} />
              </div>
            </button>
          </div>
        </GlassCard>

        {/* Hebrew Only Toggle - NEUTRAL GLASS, Tekhelet ONLY on icon + toggle */}
        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {/* Icon container - Tekhelet accent */}
              <div className="p-3 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20">
                <Type className="w-6 h-6 text-[var(--accent)]" />
              </div>
              <div>
                <div className="text-base font-medium mb-1" style={{ fontFamily: "'Inter', sans-serif" }}>{t.hebrewOnly}</div>
                <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  {t.hebrewOnlyDescription}
                </div>
              </div>
            </div>
            {/* Toggle - Tekhelet ONLY when active */}
            <button
              onClick={() => onHebrewOnlyChange(!hebrewOnly)}
              className={`
                relative w-20 h-11 rounded-full transition-all duration-300 shadow-[inset_0_2px_8px_rgba(0,0,0,0.15)] border border-[var(--glass-border)]
                ${hebrewOnly ? 'bg-[var(--accent)]' : 'bg-gray-300'}
              `}
            >
              <div
                className={`
                  absolute top-1.5 w-8 h-8 bg-white rounded-full shadow-[0_4px_12px_rgba(0,0,0,0.2)] transition-transform duration-300 flex items-center justify-center
                  ${hebrewOnly ? 'translate-x-10' : 'translate-x-1.5'}
                `}
              >
                <Type className={`w-4 h-4 ${hebrewOnly ? 'text-[var(--accent)]' : 'text-gray-600'}`} />
              </div>
            </button>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}