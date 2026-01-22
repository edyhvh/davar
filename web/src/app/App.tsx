import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { HomeScreen } from "./components/HomeScreen";
import { VerseDisplay } from "./components/VerseDisplay";
import { BottomSheet } from "./components/BottomSheet";
import { WordCard } from "./components/WordCard";
import { DesignSystemExport } from "./components/DesignSystemExport";
import { MobileDesignSystemGuide } from "./components/MobileDesignSystemGuide";
import { NavigationBar } from "./components/NavigationBar";
import { NeumorphCard } from "./components/NeumorphCard";
import { DonateScreen } from "./components/DonateScreen";
import { FeaturesScreen } from "./components/FeaturesScreen";
import {
  getBooks,
  getChapterCount,
  getChapterVerses,
  getVerseCount,
  type BookResponse,
  type VerseResponse,
  type WordResponse,
} from "./services/verseService";
import { useVerseScrollNavigation } from "./utils/useVerseScrollNavigation";
import {
  getWordAnalysisByStrong,
  type WordAnalysis,
} from "./services/lexiconService";

type Screen = "home" | "verse" | "settings" | "donate" | "features";

export default function App() {
  const getSavedReadingState = () => {
    if (typeof window === "undefined") return null;
    try {
      const raw = window.localStorage.getItem("davar.readingState");
      if (!raw) return null;
      const parsed = JSON.parse(raw) as {
        book?: string;
        chapter?: number;
        verse?: number;
        language?: "en" | "es" | "he";
        scrollNavHintCount?: number;
      };
      return parsed;
    } catch {
      return null;
    }
  };

  const getStoredLanguage = () => getSavedReadingState()?.language ?? "en";
  const getStoredBook = () => getSavedReadingState()?.book ?? "Genesis";
  const getStoredChapter = () => getSavedReadingState()?.chapter ?? 1;
  const getStoredVerse = () => getSavedReadingState()?.verse ?? 1;
  const getStoredScrollHintCount = () =>
    getSavedReadingState()?.scrollNavHintCount ?? 0;

  const [currentScreen, setCurrentScreen] = useState<Screen>("verse");
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [language, setLanguage] = useState<"en" | "es" | "he">(
    getStoredLanguage,
  );

  const [currentBook, setCurrentBook] = useState(getStoredBook);
  const [currentChapter, setCurrentChapter] = useState(getStoredChapter);
  const [currentVerse, setCurrentVerse] = useState(getStoredVerse);
  const [scrollHintCount, setScrollHintCount] = useState(
    getStoredScrollHintCount,
  );
  const [scrollJumpActive, setScrollJumpActive] = useState(false);
  const [isWordPanelHovered, setIsWordPanelHovered] = useState(false);
  const versePanelRef = useRef<HTMLDivElement | null>(null);

  const [showQumran, setShowQumran] = useState(false);
  const [showFullChapter, setShowFullChapter] = useState(false);
  const [hebrewOnly, setHebrewOnly] = useState(false);
  const [showNikud, setShowNikud] = useState(true);
  const [showCantillation, setShowCantillation] = useState(false);

  const [selectedWord, setSelectedWord] = useState<WordResponse | null>(null);
  const [lastSelectedWord, setLastSelectedWord] = useState<WordResponse | null>(
    null,
  );
  const [lastSelectedWordAnalysis, setLastSelectedWordAnalysis] =
    useState<WordAnalysis | null>(null);
  const [showMobileDesignGuide, setShowMobileDesignGuide] = useState(false);
  const [showDesignSystem, setShowDesignSystem] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  const [books, setBooks] = useState<BookResponse[]>([]);
  const [chapterVerses, setChapterVerses] = useState<VerseResponse[]>([]);
  const [chapterCount, setChapterCount] = useState(1);
  const [verseCount, setVerseCount] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedWordAnalysis, setSelectedWordAnalysis] =
    useState<WordAnalysis | null>(null);
  const [isWordAnalysisLoading, setIsWordAnalysisLoading] = useState(false);

  const getHebrewBookName = (book: string): string => {
    const found = books.find(
      (item) => item.name.toLowerCase() === book.toLowerCase(),
    );
    return found?.hebrew_name ?? book;
  };

  const getDisplayBookName = (book: string): string => {
    const found = books.find(
      (item) => item.name.toLowerCase() === book.toLowerCase(),
    );
    if (language === "es") {
      return found?.spanish_name || book;
    }
    return book;
  };

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const payload = {
      book: currentBook,
      chapter: currentChapter,
      verse: currentVerse,
      language,
      scrollNavHintCount: scrollHintCount,
    };
    window.localStorage.setItem("davar.readingState", JSON.stringify(payload));
  }, [currentBook, currentChapter, currentVerse, language, scrollHintCount]);

  const handleWordClick = (word: WordResponse) => {
    setSelectedWord(word);
  };

  const handleNavigateToVerse = (verseRef: string) => {
    const parts = verseRef.split(" ");
    if (parts.length === 2) {
      const [chapter, verse] = parts[1].split(":");
      setCurrentChapter(parseInt(chapter));
      setCurrentVerse(parseInt(verse));
      setSelectedWord(null);
    }
  };

  const currentVerseData = useMemo(
    () => chapterVerses.find((item) => item.verse === currentVerse) ?? null,
    [chapterVerses, currentVerse],
  );

  const bookOptions = useMemo(
    () =>
      [...books]
        .sort((a, b) => a.order - b.order)
        .map((book) => ({
          name: book.name,
          hebrew: book.hebrew_name,
          spanish: book.spanish_name,
        })),
    [books],
  );

  useEffect(() => {
    let isMounted = true;
    const loadBooks = async () => {
      try {
        const response = await getBooks();
        if (!isMounted) return;
        setBooks(response);
        if (response.length > 0) {
          const hasCurrent = response.some(
            (item) => item.name.toLowerCase() === currentBook.toLowerCase(),
          );
          if (!hasCurrent) {
            setCurrentBook(response[0].name);
            setCurrentChapter(1);
            setCurrentVerse(1);
          }
        }
      } catch (error) {
        if (!isMounted) return;
        setErrorMessage("Unable to load books.");
      }
    };
    loadBooks();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    const loadChapterData = async () => {
      setIsLoading(true);
      setErrorMessage(null);
      try {
        const [chapterCountValue, verseCountValue, verses] = await Promise.all([
          getChapterCount(currentBook.toLowerCase()),
          getVerseCount(currentBook.toLowerCase(), currentChapter),
          getChapterVerses(currentBook.toLowerCase(), currentChapter, {
            language: language === "he" ? undefined : language,
            showDss: showQumran,
            hebrewOnly: false, // Always load translations; UI will control display
          }),
        ]);
        if (!isMounted) return;
        setChapterCount(chapterCountValue);
        setVerseCount(verseCountValue);
        setChapterVerses(verses);
        if (verses.length > 0) {
          setCurrentVerse(Math.min(currentVerse, verses.length));
        }
      } catch (error) {
        if (!isMounted) return;
        setErrorMessage("Unable to load verses.");
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    if (currentBook) {
      loadChapterData();
    }
    return () => {
      isMounted = false;
    };
  }, [currentBook, currentChapter, language, showQumran, hebrewOnly]);

  useEffect(() => {
    let isMounted = true;
    const loadWordAnalysis = async () => {
      if (!selectedWord?.strong) {
        setSelectedWordAnalysis(null);
        setIsWordAnalysisLoading(false);
        return;
      }

      const strongPart = selectedWord.strong
        .split("/")
        .map((part) => part.trim())
        .find((part) => /^[HG]\d+$/.test(part));

      if (!strongPart) {
        setSelectedWordAnalysis(null);
        setIsWordAnalysisLoading(false);
        return;
      }

      setIsWordAnalysisLoading(true);
      try {
        const analysis = await getWordAnalysisByStrong(
          strongPart,
          language === "he" ? "en" : language,
          selectedWord.text,
        );
        if (isMounted) {
          setSelectedWordAnalysis(analysis);
          setIsWordAnalysisLoading(false);
        }
      } catch {
        if (isMounted) {
          setSelectedWordAnalysis(null);
          setIsWordAnalysisLoading(false);
        }
      }
    };
    loadWordAnalysis();
    return () => {
      isMounted = false;
    };
  }, [selectedWord, language]);

  useEffect(() => {
    if (selectedWord) {
      setLastSelectedWord(selectedWord);
    }
  }, [selectedWord]);

  useEffect(() => {
    if (selectedWord && selectedWordAnalysis) {
      setLastSelectedWordAnalysis(selectedWordAnalysis);
    }
  }, [selectedWord, selectedWordAnalysis]);

  const isSplitView = Boolean(selectedWord && !isMobile);
  const [isWordPanelVisible, setIsWordPanelVisible] = useState(false);

  useEffect(() => {
    if (selectedWord) {
      setIsWordPanelVisible(true);
      return undefined;
    }

    if (isWordPanelVisible) {
      const timeout = window.setTimeout(
        () => setIsWordPanelVisible(false),
        300,
      );
      return () => window.clearTimeout(timeout);
    }

    return undefined;
  }, [selectedWord, isWordPanelVisible]);

  useEffect(() => {
    const timeout = window.setTimeout(() => setSelectedWord(null), 50);
    return () => window.clearTimeout(timeout);
  }, [currentBook, currentChapter, currentVerse]);

  useEffect(() => {
    const media = window.matchMedia("(max-width: 767px)");
    const update = () => setIsMobile(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (!selectedWord || isMobile) {
      setIsWordPanelHovered(false);
    }
  }, [isMobile, selectedWord]);

  useEffect(() => {
    if (!scrollJumpActive) return undefined;
    const timeout = window.setTimeout(() => setScrollJumpActive(false), 240);
    return () => window.clearTimeout(timeout);
  }, [scrollJumpActive]);

  const triggerScrollJump = useCallback(() => {
    setScrollHintCount((previous) => {
      if (previous >= 5) return previous;
      setScrollJumpActive(true);
      return previous + 1;
    });
  }, []);

  const handlePreviousVerse = useCallback(async () => {
    if (currentVerse > 1) {
      setCurrentVerse(currentVerse - 1);
      return true;
    }

    if (currentChapter > 1) {
      try {
        const previousChapter = currentChapter - 1;
        const previousVerseCount = await getVerseCount(
          currentBook.toLowerCase(),
          previousChapter,
        );
        setCurrentChapter(previousChapter);
        setCurrentVerse(previousVerseCount);
        return true;
      } catch {
        return false;
      }
    }
    return false;
  }, [currentBook, currentChapter, currentVerse]);

  const handleNextVerse = useCallback(async () => {
    if (currentVerse < verseCount) {
      setCurrentVerse(currentVerse + 1);
      return true;
    }

    if (currentChapter < chapterCount) {
      setCurrentChapter(currentChapter + 1);
      setCurrentVerse(1);
      return true;
    }
    return false;
  }, [chapterCount, currentChapter, currentVerse, verseCount]);

  const isScrollNavigationActive =
    currentScreen === "verse" && !showFullChapter && !isMobile;

  useVerseScrollNavigation({
    containerRef: versePanelRef,
    isEnabled: isScrollNavigationActive,
    isBlocked: isWordPanelHovered,
    threshold: 36,
    cooldownMs: 500,
    onNavigateNext: handleNextVerse,
    onNavigatePrevious: handlePreviousVerse,
    onNavigateFeedback: triggerScrollJump,
  });

  const activeWordAnalysis = selectedWord
    ? selectedWordAnalysis
    : lastSelectedWordAnalysis;

  const wordMeanings =
    activeWordAnalysis?.definitions?.map((item) => item.text) ?? [];

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: "var(--background)",
        height: isScrollNavigationActive ? "100vh" : undefined,
        overflow: isScrollNavigationActive ? "hidden" : undefined,
      }}
    >
      <div className="sticky top-0 z-40 px-6 pt-6">
        <div className="max-w-7xl mx-auto">
          <NavigationBar
            book={currentBook}
            bookDisplayName={getDisplayBookName(currentBook)}
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
              setCurrentScreen("verse");
            }}
            onChapterChange={(chapter) => {
              setCurrentChapter(chapter);
              setCurrentVerse(1);
            }}
            onVerseChange={(verse) => setCurrentVerse(verse)}
            onHomeClick={() => setCurrentScreen("home")}
            onDonateClick={() => setCurrentScreen("donate")}
            onFeaturesClick={() => setCurrentScreen("features")}
            onPreviousVerse={() => {
              if (currentVerse > 1) {
                setCurrentVerse(currentVerse - 1);
              }
            }}
            onNextVerse={() => {
              if (currentVerse < verseCount) {
                setCurrentVerse(currentVerse + 1);
              }
            }}
            hasPreviousVerse={currentVerse > 1}
            hasNextVerse={currentVerse < verseCount}
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

      <div className="px-6 pb-32 pt-6">
        <div className="max-w-7xl mx-auto">
          {currentScreen === "home" && <HomeScreen language={language} />}
          {currentScreen === "donate" && <DonateScreen />}
          {currentScreen === "features" && <FeaturesScreen />}

          {currentScreen === "verse" && (
            <div className="grid gap-6 items-start md:grid-cols-[7fr_3fr]">
              <div
                ref={versePanelRef}
                className={`min-h-[70vh] ${showFullChapter ? "" : "flex items-center justify-center"} w-full max-w-3xl md:max-w-4xl justify-self-center verse-panel-shell ${
                  isSplitView
                    ? "verse-panel-split md:col-span-1"
                    : "verse-panel-centered md:col-span-2"
                } ${scrollJumpActive ? "verse-panel-jump" : ""}`}
                style={showFullChapter ? undefined : { height: "70vh" }}
              >
                <div className="verse-panel-inner">
                  {currentVerseData ? (
                    <VerseDisplay
                      hebrewText={currentVerseData.hebrew}
                      translation={currentVerseData.translation ?? ""}
                      verseRef={`${currentBook} ${currentChapter}:${currentVerse}`}
                      verseNumber={currentVerse}
                      bookName={getDisplayBookName(currentBook)}
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
                      previousVerseSnippet={
                        currentVerse > 1 ? "Previous verse..." : undefined
                      }
                      nextVerseSnippet={
                        currentVerse < chapterVerses.length
                          ? "Next verse..."
                          : undefined
                      }
                      onSwipeUp={() => {
                        void handlePreviousVerse();
                      }}
                      onSwipeDown={() => {
                        void handleNextVerse();
                      }}
                    />
                  ) : (
                    <NeumorphCard>
                      <p className="text-sm text-gray-500">
                        Select a book to begin.
                      </p>
                    </NeumorphCard>
                  )}

                  {isLoading && (
                    <NeumorphCard className="mt-6">
                      <p className="text-sm text-gray-500">Loading verses...</p>
                    </NeumorphCard>
                  )}
                  {errorMessage && (
                    <NeumorphCard className="mt-6">
                      <p className="text-sm text-red-500">{errorMessage}</p>
                    </NeumorphCard>
                  )}
                </div>
              </div>

              <div
                className="hidden md:block"
                style={showFullChapter ? undefined : { height: "70vh" }}
              >
                {(() => {
                  const wordForCard = selectedWord ?? lastSelectedWord;
                  const wordAnalysisForCard = selectedWord
                    ? selectedWordAnalysis
                    : lastSelectedWordAnalysis;

                  return (
                <NeumorphCard
                  className={`p-6 sticky top-24 word-panel-shell ${
                    selectedWord ? "word-panel-open" : "word-panel-closed"
                  }`}
                  style={!selectedWord ? { pointerEvents: "none" } : undefined}
                  onMouseEnter={() => setIsWordPanelHovered(true)}
                  onMouseLeave={() => setIsWordPanelHovered(false)}
                >
                  {wordForCard && isWordPanelVisible ? (
                    <WordCard
                      word={wordAnalysisForCard?.hebrew ?? wordForCard.text}
                      wordFromVerse={wordForCard.text}
                      transliteration={wordAnalysisForCard?.transliteration}
                      meanings={wordMeanings}
                      root={wordAnalysisForCard?.root}
                      rootTransliteration={wordAnalysisForCard?.root_strong}
                      rootMeaning={
                        wordAnalysisForCard?.root_definitions?.[0]?.text
                      }
                      prefixes={wordForCard.prefixes}
                      language={language}
                      showNikud={showNikud}
                      instances={(wordAnalysisForCard?.instances ?? []).map(
                        (instance) =>
                          typeof instance === "string"
                            ? { verse: instance, text: "" }
                            : instance,
                      )}
                      onInstanceClick={handleNavigateToVerse}
                      onClose={() => setSelectedWord(null)}
                      isLoading={Boolean(selectedWord && isWordAnalysisLoading)}
                    />
                  ) : (
                    <div
                      className="text-sm text-[var(--text-secondary)]"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      Select a word
                    </div>
                  )}
                </NeumorphCard>
                  );
                })()}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="md:hidden">
        <div className="h-10" />
      </div>

      {isMobile && selectedWord && (
        <BottomSheet
          isOpen={!!selectedWord}
          onClose={() => setSelectedWord(null)}
          title=""
        >
          <WordCard
            word={selectedWordAnalysis?.hebrew ?? selectedWord.text}
            wordFromVerse={selectedWord.text}
            transliteration={selectedWordAnalysis?.transliteration}
            meanings={wordMeanings}
            root={selectedWordAnalysis?.root}
            rootTransliteration={selectedWordAnalysis?.root_strong}
            rootMeaning={selectedWordAnalysis?.root_definitions?.[0]?.text}
            prefixes={selectedWord.prefixes}
            language={language}
            showNikud={showNikud}
            instances={(selectedWordAnalysis?.instances ?? []).map(
              (instance) =>
                typeof instance === "string"
                  ? { verse: instance, text: "" }
                  : instance,
            )}
            onInstanceClick={handleNavigateToVerse}
            onClose={() => setSelectedWord(null)}
            isLoading={!selectedWordAnalysis}
          />
        </BottomSheet>
      )}

      {showDesignSystem && (
        <div className="fixed inset-0 z-50 overflow-auto">
          <DesignSystemExport
            theme={theme}
            onThemeChange={setTheme}
            onClose={() => setShowDesignSystem(false)}
          />
        </div>
      )}

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
