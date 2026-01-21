import React, { useEffect, useMemo, useState } from "react";
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
import {
  getWordAnalysisByStrong,
  type WordAnalysis,
} from "./services/lexiconService";

type Screen = "home" | "verse" | "settings" | "donate" | "features";

export default function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>("verse");
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [language, setLanguage] = useState<"en" | "es" | "he">("en");

  const [currentBook, setCurrentBook] = useState("Genesis");
  const [currentChapter, setCurrentChapter] = useState(1);
  const [currentVerse, setCurrentVerse] = useState(1);

  const [showQumran, setShowQumran] = useState(false);
  const [showFullChapter, setShowFullChapter] = useState(false);
  const [hebrewOnly, setHebrewOnly] = useState(false);
  const [showNikud, setShowNikud] = useState(true);
  const [showCantillation, setShowCantillation] = useState(false);

  const [selectedWord, setSelectedWord] = useState<WordResponse | null>(null);
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

  const getHebrewBookName = (book: string): string => {
    const found = books.find(
      (item) => item.name.toLowerCase() === book.toLowerCase(),
    );
    return found?.hebrew_name ?? book;
  };

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

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
    () => books.map((book) => ({ name: book.name, hebrew: book.hebrew_name })),
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
          setCurrentBook(response[0].name);
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
            hebrewOnly,
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
        return;
      }
      try {
        const analysis = await getWordAnalysisByStrong(selectedWord.strong, language === 'he' ? 'en' : language);
        if (isMounted) setSelectedWordAnalysis(analysis);
      } catch {
        if (isMounted) setSelectedWordAnalysis(null);
      }
    };
    loadWordAnalysis();
    return () => {
      isMounted = false;
    };
  }, [selectedWord, language]);

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
        220,
      );
      return () => window.clearTimeout(timeout);
    }

    return undefined;
  }, [selectedWord, isWordPanelVisible]);

  useEffect(() => {
    setSelectedWord(null);
  }, [currentBook, currentChapter, currentVerse]);

  useEffect(() => {
    const media = window.matchMedia("(max-width: 767px)");
    const update = () => setIsMobile(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);

  const wordMeanings =
    selectedWordAnalysis?.definitions?.map((item) => item.text) ?? [];

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: "var(--background)" }}
    >
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
                className={`min-h-[70vh] ${showFullChapter ? "" : "flex items-center justify-center"} w-full max-w-3xl md:max-w-4xl justify-self-center verse-panel-shell ${
                  isSplitView ? "verse-panel-split md:col-span-1" : "verse-panel-centered md:col-span-2"
                }`}
                style={showFullChapter ? undefined : { height: "70vh" }}
              >
                {currentVerseData ? (
                  <VerseDisplay
                    hebrewText={currentVerseData.hebrew}
                    translation={currentVerseData.translation ?? ""}
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
                    previousVerseSnippet={
                      currentVerse > 1 ? "Previous verse..." : undefined
                    }
                    nextVerseSnippet={
                      currentVerse < chapterVerses.length
                        ? "Next verse..."
                        : undefined
                    }
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

              <div className="hidden md:block" style={showFullChapter ? undefined : { height: "70vh" }}>
                <NeumorphCard
                  className={`p-6 sticky top-24 word-panel-shell ${
                    selectedWord ? "word-panel-open" : "word-panel-closed"
                  }`}
                  style={!selectedWord ? { pointerEvents: "none" } : undefined}
                >
                  {selectedWord ? (
                    <WordCard
                      word={selectedWordAnalysis?.hebrew ?? selectedWord.text}
                      transliteration={selectedWordAnalysis?.transliteration}
                      meanings={wordMeanings}
                      root={selectedWordAnalysis?.root}
                      rootTransliteration={selectedWordAnalysis?.root_strong}
                      rootMeaning={
                        selectedWordAnalysis?.root_definitions?.[0]?.text
                      }
                      instances={(selectedWordAnalysis?.instances ?? []).map((instance) =>
                        typeof instance === "string"
                          ? { verse: instance, text: "" }
                          : instance,
                      )}
                      onInstanceClick={handleNavigateToVerse}
                      onClose={() => setSelectedWord(null)}
                      isLoading={!selectedWordAnalysis}
                    />
                  ) : (
                    <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      Select a word
                    </div>
                  )}
                </NeumorphCard>
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
            transliteration={selectedWordAnalysis?.transliteration}
            meanings={wordMeanings}
            root={selectedWordAnalysis?.root}
            rootTransliteration={selectedWordAnalysis?.root_strong}
            rootMeaning={selectedWordAnalysis?.root_definitions?.[0]?.text}
            instances={(selectedWordAnalysis?.instances ?? []).map((instance) =>
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
