import React, { useState, useEffect } from 'react';
import { LaunchScreen } from './components/LaunchScreen';
import { HomeScreen } from './components/HomeScreen';
import { VerseDisplay } from './components/VerseDisplay';
import { SettingsScreen } from './components/SettingsScreen';
import { BottomNavBar } from './components/BottomNavBar';
import { BookSelector } from './components/BookSelector';
import { ChapterVerseSelector } from './components/ChapterVerseSelector';
import { BottomSheet } from './components/BottomSheet';
import { WordCard } from './components/WordCard';

// Sample Bible data with Qumran variants
const sampleVerses = {
  'Genesis': {
    1: [
      {
        hebrew: 'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
        translation: 'In the beginning, God created the heavens and the earth.',
        wordVariants: {
          'בְּרֵאשִׁית': {
            qumranWord: 'בְּרֵאשִׁית',
            masoreticWord: 'בְּרֵאשִׁית',
            label: 'Beginning',
            color: 'yellow' as const,
          }
        }
      },
      {
        hebrew: 'וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם',
        translation: 'Now the earth was formless and empty, and darkness was over the surface of the deep.',
        wordVariants: {}
      },
      {
        hebrew: 'וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר',
        translation: 'And God said, "Let there be light," and there was light.',
        wordVariants: {}
      },
    ]
  }
};

// Sample word analysis data
const wordAnalysisData: { [key: string]: any } = {
  'בְּרֵאשִׁית': {
    word: 'בְּרֵאשִׁית',
    transliteration: 'bereshit',
    meanings: ['in beginning', 'at first', 'when beginning'],
    root: 'ראש',
    rootTransliteration: 'rosh',
    rootMeaning: 'head, beginning, chief',
    instances: [
      { verse: 'Gen 1:1', text: 'In the beginning God created...' },
      { verse: 'Gen 10:10', text: 'The beginning of his kingdom was...' },
    ]
  },
  'בָּרָא': {
    word: 'בָּרָא',
    transliteration: 'bara',
    meanings: ['created', 'brought into existence'],
    root: 'ברא',
    rootTransliteration: 'bara',
    rootMeaning: 'to create, shape, form',
    instances: [
      { verse: 'Gen 1:1', text: 'In the beginning God created...' },
      { verse: 'Gen 1:21', text: 'So God created the great creatures...' },
      { verse: 'Gen 1:27', text: 'So God created mankind...' },
    ]
  },
  'אֱלֹהִים': {
    word: 'אֱלֹהִים',
    transliteration: 'elohim',
    meanings: ['God', 'gods', 'divine beings'],
    root: 'אלה',
    rootTransliteration: 'elah',
    rootMeaning: 'deity, divine power',
    instances: [
      { verse: 'Gen 1:1', text: 'In the beginning God created...' },
      { verse: 'Gen 1:2', text: 'and the Spirit of God was hovering...' },
    ]
  },
};

type Screen = 'home' | 'verse' | 'settings';

