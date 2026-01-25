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
import { Skeleton } from "./components/ui/skeleton";
import { DonateScreen } from "./components/DonateScreen";
import { FeaturesScreen } from "./components/FeaturesScreen";
import {
  getBooks,
  getChapterCount,
  getChapterVerses,
  getVerseCount,
  lookupBook,
  type BookResponse,
  type VerseResponse,
  type WordResponse,
} from "./services/verseService";
import { useVerseScrollNavigation } from "./utils/useVerseScrollNavigation";
import { stripCantillation, stripMeteg } from "./utils/hebrew";
import {
  getWordAnalysisByStrong,
  type WordAnalysis,
} from "./services/lexiconService";
import { usePersistedState, usePersistedBookPosition } from "./hooks/usePersistedState";
import { getStoredReadingState, getLastPositionForBook, updateLastPositionForBook, createDefaultReadingState, saveReadingState } from "./utils/storageHelpers";
import type { ReadingStateV2 } from "./utils/storageHelpers";
import { useTranslation } from "./hooks/useTranslation";
import { useDocumentTitle } from "./hooks/useDocumentTitle";

type Screen = "home" | "verse" | "settings" | "donate" | "features";

type RouteState = {
  screen: Screen;
  book?: string;
  chapter?: number;
  verse?: number;
};

const BOOK_ABBREVIATIONS: Record<string, string> = {
  gen: "Genesis",
  exod: "Exodus",
  ex: "Exodus",
  lev: "Leviticus",
  num: "Numbers",
  deut: "Deuteronomy",
  josh: "Joshua",
  judg: "Judges",
  ruth: "Ruth",
  "1sam": "Samuel1",
  "2sam": "Samuel2",
  "1kgs": "Kings1",
  "2kgs": "Kings2",
  "1chr": "Chronicles1",
  "2chr": "Chronicles2",
  ezra: "Ezra",
  neh: "Nehemiah",
  esth: "Esther",
  job: "Job",
  ps: "Psalms",
  prov: "Proverbs",
  eccl: "Ecclesiastes",
  song: "SongOfSolomon",
  isa: "Isaiah",
  jer: "Jeremiah",
  ezek: "Ezekiel",
  dan: "Daniel",
  hos: "Hosea",
  joel: "Joel",
  amos: "Amos",
  obad: "Obadiah",
  jonah: "Jonah",
  mic: "Micah",
  nah: "Nahum",
  hab: "Habakkuk",
  zeph: "Zephaniah",
  hag: "Haggai",
  zech: "Zechariah",
  mal: "Malachi",
  matt: "Matthew",
  mark: "Mark",
  luke: "Luke",
  john: "John",
  acts: "Acts",
  rom: "Romans",
  "1cor": "Corinthians1",
  "2cor": "Corinthians2",
  gal: "Galatians",
  eph: "Ephesians",
  phil: "Philippians",
  col: "Colossians",
  "1thess": "Thessalonians1",
  "2thess": "Thessalonians2",
  "1tim": "Timothy1",
  "2tim": "Timothy2",
  tit: "Titus",
  phlm: "Philemon",
  phlm2: "Philemon",
  heb: "Hebrews",
  jas: "James",
  "1pet": "Peter1",
  "2pet": "Peter2",
  "1john": "John1",
  "2john": "John2",
  "3john": "John3",
  jude: "Jude",
  rev: "Revelation",
};

