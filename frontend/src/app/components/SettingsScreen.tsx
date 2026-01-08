import React from 'react';
import { GlassCard } from './GlassCard';

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
  onDesignSystemClick?: () => void;
}

// 2D Retro Pill Toggle inspired by the copper toggle switch
function RetroPillToggle({ 
  isOn, 
  onToggle
}: { 
  isOn: boolean; 
  onToggle: () => void;
}) {
  return (
    <button
      onClick={onToggle}
      className="relative bg-[var(--border)] rounded-full p-0.5 transition-all duration-300 flex-shrink-0"
      style={{ 
        width: '80px', 
        height: '40px',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.15)'
      }}
    >
      {/* Sliding pill */}
      <div
        className={`
          absolute top-0.5 h-[36px] w-[38px] rounded-full transition-all duration-300
          ${isOn 
            ? 'translate-x-[40px] bg-[var(--primary)]' 
            : 'translate-x-0.5 bg-[var(--muted)]'
          }
        `}
        style={{
          boxShadow: isOn 
            ? '0 2px 8px var(--accent-glow), inset 0 -2px 4px rgba(0,0,0,0.2)' 
            : '0 2px 4px rgba(0,0,0,0.1), inset 0 -2px 4px rgba(0,0,0,0.1)',
          border: isOn ? '2px solid var(--accent-dark)' : '2px solid var(--border)'
        }}
      />
    </button>
  );
}

// Retro On/Off Button Component inspired by vintage audio equipment
function RetroOnOffButton({ 
  isOn, 
  onToggle 
}: { 
  isOn: boolean; 
  onToggle: () => void;
}) {
  return (
    <button
      onClick={onToggle}
      className="relative flex flex-col items-center justify-center gap-2 group"
      style={{ width: '64px' }}
    >
      {/* Large circular button with light indicator */}
      <div 
        className={`
          relative w-14 h-14 rounded-full border-3 transition-all duration-300
          ${isOn 
            ? 'bg-[var(--primary)] border-[var(--accent-dark)] shadow-lg' 
            : 'bg-[var(--muted)] border-[var(--border)] shadow-sm'
          }
        `}
        style={{
          boxShadow: isOn 
            ? '0 0 20px var(--accent-glow), inset 0 2px 4px rgba(0,0,0,0.2)' 
            : 'inset 0 2px 4px rgba(0,0,0,0.1)',
          borderWidth: '3px'
        }}
      >
        {/* Inner light indicator - glows when on */}
        <div 
          className={`
            absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2
            w-6 h-6 rounded-full transition-all duration-300
            ${isOn 
              ? 'bg-white opacity-90' 
              : 'bg-[var(--text-secondary)] opacity-20'
            }
          `}
          style={{
            boxShadow: isOn 
              ? '0 0 12px rgba(255,255,255,0.8), 0 0 24px var(--accent-glow)' 
              : 'none'
          }}
        />
      </div>
      
      {/* ON/OFF label */}
      <div 
        className="text-xs font-bold tracking-wide uppercase"
        style={{ 
          fontFamily: "'Inter', sans-serif",
          color: isOn ? 'var(--primary)' : 'var(--text-secondary)'
        }}
      >
        {isOn ? 'ON' : 'OFF'}
      </div>
    </button>
  );
}

