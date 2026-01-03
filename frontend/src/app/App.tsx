import React, { useState } from 'react';
import { DavarLogo } from './components/DavarLogo';
import { GlassButton } from './components/GlassButton';
import { GlassCard } from './components/GlassCard';
import { NavigationBar } from './components/NavigationBar';
import { VerseDisplay } from './components/VerseDisplay';
import { BottomSheet } from './components/BottomSheet';
import { WordCard } from './components/WordCard';
import { SettingsScreen } from './components/SettingsScreen';
import { DesignTokens } from './components/DesignTokens';
import { ComponentShowcase } from './components/ComponentShowcase';
import { StyleGuide } from './components/StyleGuide';
import { LaunchScreen } from './components/LaunchScreen';
import { SplashScreen } from './components/SplashScreen';
import { NavigationSelector } from './components/NavigationSelector';
import { BookSelector } from './components/BookSelector';
import { BottomNavBar } from './components/BottomNavBar';
import { ChapterVerseSelector } from './components/ChapterVerseSelector';
import { SwipeIndicator } from './components/SwipeIndicator';
import { DesignSystemExport } from './components/DesignSystemExport';
import { Settings, Home, BookOpen, FileText } from 'lucide-react';
import { X } from 'lucide-react';

// Sample data
const sampleVerses = {
  'Genesis-1-1': {
    hebrew: 'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
    translation: 'In the beginning God created the heavens and the earth.',
    translationEs: 'En el principio creó Dios los cielos y la tierra.',
    translationHe: 'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
    qumran: 'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֶת הַשָּׁמַיִם וְאֶת הָאָרֶץ',
    qumranTranslation: 'In the beginning God created the heavens and the earth. (Qumran variant)',
  },
  'Genesis-1-2': {
    hebrew: 'וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם',
    translation: 'Now the earth was formless and empty, darkness was over the surface of the deep.',
    translationEs: 'Y la tierra estaba desordenada y vacía, y las tinieblas estaban sobre la faz del abismo.',
    translationHe: 'וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם',
  },
  'Genesis-1-3': {
    hebrew: 'וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר',
    translation: 'And God said, "Let there be light," and there was light.',
    translationEs: 'Y dijo Dios: Sea la luz; y fue la luz.',
    translationHe: 'וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר',
  },
  'Psalms-23-1': {
    hebrew: 'יְהוָה רֹעִי לֹא אֶחְסָר',
    translation: 'The LORD is my shepherd, I lack nothing.',
    translationEs: 'Jehová es mi pastor; nada me faltará.',
    translationHe: 'יְהוָה רֹעִי לֹא אֶחְסָר',
  },
};

const booksData: { [key: string]: { en: string; es: string; he: string } } = {
  'Genesis': { en: 'Genesis', es: 'Génesis', he: 'בראשית' },
  'Exodus': { en: 'Exodus', es: 'Éxodo', he: 'שמות' },
  'Psalms': { en: 'Psalms', es: 'Salmos', he: 'תהלים' },
};

const sampleWordData = {
  'אֱלֹהִים': {
    word: 'אֱלֹהִים',
    meanings: ['God', 'Divine being', 'Supreme deity'],
    root: 'אֵל',
    instances: [
      { verse: 'Gen 1:1', text: 'בָּרָא אֱלֹהִים' },
      { verse: 'Gen 1:3', text: 'וַיֹּאמֶר אֱלֹהִים' },
      { verse: 'Gen 1:4', text: 'וַיַּרְא אֱלֹהִים' },
      { verse: 'Gen 1:5', text: 'וַיִּקְרָא אֱלֹהִים' },
      { verse: 'Gen 1:6', text: 'וַיֹּאמֶר אֱלֹהִים' },
      { verse: 'Gen 1:7', text: 'וַיַּעַשׂ אֱלֹהִים' },
    ],
  },
  'בְּרֵאשִׁית': {
    word: 'בְּרֵאשִׁית',
    meanings: ['In the beginning', 'At first', 'Initially'],
    root: 'רֵאשִׁית',
    instances: [
      { verse: 'Gen 1:1', text: 'בְּרֵאשִׁית בָּרָא' },
    ],
  },
};

