import React, { useEffect, useMemo, useState } from 'react';
import { HomeScreen } from './components/HomeScreen';
import { VerseDisplay } from './components/VerseDisplay';
import { BottomSheet } from './components/BottomSheet';
import { WordCard } from './components/WordCard';
import { DesignSystemExport } from './components/DesignSystemExport';
import { MobileDesignSystemGuide } from './components/MobileDesignSystemGuide';
import { NavigationBar } from './components/NavigationBar';
import { NeumorphCard } from './components/NeumorphCard';
import { DonateScreen } from './components/DonateScreen';
import { FeaturesScreen } from './components/FeaturesScreen';
import { getBooks, getChapterCount, getChapterVerses, getVerse, getVerseCount } from './services/verseService';
import { getWordAnalysisByStrong, getWordAnalysisByText } from './services/lexiconService';
import type { WordResponse } from './services/verseService';

type Screen = 'home' | 'verse' | 'settings' | 'donate' | 'features';

export default function App() {
  // App state
  const [currentScreen, setCurrentScreen] = useState<Screen>('verse');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [language, setLanguage] = useState<'en' | 'es' | 'he'>('en');
  
  // Bible navigation state
  const [currentBook, setCurrentBook] = useState('Genesis');
  const [currentChapter, setCurrentChapter] = useState(1);
  const [currentVerse, setCurrentVerse] = useState(1);
  
  // View settings
  const [showQumran, setShowQumran] = useState(false);
  const [showFullChapter, setShowFullChapter] = useState(false);
  const [hebrewOnly, setHebrewOnly] = useState(false);
  const [showNikud, setShowNikud] = useState(true);
  const [showCantillation, setShowCantillation] = useState(false);
  
  // UI state
  const [selectedWord, setSelectedWord] = useState<WordResponse | null>(null);
  const [showMobileDesignGuide, setShowMobileDesignGuide] = useState(false);
  const [showDesignSystem, setShowDesignSystem] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Get Hebrew book name
  const getHebrewBookName = (book: string): string => {
    const hebrewNames: { [key: string]: string } = {
      'Genesis': 'בראשית',
      'Exodus': 'שמות',
      'Leviticus': 'ויקרא',
      'Numbers': 'במדבר',
      'Deuteronomy': 'דברים',
    };
    return hebrewNames[book] || book;
  };

  // Handle theme changes
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // Handle word click
  const handleWordClick = (word: WordResponse) => {
    setSelectedWord(word);
  };

  // Handle navigation to specific verse
  const handleNavigateToVerse = (verseRef: string) => {
    // Parse verse reference like "Gen 1:1"
    const parts = verseRef.split(' ');
    if (parts.length === 2) {
      const [chapter, verse] = parts[1].split(':');
      setCurrentChapter(parseInt(chapter));
      setCurrentVerse(parseInt(verse));
      setSelectedWord(null);
    }
  };

  // Get current verse data
  const currentVerseData = useMemo(
    () => getVerse(currentBook, currentChapter, currentVerse),
    [currentBook, currentChapter, currentVerse]
  );

  const chapterVerses = useMemo(
    () => getChapterVerses(currentBook, currentChapter),
    [currentBook, currentChapter]
  );

  const availableBooks = useMemo(() => getBooks(), []);
  const bookOptions = useMemo(
    () => availableBooks.map((book) => ({ name: book, hebrew: getHebrewBookName(book) })),
    [availableBooks]
  );

  const chapterCount = useMemo(
    () => getChapterCount(currentBook),
    [currentBook]
  );

  const verseCount = useMemo(
    () => getVerseCount(currentBook, currentChapter),
    [currentBook, currentChapter]
  );

  const selectedWordAnalysis = useMemo(() => {
    if (!selectedWord) return null;
    return getWordAnalysisByStrong(selectedWord.strong) ?? getWordAnalysisByText(selectedWord.text);
  }, [selectedWord]);

  const isSplitView = Boolean(selectedWord && !isMobile);
  const [isWordPanelVisible, setIsWordPanelVisible] = useState(false);

  useEffect(() => {
    if (selectedWord) {
      setIsWordPanelVisible(true);
      return undefined;
    }

    if (isWordPanelVisible) {
      const timeout = window.setTimeout(() => setIsWordPanelVisible(false), 220);
      return () => window.clearTimeout(timeout);
    }

    return undefined;
  }, [selectedWord, isWordPanelVisible]);

  useEffect(() => {
    setSelectedWord(null);
  }, [currentBook, currentChapter, currentVerse]);

  useEffect(() => {
    const media = window.matchMedia('(max-width: 767px)');
    const update = () => setIsMobile(media.matches);
    update();
    media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, []);

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--background)' }}>
      <div className="sticky top-0 z-40 px-6 pt-6">
        <div className="max-w-7xl mx-auto">
          <NavigationBar
            book={currentBook}
            bookHebrew={getHebrewBookName(currentBook)}
            chapter={currentChapter}
            verse={currentVerse}
            books={bookOptions}
            chapterCount={chapterCount}
            verseCount={verseCount}
            onBookChange={(book) => {
              setCurrentBook(book);
              setCurrentChapter(1);
              setCurrentVerse(1);
              setCurrentScreen('verse');
            }}
            onChapterChange={(chapter) => {
              setCurrentChapter(chapter);
              setCurrentVerse(1);
            }}
            onVerseChange={(verse) => setCurrentVerse(verse)}
            onHomeClick={() => setCurrentScreen('home')}
            onDonateClick={() => setCurrentScreen('donate')}
            onFeaturesClick={() => setCurrentScreen('features')}
            theme={theme}
            onThemeChange={setTheme}
            language={language}
            onLanguageChange={setLanguage}
            showQumran={showQumran}
            onQumranChange={setShowQumran}
            showFullChapter={showFullChapter}
            onFullChapterChange={setShowFullChapter}
            hebrewOnly={hebrewOnly}
            onHebrewOnlyChange={setHebrewOnly}
            showNikud={showNikud}
            onNikudChange={setShowNikud}
            showCantillation={showCantillation}
            onCantillationChange={setShowCantillation}
          />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="px-6 pb-32 pt-6">
        <div className="max-w-7xl mx-auto">
          {currentScreen === 'home' && (
            <HomeScreen language={language} />
          )}

          {currentScreen === 'donate' && (
            <DonateScreen />
          )}

          {currentScreen === 'features' && (
            <FeaturesScreen />
          )}

          {currentScreen === 'verse' && currentVerseData && (
            <div className={`grid gap-6 ${isSplitView ? 'md:grid-cols-[7fr_3fr]' : 'md:grid-cols-1'}`}>
              <div className={`min-h-[70vh] ${showFullChapter ? '' : 'flex items-center justify-center'} ${isSplitView ? '' : 'mx-auto w-full max-w-3xl'} verse-panel-shell ${isSplitView ? 'verse-panel-split' : 'verse-panel-centered'}`}>
                <VerseDisplay
                  hebrewText={currentVerseData.hebrew}
                  translation={currentVerseData.translation ?? ''}
                  verseRef={`${currentBook} ${currentChapter}:${currentVerse}`}
                  verseNumber={currentVerse}
                  bookName={currentBook}
                  bookNameHebrew={getHebrewBookName(currentBook)}
                  book={currentBook}
                  chapter={currentChapter}
                  language={language}
                  onWordClick={handleWordClick}
                  showQumran={showQumran}
                  showFullChapter={showFullChapter}
                  hebrewOnly={hebrewOnly}
                  showNikud={showNikud}
                  showCantillation={showCantillation}
                  chapterVerses={chapterVerses}
                  words={currentVerseData.words}
                  dssVariants={currentVerseData.dss}
                  selectedWord={selectedWord?.text ?? null}
                  previousVerseSnippet={currentVerse > 1 ? 'Previous verse...' : undefined}
                  nextVerseSnippet={currentVerse < chapterVerses.length ? 'Next verse...' : undefined}
                  onSwipeUp={() => {
                    if (currentVerse > 1) {
                      setCurrentVerse(currentVerse - 1);
                    }
                  }}
                  onSwipeDown={() => {
                    if (currentVerse < chapterVerses.length) {
                      setCurrentVerse(currentVerse + 1);
                    }
                  }}
                />
              </div>

              <div className="hidden md:block">
                {(selectedWord || isWordPanelVisible) && (
                  <NeumorphCard
                    className={`p-6 sticky top-24 word-panel-shell ${selectedWord ? 'word-panel-open' : 'word-panel-closed'}`}
                  >
                    {selectedWord && (
                      <WordCard
                        word={selectedWordAnalysis?.word ?? selectedWord.text}
                        transliteration={selectedWordAnalysis?.transliteration}
                        meanings={selectedWordAnalysis?.meanings ?? []}
                        root={selectedWordAnalysis?.root}
                        rootTransliteration={selectedWordAnalysis?.rootTransliteration}
                        rootMeaning={selectedWordAnalysis?.rootMeaning}
                        instances={selectedWordAnalysis?.instances ?? []}
                        onInstanceClick={handleNavigateToVerse}
                        onClose={() => setSelectedWord(null)}
                      />
                    )}
                  </NeumorphCard>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Navigation (mobile only) */}
      <div className="md:hidden">
        <div className="h-10" />
      </div>

      {/* Word Analysis Bottom Sheet (mobile only) */}
      {isMobile && selectedWord && (
        <BottomSheet
          isOpen={!!selectedWord}
          onClose={() => setSelectedWord(null)}
          title=""
        >
          <WordCard
            word={selectedWordAnalysis?.word ?? selectedWord.text}
            transliteration={selectedWordAnalysis?.transliteration}
            meanings={selectedWordAnalysis?.meanings ?? []}
            root={selectedWordAnalysis?.root}
            rootTransliteration={selectedWordAnalysis?.rootTransliteration}
            rootMeaning={selectedWordAnalysis?.rootMeaning}
            instances={selectedWordAnalysis?.instances ?? []}
            onInstanceClick={handleNavigateToVerse}
            onClose={() => setSelectedWord(null)}
          />
        </BottomSheet>
      )}

      {/* Design System Export */}
      {showDesignSystem && (
        <div className="fixed inset-0 z-50 overflow-auto">
          <DesignSystemExport 
            theme={theme}
            onThemeChange={setTheme}
            onClose={() => setShowDesignSystem(false)}
          />
        </div>
      )}

      {/* Mobile Design System Guide */}
      {showMobileDesignGuide && (
        <div className="fixed inset-0 z-50 overflow-auto bg-[var(--background)]">
          <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
              <button
                onClick={() => setShowMobileDesignGuide(false)}
                className="mb-8 px-6 py-3 bg-[var(--primary)] text-white rounded-full hover:scale-105 transition-all"
                style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
              >
                ← Back to App
              </button>
              <MobileDesignSystemGuide />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}