// Simple retro-style SVG icons
const RetroIcons = {
  Theme: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="8" fill="currentColor" opacity="0.3"/>
      <path d="M12 4 L12 12 L16 8 Z" fill="currentColor"/>
    </svg>
  ),
  Language: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="2" fill="none"/>
      <path d="M4 12 H20 M12 4 C14 8 14 16 12 20 M12 4 C10 8 10 16 12 20" stroke="currentColor" strokeWidth="2" fill="none"/>
    </svg>
  ),
  Qumran: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="4" width="12" height="16" stroke="currentColor" strokeWidth="2" fill="none" rx="1"/>
      <line x1="9" y1="8" x2="15" y2="8" stroke="currentColor" strokeWidth="2"/>
      <line x1="9" y1="12" x2="15" y2="12" stroke="currentColor" strokeWidth="2"/>
      <line x1="9" y1="16" x2="13" y2="16" stroke="currentColor" strokeWidth="2"/>
    </svg>
  ),
  Chapter: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M7 4 L7 20 M7 4 L14 4 C16 4 17 6 17 8 C17 10 16 12 14 12 L7 12 M7 12 L15 12 C17 12 18 14 18 16 C18 18 17 20 15 20 L7 20" stroke="currentColor" strokeWidth="2" fill="none"/>
    </svg>
  ),
  Hebrew: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M8 6 L8 18 M12 6 L12 18 M16 6 L16 12 M8 12 L16 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  DesignSystem: () => (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="4" y="4" width="7" height="7" stroke="currentColor" strokeWidth="2" fill="none"/>
      <rect x="13" y="4" width="7" height="7" stroke="currentColor" strokeWidth="2" fill="none"/>
      <rect x="4" y="13" width="7" height="7" stroke="currentColor" strokeWidth="2" fill="none"/>
      <rect x="13" y="13" width="7" height="7" stroke="currentColor" strokeWidth="2" fill="none"/>
    </svg>
  )
};

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
  onDesignSystemClick,
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
    <div className="pb-24">
      {/* General Section Header */}
      <h3 className="text-sm text-[var(--text-secondary)] px-6 py-4 uppercase tracking-wider font-bold" style={{ fontFamily: "'Inter', sans-serif" }}>
        {t.general}
      </h3>
      
      {/* Theme Toggle */}
      <div className="px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-[var(--text-secondary)]">
              <RetroIcons.Theme />
            </div>
            <div>
              <div className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>{t.theme}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-0.5" style={{ fontFamily: "'Inter', sans-serif" }}>
                {t.darkMode}
              </div>
            </div>
          </div>
          <RetroPillToggle
            isOn={theme === 'dark'}
            onToggle={() => onThemeChange(theme === 'light' ? 'dark' : 'light')}
          />
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-[var(--border)]" />

      {/* Language Selector */}
      <div className={`px-6 py-6 relative ${isLanguageOpen ? 'z-50' : 'z-10'}`}>
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="text-[var(--text-secondary)]">
              <RetroIcons.Language />
            </div>
            <div>
              <div className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                {t.language}
              </div>
            </div>
          </div>

          {/* Custom Dropdown */}
          <div className="relative flex-shrink-0" ref={dropdownRef} style={{ minWidth: '140px' }}>
            <button
              onClick={() => setIsLanguageOpen(!isLanguageOpen)}
              className="w-full bg-[var(--muted)] border-2 border-[var(--border)] rounded-[16px] px-4 py-2 flex items-center justify-between hover:bg-[var(--primary)]/10 transition-all"
            >
              <span className="text-sm text-[var(--foreground)] font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>
                {selectedLanguage.nativeName}
              </span>
              <svg 
                className={`w-4 h-4 text-[var(--text-secondary)] transition-transform ${isLanguageOpen ? 'rotate-180' : ''}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown List */}
            {isLanguageOpen && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-[var(--background)] border-2 border-[var(--border)] rounded-[16px] shadow-lg overflow-hidden z-[100]">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      onLanguageChange(lang.code);
                      setIsLanguageOpen(false);
                    }}
                    className={`w-full px-4 py-3 flex items-center justify-between hover:bg-[var(--muted)] transition-all ${
                      lang.code === language ? 'bg-[var(--muted)]' : ''
                    }`}
                  >
                    <span className="text-sm text-[var(--foreground)] font-medium" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {lang.nativeName}
                    </span>
                    {lang.code === language && (
                      <svg className="w-4 h-4 text-[var(--primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-[var(--border)]" />

      {/* Qumran Toggle */}
      <div className="px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-[var(--text-secondary)]">
              <RetroIcons.Qumran />
            </div>
            <div>
              <div className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>{t.qumranVariants}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-0.5" style={{ fontFamily: "'Inter', sans-serif" }}>
                {t.qumranDescription}
              </div>
            </div>
          </div>
          <RetroOnOffButton
            isOn={showQumran}
            onToggle={() => onQumranChange(!showQumran)}
          />
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-[var(--border)]" />

      {/* Full Chapter Toggle */}
      <div className="px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-[var(--text-secondary)]">
              <RetroIcons.Chapter />
            </div>
            <div>
              <div className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>{t.fullChapter}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-0.5" style={{ fontFamily: "'Inter', sans-serif" }}>
                {t.fullChapterDescription}
              </div>
            </div>
          </div>
          <RetroOnOffButton
            isOn={showFullChapter}
            onToggle={() => onFullChapterChange(!showFullChapter)}
          />
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-[var(--border)]" />

      {/* Hebrew Only Toggle */}
      <div className="px-6 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="text-[var(--text-secondary)]">
              <RetroIcons.Hebrew />
            </div>
            <div>
              <div className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>{t.hebrewOnly}</div>
              <div className="text-xs text-[var(--text-secondary)] mt-0.5" style={{ fontFamily: "'Inter', sans-serif" }}>
                {t.hebrewOnlyDescription}
              </div>
            </div>
          </div>
          <RetroOnOffButton
            isOn={hebrewOnly}
            onToggle={() => onHebrewOnlyChange(!hebrewOnly)}
          />
        </div>
      </div>

      {/* Design System Button */}
      {onDesignSystemClick && (
        <>
          {/* Divider */}
          <div className="border-t border-[var(--border)]" />
          
          <button
            onClick={onDesignSystemClick}
            className="px-6 py-6 flex items-center justify-between w-full hover:bg-[var(--muted)] transition-all"
          >
            <div className="flex items-center gap-4">
              <div className="text-[var(--text-secondary)]">
                <RetroIcons.DesignSystem />
              </div>
              <div>
                <div className="text-base font-semibold text-[var(--text-primary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Design System</div>
                <div className="text-xs text-[var(--text-secondary)] mt-0.5" style={{ fontFamily: "'Inter', sans-serif" }}>
                  View design components
                </div>
              </div>
            </div>
          </button>
        </>
      )}
    </div>
  );
}