export default function App() {
  // Launch screen state
  const [showLaunchScreen, setShowLaunchScreen] = useState(true);
  
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
  
  // UI state
  const [showBookSelector, setShowBookSelector] = useState(false);
  const [showChapterVerseSelector, setShowChapterVerseSelector] = useState(false);
  const [showWordAnalysis, setShowWordAnalysis] = useState(false);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

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
  const handleWordClick = (word: string) => {
    setSelectedWord(word);
    setShowWordAnalysis(true);
  };

  // Handle navigation to specific verse
  const handleNavigateToVerse = (verseRef: string) => {
    // Parse verse reference like "Gen 1:1"
    const parts = verseRef.split(' ');
    if (parts.length === 2) {
      const [chapter, verse] = parts[1].split(':');
      setCurrentChapter(parseInt(chapter));
      setCurrentVerse(parseInt(verse));
      setShowWordAnalysis(false);
    }
  };

  // Get current verse data
  const getCurrentVerseData = () => {
    const bookData = sampleVerses[currentBook as keyof typeof sampleVerses];
    if (!bookData) return null;
    
    const chapterData = bookData[currentChapter as keyof typeof bookData];
    if (!chapterData || !Array.isArray(chapterData)) return null;
    
    return chapterData[currentVerse - 1];
  };

  const currentVerseData = getCurrentVerseData();

  // Get all chapter verses
  const getChapterVerses = () => {
    const bookData = sampleVerses[currentBook as keyof typeof sampleVerses];
    if (!bookData) return [];
    
    const chapterData = bookData[currentChapter as keyof typeof bookData];
    if (!chapterData || !Array.isArray(chapterData)) return [];
    
    return chapterData;
  };

  // Show launch screen
  if (showLaunchScreen) {
    return (
      <LaunchScreen
        onComplete={() => setShowLaunchScreen(false)}
        language={language}
      />
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--background)' }}>
      {/* Main Content Area */}
      <div className={`max-w-md mx-auto px-6 ${currentScreen === 'verse' ? 'min-h-screen flex items-center' : 'pt-8 pb-32'}`}>
        {currentScreen === 'home' && (
          <HomeScreen language={language} />
        )}

        {currentScreen === 'verse' && currentVerseData && (
          <VerseDisplay
            hebrewText={currentVerseData.hebrew}
            translation={currentVerseData.translation}
            verseRef={`${currentBook} ${currentChapter}:${currentVerse}`}
            verseNumber={currentVerse}
            bookName={currentBook}
            bookNameHebrew={getHebrewBookName(currentBook)}
            book={currentBook}
            chapter={currentChapter}
            language={language}
            onBookNameClick={() => setShowBookSelector(true)}
            onChapterChange={(chapter) => {
              setCurrentChapter(chapter);
              setCurrentVerse(1);
            }}
            onVerseChange={(verse) => setCurrentVerse(verse)}
            onWordClick={handleWordClick}
            showQumran={showQumran}
            showFullChapter={showFullChapter}
            hebrewOnly={hebrewOnly}
            chapterVerses={getChapterVerses()}
            previousVerseSnippet={currentVerse > 1 ? 'Previous verse...' : undefined}
            nextVerseSnippet={currentVerse < getChapterVerses().length ? 'Next verse...' : undefined}
            onSwipeUp={() => {
              if (currentVerse > 1) {
                setCurrentVerse(currentVerse - 1);
              }
            }}
            onSwipeDown={() => {
              const chapterVerses = getChapterVerses();
              if (currentVerse < chapterVerses.length) {
                setCurrentVerse(currentVerse + 1);
              }
            }}
          />
        )}
      </div>

      {/* Bottom Navigation */}
      <BottomNavBar
        onHomeClick={() => setCurrentScreen('home')}
        onChapterVerseClick={() => setShowChapterVerseSelector(true)}
        onSettingsClick={() => setShowSettings(true)}
      />

      {/* Swipe Indicator Line - Only on Verse Screen */}
      {(currentScreen === 'verse' || currentScreen === 'home') && (
        <div className="fixed bottom-[100px] left-0 right-0 z-20 pointer-events-none">
          <div 
            className="w-full h-[1px]"
            style={{ backgroundColor: '#999999' }}
          />
        </div>
      )}

      {/* Book Selector Modal */}
      {showBookSelector && (
        <BookSelector
          currentBook={currentBook}
          onBookSelect={(book) => {
            setCurrentBook(book);
            setCurrentChapter(1);
            setCurrentVerse(1);
          }}
          onClose={() => setShowBookSelector(false)}
          language={language}
        />
      )}

      {/* Chapter & Verse Selector Bottom Sheet */}
      {showChapterVerseSelector && (
        <ChapterVerseSelector
          book={currentBook}
          currentChapter={currentChapter}
          currentVerse={currentVerse}
          onSelect={(chapter, verse) => {
            setCurrentChapter(chapter);
            setCurrentVerse(verse);
            setCurrentScreen('verse');
          }}
          onClose={() => setShowChapterVerseSelector(false)}
        />
      )}

      {/* Word Analysis Bottom Sheet */}
      {showWordAnalysis && selectedWord && wordAnalysisData[selectedWord] && (
        <BottomSheet
          isOpen={showWordAnalysis}
          onClose={() => {
            setShowWordAnalysis(false);
            setSelectedWord(null);
          }}
          title=""
        >
          <WordCard
            word={wordAnalysisData[selectedWord].word}
            transliteration={wordAnalysisData[selectedWord].transliteration}
            meanings={wordAnalysisData[selectedWord].meanings}
            root={wordAnalysisData[selectedWord].root}
            rootTransliteration={wordAnalysisData[selectedWord].rootTransliteration}
            rootMeaning={wordAnalysisData[selectedWord].rootMeaning}
            instances={wordAnalysisData[selectedWord].instances}
            onInstanceClick={handleNavigateToVerse}
          />
        </BottomSheet>
      )}

      {/* Settings Bottom Sheet */}
      {showSettings && (
        <BottomSheet
          isOpen={showSettings}
          onClose={() => setShowSettings(false)}
          title="Settings"
        >
          <SettingsScreen
            theme={theme}
            onThemeChange={setTheme}
            language={language}
            onLanguageChange={(lang) => setLanguage(lang as 'en' | 'es' | 'he')}
            showQumran={showQumran}
            onQumranChange={setShowQumran}
            showFullChapter={showFullChapter}
            onFullChapterChange={setShowFullChapter}
            hebrewOnly={hebrewOnly}
            onHebrewOnlyChange={setHebrewOnly}
          />
        </BottomSheet>
      )}
    </div>
  );
}