export default function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [book, setBook] = useState('Genesis');
  const [chapter, setChapter] = useState(1);
  const [verse, setVerse] = useState(1);
  const [showWordSheet, setShowWordSheet] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showDesignSystem, setShowDesignSystem] = useState(false);
  const [showLaunch, setShowLaunch] = useState(true);
  const [showNavigationSelector, setShowNavigationSelector] = useState(false);
  const [showBookSelector, setShowBookSelector] = useState(false);
  const [showChapterVerseSelector, setShowChapterVerseSelector] = useState(false);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [language, setLanguage] = useState<'en' | 'es' | 'he'>('en');
  const [showQumran, setShowQumran] = useState(true);
  
  // Onboarding hint state (shows until word sheet is opened)
  const [hasOpenedWordSheet, setHasOpenedWordSheet] = useState(false);
  const showOnboardingHint = !hasOpenedWordSheet;

  // Settings modal swipe state
  const [settingsTouchStart, setSettingsTouchStart] = useState(0);
  const [settingsTouchEnd, setSettingsTouchEnd] = useState(0);

  const verseKey = `${book}-${chapter}-${verse}`;
  const currentVerse = sampleVerses[verseKey as keyof typeof sampleVerses] || sampleVerses['Genesis-1-1'];
  
  // Get previous and next verse snippets
  const prevVerseKey = `${book}-${chapter}-${verse - 1}`;
  const nextVerseKey = `${book}-${chapter}-${verse + 1}`;
  const previousVerse = sampleVerses[prevVerseKey as keyof typeof sampleVerses];
  const nextVerse = sampleVerses[nextVerseKey as keyof typeof sampleVerses];
  
  // Get book names
  const bookData = booksData[book] || { en: 'Genesis', es: 'Génesis', he: 'בְּרֵאשִׁית' };
  const bookName = language === 'he' ? bookData.he : (language === 'es' ? bookData.es : bookData.en);
  const bookNameHebrew = bookData.he;

  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    setTheme(newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleThemeToggle = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    handleThemeChange(newTheme);
  };

  const handleWordClick = (word: string) => {
    setSelectedWord(word);
    setShowWordSheet(true);
    setHasOpenedWordSheet(true);
  };

  const handleNextVerse = () => {
    setVerse((prev) => Math.min(prev + 1, 30));
  };

  const handlePrevVerse = () => {
    setVerse((prev) => Math.max(prev - 1, 1));
  };

  // Handle swipe down to dismiss settings
  const handleSettingsTouchStart = (e: React.TouchEvent) => {
    setSettingsTouchStart(e.targetTouches[0].clientY);
  };

  const handleSettingsTouchMove = (e: React.TouchEvent) => {
    setSettingsTouchEnd(e.targetTouches[0].clientY);
  };

  const handleSettingsTouchEnd = () => {
    if (settingsTouchStart - settingsTouchEnd < -100) {
      // Swipe down detected (threshold: 100px)
      setShowSettings(false);
    }
  };

  // Show launch screen
  if (showLaunch) {
    return <LaunchScreen onComplete={() => setShowLaunch(false)} />;
  }

  return (
    <div className="min-h-screen bg-background transition-colors duration-300">
      {/* Mobile Container */}
      <div className="max-w-md mx-auto min-h-screen bg-background shadow-2xl relative">
        
        {/* Design System View */}
        {showDesignSystem ? (
          <div className="relative">
            {/* Back button */}
            <button
              onClick={() => setShowDesignSystem(false)}
              className="fixed top-6 right-6 z-50 w-12 h-12 bg-[var(--accent)] text-white rounded-full shadow-lg hover:scale-110 transition-transform flex items-center justify-center"
              aria-label="Back to app"
            >
              <X className="w-6 h-6" />
            </button>
            <DesignSystemExport theme={theme} onThemeChange={handleThemeChange} />
          </div>
        ) : showNavigationSelector ? (
          // Navigation Selector View
          <div className="min-h-screen">
            <header className="sticky top-0 z-30 bg-[var(--glass-surface)] backdrop-blur-xl border-b border-[var(--glass-border)]">
              <div className="flex items-center justify-between p-4">
                <button
                  onClick={() => setShowNavigationSelector(false)}
                  className="p-2 rounded-full hover:bg-[var(--muted)] transition-colors"
                >
                  <Home className="w-5 h-5 text-[var(--text-secondary)]" />
                </button>
                <h2 style={{ fontFamily: "'Inter', sans-serif" }}>Davar</h2>
                <div className="w-9" /> {/* Spacer */}
              </div>
            </header>
            <main className="px-4 py-6">
              <NavigationSelector
                book={book}
                chapter={chapter}
                verse={verse}
                onBookChange={setBook}
                onChapterChange={setChapter}
                onVerseChange={setVerse}
                onClose={() => setShowNavigationSelector(false)}
              />
            </main>
          </div>
        ) : showBookSelector ? (
          // Book Selector View - Full Screen
          <BookSelector
            currentBook={book}
            onBookSelect={setBook}
            onClose={() => setShowBookSelector(false)}
            language={language}
          />
        ) : showChapterVerseSelector ? (
          // Chapter and Verse Selector View - Full Screen
          <ChapterVerseSelector
            book={book}
            currentChapter={chapter}
            currentVerse={verse}
            onSelect={(newChapter, newVerse) => {
              setChapter(newChapter);
              setVerse(newVerse);
            }}
            onClose={() => setShowChapterVerseSelector(false)}
          />
        ) : (
          // Main Verse View
          <>
            {/* Minimal Header with Logo */}
            <header className="absolute top-0 left-0 right-0 z-30 flex items-center justify-center p-6">
              <button
                onClick={handleThemeToggle}
                className="hover:opacity-80 transition-opacity"
                aria-label="Toggle theme"
              >
                <DavarLogo size="sm" theme={theme} />
              </button>
            </header>

            {/* Main Content - Centered Verse */}
            <main className="min-h-screen flex flex-col items-center justify-center px-6 py-24 pb-32">
              <div className="max-w-lg w-full">
                {/* Verse Display */}
                <VerseDisplay
                  hebrewText={currentVerse.hebrew}
                  translation={language === 'es' ? currentVerse.translationEs : currentVerse.translation}
                  qumranText={currentVerse.qumran}
                  qumranTranslation={currentVerse.qumranTranslation}
                  verseRef={`${book} ${chapter}:${verse}`}
                  verseNumber={verse}
                  bookName={bookName}
                  bookNameHebrew={bookNameHebrew}
                  language={language}
                  onBookNameClick={() => setShowBookSelector(true)}
                  onWordClick={handleWordClick}
                  previousVerseSnippet={previousVerse?.hebrew.split(' ').slice(0, 3).join(' ')}
                  nextVerseSnippet={nextVerse?.hebrew.split(' ').slice(0, 3).join(' ')}
                  showOnboardingHint={showOnboardingHint}
                  showQumran={showQumran}
                  onSwipeUp={handlePrevVerse}
                  onSwipeDown={handleNextVerse}
                />
              </div>
            </main>

            {/* Bottom Navigation Bar */}
            <BottomNavBar
              onHomeClick={() => setShowNavigationSelector(true)}
              onChapterVerseClick={() => setShowChapterVerseSelector(true)}
              onSettingsClick={() => setShowSettings(true)}
            />

            {/* Floating Design System Export Button */}
            <button
              onClick={() => setShowDesignSystem(true)}
              className="fixed bottom-32 right-6 w-14 h-14 bg-[var(--accent)] text-white rounded-full shadow-lg hover:scale-110 transition-transform z-40 flex items-center justify-center"
              aria-label="View Design System Export"
            >
              <FileText className="w-6 h-6" />
            </button>
          </>
        )}

        {/* Bottom Sheet for Word Details */}
        <BottomSheet isOpen={showWordSheet} onClose={() => setShowWordSheet(false)}>
          {selectedWord && sampleWordData[selectedWord as keyof typeof sampleWordData] && (
            <WordCard
              {...sampleWordData[selectedWord as keyof typeof sampleWordData]}
              onInstanceClick={(verseRef) => {
                console.log('Navigate to:', verseRef);
                setShowWordSheet(false);
              }}
            />
          )}
        </BottomSheet>

        {/* Settings Modal - Swipeable Bottom Sheet */}
        {showSettings && (
          <div 
            className="fixed inset-0 z-50 flex items-end"
            onClick={() => setShowSettings(false)}
          >
            {/* Backdrop - More transparent */}
            <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
            
            {/* Settings Sheet */}
            <div 
              className="relative w-full max-w-md mx-auto bg-[var(--glass-surface)] backdrop-blur-[45px] rounded-t-[32px] border-t-2 border-x-2 border-[var(--glass-border)] shadow-[0_-8px_32px_rgba(0,0,0,0.3)] animate-slide-up"
              onClick={(e) => e.stopPropagation()}
              style={{
                maxHeight: '85vh',
                animation: 'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
              onTouchStart={handleSettingsTouchStart}
              onTouchMove={handleSettingsTouchMove}
              onTouchEnd={handleSettingsTouchEnd}
            >
              {/* Drag Handle */}
              <div className="flex justify-center pt-3 pb-2">
                <div className="w-12 h-1.5 bg-[var(--text-secondary)]/30 rounded-full" />
              </div>

              {/* Header with DAVAR and Close */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--glass-border)]">
                <h2 
                  className="text-xl tracking-[0.25em]" 
                  style={{ fontFamily: "'Suez One', serif" }}
                >
                  DAVAR
                </h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="p-2 rounded-full hover:bg-[var(--muted)] transition-colors"
                  aria-label="Close settings"
                >
                  <svg className="w-6 h-6 text-[var(--text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Scrollable Content */}
              <div className="overflow-y-auto px-4 py-6" style={{ maxHeight: 'calc(85vh - 120px)' }}>
                <SettingsScreen
                  theme={theme}
                  onThemeChange={handleThemeChange}
                  language={language}
                  onLanguageChange={setLanguage}
                  showQumran={showQumran}
                  onQumranChange={setShowQumran}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes slideUp {
          from {
            transform: translateY(100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}