export default function App() {
  // Initialize persisted state from localStorage or defaults
  const initialState = getStoredReadingState() ?? createDefaultReadingState();

  // Use persisted state hooks for all settings
  const [currentScreen, setCurrentScreen] = useState<Screen>("verse");
  const [theme, setTheme] = usePersistedState("theme", initialState.theme);
  const [language, setLanguage] = usePersistedState(
    "language",
    initialState.language,
  );
  const { t, isRTL } = useTranslation(language);
  const [showQumran, setShowQumran] = usePersistedState(
    "showQumran",
    initialState.showQumran,
  );
  const [showFullChapter, setShowFullChapter] = usePersistedState(
    "showFullChapter",
    initialState.showFullChapter,
  );
  const [hebrewOnly, setHebrewOnly] = usePersistedState(
    "hebrewOnly",
    initialState.hebrewOnly,
  );
  const [showNikud, setShowNikud] = usePersistedState(
    "showNikud",
    initialState.showNikud,
  );
  const [showCantillation, setShowCantillation] = usePersistedState(
    "showCantillation",
    initialState.showCantillation,
  );
  const [scrollHintCount, setScrollHintCount] = usePersistedState(
    "scrollNavHintCount",
    initialState.scrollNavHintCount,
  );

  // Navigation state - also persisted but with special logic for per-book tracking
  const [currentBook, setCurrentBook] = useState(initialState.book);
  const [currentChapter, setCurrentChapter] = useState(
    initialState.chapter,
  );
  const [currentVerse, setCurrentVerse] = useState(initialState.verse);
  const prevBookRef = useRef(currentBook);

  // Non-persisted UI state
  const [scrollJumpActive, setScrollJumpActive] = useState(false);
  const [isWordPanelHovered, setIsWordPanelHovered] = useState(false);
  const versePanelRef = useRef<HTMLDivElement | null>(null);

  const [selectedWord, setSelectedWord] = useState<WordResponse | null>(null);
  const [isWordPanelDismissed, setIsWordPanelDismissed] = useState(true);
  const [showWordHint, setShowWordHint] = useState(true);
  const [isNavigatingWordPanel, setIsNavigatingWordPanel] = useState(false);
  const [showWordSkeleton, setShowWordSkeleton] = useState(false);
  const navigationKeyRef = useRef<string | null>(null);
  const wordSkeletonTimerRef = useRef<number | null>(null);
  const wordPanelDismissedRef = useRef(true);
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
  const lastUrlRef = useRef<string | null>(null);
  const pendingRouteRef = useRef<RouteState | null>(null);
  const isHandlingPopStateRef = useRef(false);
  const preserveWordRef = useRef(false);
  const pendingWordTextRef = useRef<string | null>(null);
  const pendingWordStrongRef = useRef<string | null>(null);
  const pendingWordRef = useRef<WordResponse | null>(null);
  const [wordCardTabKey, setWordCardTabKey] = useState(0);

  const buildRoutePath = useCallback(
    (route: RouteState) => {
      switch (route.screen) {
        case "home":
          return "/home";
        case "donate":
          return "/donate";
        case "features":
          return "/features";
        case "settings":
          return "/settings";
        case "verse": {
          const book = route.book ? encodeURIComponent(route.book) : "";
          const chapter = route.chapter ?? 1;
          const verse = route.verse ?? 1;
          return book ? `/verse/${book}/${chapter}/${verse}` : "/";
        }
        default:
          return "/";
      }
    },
    [],
  );

  const parseRoutePath = useCallback((pathname: string): RouteState => {
    const trimmed = pathname.replace(/\/+$/, "") || "/";
    const parts = trimmed.split("/").filter(Boolean);

    if (parts.length === 0) {
      return { screen: "verse" };
    }

    const [root, book, chapter, verse] = parts;
    if (root === "home") return { screen: "home" };
    if (root === "donate") return { screen: "donate" };
    if (root === "features") return { screen: "features" };
    if (root === "settings") return { screen: "settings" };

    if (root === "verse") {
      const decodedBook = book ? decodeURIComponent(book) : undefined;
      const parsedChapter = chapter ? Number.parseInt(chapter, 10) : undefined;
      const parsedVerse = verse ? Number.parseInt(verse, 10) : undefined;
      return {
        screen: "verse",
        book: decodedBook,
        chapter: Number.isNaN(parsedChapter) ? undefined : parsedChapter,
        verse: Number.isNaN(parsedVerse) ? undefined : parsedVerse,
      };
    }

    return { screen: "verse" };
  }, []);

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

  const tabTitle = useMemo(() => {
    if (currentScreen !== "verse" || !currentBook || !currentChapter) {
      return "Davar";
    }

    if (language === "he") {
      return `${getHebrewBookName(currentBook)} ${currentChapter}`;
    }

    const displayBookName = getDisplayBookName(currentBook);
    const hebrewBookName = getHebrewBookName(currentBook);

    return `${displayBookName} ${hebrewBookName} ${currentChapter}`;
  }, [currentBook, currentChapter, currentScreen, language, books]);

  useDocumentTitle(tabTitle);

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    pendingRouteRef.current = parseRoutePath(window.location.pathname);
  }, [parseRoutePath]);

  useEffect(() => {
    document.documentElement.dir = isRTL ? "rtl" : "ltr";
    document.documentElement.lang = language;
  }, [isRTL, language]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    // Save navigation state and per-book position to localStorage
    const stored = getStoredReadingState();
    if (stored) {
      let updated = { ...stored, book: currentBook, chapter: currentChapter, verse: currentVerse };
      updated = updateLastPositionForBook(updated, currentBook, currentChapter, currentVerse);
      saveReadingState(updated);
    }
  }, [currentBook, currentChapter, currentVerse]);

  // Clear selected word and chapter verses when book changes to prevent showing stale data
  useEffect(() => {
    if (prevBookRef.current !== currentBook) {
      setSelectedWord(null);
      setSelectedWordAnalysis(null);
      setChapterVerses([]); // Clear old verses so currentVerseData becomes null
      prevBookRef.current = currentBook;
    }
  }, [currentBook]);

  const handleWordClick = (word: WordResponse) => {
    setIsWordPanelDismissed(false);
    setShowWordHint(false);
    setSelectedWord(word);
  };

  const handleNavigateToVerse = async (verseRef: string) => {
    const wordToPreserve = selectedWord ?? lastSelectedWord;
    if (wordToPreserve) {
      preserveWordRef.current = true;
      pendingWordTextRef.current = wordToPreserve.text;
      pendingWordStrongRef.current = wordToPreserve.strong ?? null;
      pendingWordRef.current = wordToPreserve;
      setIsWordPanelDismissed(false);
      setWordCardTabKey((previous) => previous + 1);
    }
    const cleanedRef = verseRef.replace(/\s+/g, " ").trim();
    const lastSpaceIndex = cleanedRef.lastIndexOf(" ");
    if (lastSpaceIndex <= 0) return;

    const bookLabel = cleanedRef.slice(0, lastSpaceIndex).trim();
    const chapterVerse = cleanedRef.slice(lastSpaceIndex + 1).trim();
    const match = chapterVerse.match(/^(\d+):(\d+)$/);
    if (!match) return;

    const chapter = Number.parseInt(match[1], 10);
    const verse = Number.parseInt(match[2], 10);
    if (Number.isNaN(chapter) || Number.isNaN(verse)) return;

    const normalizedBookLabel = bookLabel.toLowerCase().replace(/\./g, "");
    const abbreviationMatch = BOOK_ABBREVIATIONS[normalizedBookLabel];

    const matchedBook = books.find((item) => {
      const label = normalizedBookLabel;
      return (
        item.name.toLowerCase() === label ||
        item.hebrew_name?.toLowerCase() === label ||
        item.spanish_name?.toLowerCase() === label
      );
    });

    let resolvedBookName =
      matchedBook?.name ?? abbreviationMatch ?? bookLabel;
    if (!matchedBook && !abbreviationMatch) {
      try {
        const resolved = await lookupBook(bookLabel);
        resolvedBookName = resolved.name;
      } catch (error) {
        console.error("Failed to normalize book label:", error);
      }
    }

    setCurrentBook(resolvedBookName);
    setCurrentChapter(chapter);
    setCurrentVerse(verse);
    if (isMobile) {
      setSelectedWord(null);
    } else {
      setIsWordPanelDismissed(false);
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
        setErrorMessage(t("errors.loadBooks"));
      }
    };
    loadBooks();
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const pending = pendingRouteRef.current;
    if (!pending) return;

    if (pending.screen !== "verse") {
      setCurrentScreen(pending.screen);
      pendingRouteRef.current = null;
      return;
    }

    if (pending.book) {
      const matchedBook = books.find(
        (item) => item.name.toLowerCase() === pending.book?.toLowerCase(),
      );
      if (matchedBook) {
        setCurrentBook(matchedBook.name);
      } else {
        setCurrentBook(pending.book);
      }
    }

    if (pending.chapter) {
      setCurrentChapter(pending.chapter);
    }

    if (pending.verse) {
      setCurrentVerse(pending.verse);
    }

    setCurrentScreen("verse");
    pendingRouteRef.current = null;
  }, [books]);

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
        setErrorMessage(t("errors.loadVerses"));
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
    if (typeof window === "undefined") return;
    const handlePopState = () => {
      isHandlingPopStateRef.current = true;
      const route = parseRoutePath(window.location.pathname);
      if (route.screen !== "verse") {
        setCurrentScreen(route.screen);
      } else {
        if (route.book) {
          const matchedBook = books.find(
            (item) => item.name.toLowerCase() === route.book?.toLowerCase(),
          );
          if (matchedBook) {
            setCurrentBook(matchedBook.name);
          } else {
            setCurrentBook(route.book);
          }
        }
        if (route.chapter) {
          setCurrentChapter(route.chapter);
        }
        if (route.verse) {
          setCurrentVerse(route.verse);
        }
        setCurrentScreen("verse");
      }
      window.setTimeout(() => {
        isHandlingPopStateRef.current = false;
      }, 0);
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, [books, parseRoutePath]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (isHandlingPopStateRef.current) return;

    const path = buildRoutePath({
      screen: currentScreen,
      book: currentBook,
      chapter: currentChapter,
      verse: currentVerse,
    });

    if (lastUrlRef.current === path) return;
    window.history.pushState(null, "", path);
    lastUrlRef.current = path;
  }, [buildRoutePath, currentBook, currentChapter, currentScreen, currentVerse]);

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

  const isSplitView = Boolean(!isMobile && (selectedWord || isNavigatingWordPanel));
  const [isWordPanelVisible, setIsWordPanelVisible] = useState(false);
  const isWordPanelActive =
    !isMobile && !isWordPanelDismissed && (selectedWord || isNavigatingWordPanel);
  const shouldShowWordSkeleton =
    isWordPanelActive && isNavigatingWordPanel && showWordSkeleton && !selectedWord;

  useEffect(() => {
    if (isWordPanelActive) {
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
  }, [isWordPanelActive, isWordPanelVisible]);

  useEffect(() => {
    wordPanelDismissedRef.current = isWordPanelDismissed;
  }, [isWordPanelDismissed]);

  useEffect(() => {
    if (wordSkeletonTimerRef.current) {
      window.clearTimeout(wordSkeletonTimerRef.current);
      wordSkeletonTimerRef.current = null;
    }
    setShowWordSkeleton(false);

    if (isMobile) {
      setIsNavigatingWordPanel(false);
      return;
    }

    const navigationKey = `${currentBook}-${currentChapter}-${currentVerse}`;
    if (navigationKeyRef.current === navigationKey) return;
    navigationKeyRef.current = navigationKey;

    if (preserveWordRef.current) {
      setIsNavigatingWordPanel(false);
      setIsWordPanelDismissed(false);
      return;
    }

    setIsNavigatingWordPanel(false);
    setIsWordPanelDismissed(true);
    setSelectedWord(null);
  }, [currentBook, currentChapter, currentVerse, isMobile]);

  useEffect(() => {
    if (!currentVerseData || !preserveWordRef.current) return;

    const targetText = pendingWordTextRef.current;
    const targetStrong = pendingWordStrongRef.current;
    const fallbackWord = pendingWordRef.current;

    const normalize = (text: string) =>
      stripMeteg(stripCantillation(text)).replace(/\//g, "");

    let matchedWord: WordResponse | undefined;

    if (targetStrong) {
      matchedWord = currentVerseData.words?.find(
        (word) => word.strong === targetStrong,
      );
    }

    if (!matchedWord && targetText) {
      const normalizedTarget = normalize(targetText);
      matchedWord = currentVerseData.words?.find(
        (word) => normalize(word.text) === normalizedTarget,
      );
    }

    if (matchedWord) {
      setSelectedWord(matchedWord);
      setIsWordPanelDismissed(false);
    } else if (fallbackWord) {
      setSelectedWord(fallbackWord);
      setIsWordPanelDismissed(false);
    }

    preserveWordRef.current = false;
    pendingWordTextRef.current = null;
    pendingWordStrongRef.current = null;
    pendingWordRef.current = null;
  }, [currentVerseData]);

  useEffect(() => {
    if (!selectedWord) return;
    setIsNavigatingWordPanel(false);
    setShowWordSkeleton(false);
    if (wordSkeletonTimerRef.current) {
      window.clearTimeout(wordSkeletonTimerRef.current);
      wordSkeletonTimerRef.current = null;
    }
  }, [selectedWord]);

  useEffect(() => {
    return () => {
      if (wordSkeletonTimerRef.current) {
        window.clearTimeout(wordSkeletonTimerRef.current);
        wordSkeletonTimerRef.current = null;
      }
    };
  }, []);

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

  const activeWordAnalysis = selectedWordAnalysis ?? lastSelectedWordAnalysis;

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
        <div className="mx-auto flex justify-center">
          <NavigationBar
            book={currentBook}
            bookDisplayName={getDisplayBookName(currentBook)}
            bookHebrew={getHebrewBookName(currentBook)}
            chapter={currentChapter}
            verse={currentVerse}
            books={bookOptions}
            chapterCount={chapterCount}
            verseCount={verseCount}
            onBookChange={(selectedBook) => {
              if (selectedBook === currentBook) {
                // Same book - retrieve last position for this book
                const stored = getStoredReadingState();
                if (stored) {
                  const position = getLastPositionForBook(stored, selectedBook);
                  setCurrentChapter(position.chapter);
                  setCurrentVerse(position.verse);
                }
              } else {
                // Different book - reset to 1:1
                setCurrentBook(selectedBook);
                setCurrentChapter(1);
                setCurrentVerse(1);
              }
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
          {currentScreen === "donate" && <DonateScreen language={language} />}
          {currentScreen === "features" && (
            <FeaturesScreen language={language} />
          )}

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
                      showOnboardingHint={showWordHint}
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
                        currentVerse > 1
                          ? t("verse.previousSnippet")
                          : undefined
                      }
                      nextVerseSnippet={
                        currentVerse < chapterVerses.length
                          ? t("verse.nextSnippet")
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
                        {t("verse.selectBookPrompt")}
                      </p>
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
                  const wordForCard =
                    selectedWord ??
                    (!isNavigatingWordPanel && !showWordSkeleton
                      ? lastSelectedWord
                      : null);
                  const wordAnalysisForCard = selectedWord
                    ? selectedWordAnalysis
                    : lastSelectedWordAnalysis;

                  return (
                <NeumorphCard
                  className={`p-6 sticky top-24 word-panel-shell ${
                    isWordPanelActive ? "word-panel-open" : "word-panel-closed"
                  }`}
                  style={!isWordPanelActive ? { pointerEvents: "none" } : undefined}
                  onMouseEnter={() => setIsWordPanelHovered(true)}
                  onMouseLeave={() => setIsWordPanelHovered(false)}
                >
                  {shouldShowWordSkeleton ? (
                    <div className="space-y-5">
                      <div className="flex justify-end">
                        <Skeleton className="h-9 w-9 rounded-full" />
                      </div>
                      <Skeleton className="h-16 w-40 mx-auto" />
                      <Skeleton className="h-3 w-32 mx-auto" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-4/5" />
                      <Skeleton className="h-4 w-3/4" />
                    </div>
                  ) : wordForCard && isWordPanelVisible ? (
                    <WordCard
                      word={wordAnalysisForCard?.hebrew ?? wordForCard.text}
                      wordFromVerse={wordForCard.text}
                      strongNumber={wordAnalysisForCard?.strong_number}
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
                      tabResetKey={wordCardTabKey}
                      onClose={() => {
                        if (!isMobile) {
                          setIsWordPanelDismissed(true);
                        }
                        setSelectedWord(null);
                        setIsNavigatingWordPanel(false);
                        setShowWordSkeleton(false);
                        if (wordSkeletonTimerRef.current) {
                          window.clearTimeout(wordSkeletonTimerRef.current);
                          wordSkeletonTimerRef.current = null;
                        }
                      }}
                      isLoading={Boolean(selectedWord && isWordAnalysisLoading)}
                    />
                  ) : isNavigatingWordPanel ? (
                    <div className="h-40" />
                  ) : (
                    <div
                      className="text-sm text-[var(--text-secondary)]"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {t("wordCard.selectWord")}
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
            strongNumber={selectedWordAnalysis?.strong_number}
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
            tabResetKey={wordCardTabKey}
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
                {t("navigation.backToApp")}
              </button>
              <MobileDesignSystemGuide />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
