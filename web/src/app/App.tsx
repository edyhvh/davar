import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { BottomSheet } from "./components/BottomSheet";
import { ConnectionErrorPage } from "./components/ConnectionErrorPage";
import { DesignSystemExport } from "./components/DesignSystemExport";
import { DonateScreen } from "./components/DonateScreen";
import { FeaturesScreen } from "./components/FeaturesScreen";
import { FeedbackScreen } from "./components/FeedbackScreen";
import { HomeScreen } from "./components/HomeScreen";
import { LegalScreen } from "./components/LegalScreen";
import { MobileDesignSystemGuide } from "./components/MobileDesignSystemGuide";
import { NavigationBar } from "./components/NavigationBar";
import { NeumorphCard } from "./components/NeumorphCard";
import { NotFoundPage } from "./components/NotFoundPage";
import { SettingsScreen } from "./components/SettingsScreen";
import { Skeleton } from "./components/ui/skeleton";
import { TthSection } from "./components/TthSection";
import { VerseDisplay } from "./components/VerseDisplay";
import { WordCard } from "./components/WordCard";
import { useDocumentTitle } from "./hooks/useDocumentTitle";
import { usePersistedState } from "./hooks/usePersistedState";
import { translate, useTranslation } from "./hooks/useTranslation";
import {
	type BookResponse,
	getBooks,
	getChapterCount,
	getChapterVerses,
	getVerseCount,
	loadLexiconEntry,
	lookupBook,
	type VerseResponse,
	type WordAnalysis,
	type WordResponse,
} from "./services/staticData";
import { formatBookDisplayName } from "./utils/bookNameFormatter";
import { stripCantillation, stripMeteg } from "./utils/hebrew";
import {
	createDefaultReadingState,
	getLastPositionForBook,
	getStoredReadingState,
	saveReadingState,
	updateLastPositionForBook,
} from "./utils/storageHelpers";
import {
	getDssCommentaryForLanguage,
	HUTTER_ANNOUNCEMENT_RELEASE,
	TTH_BOOK_MAPPING,
} from "./utils/translationConfig";
import { useVerseScrollNavigation } from "./utils/useVerseScrollNavigation";

type Screen =
	| "home"
	| "verse"
	| "settings"
	| "donate"
	| "features"
	| "terms"
	| "privacy"
	| "feedback"
	| "tth"
	| "notFound"
	| "connectionError";
