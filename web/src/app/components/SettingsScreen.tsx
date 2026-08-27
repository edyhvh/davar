import React, { type ReactNode } from "react";
import {
	SHARED_SETTINGS_ORDER,
	canUseSeferStyle,
	isSeferStyleVisible,
	type SharedSettingId,
} from "@davar/shared/settingsOrder";
import { useTranslation } from "../hooks/useTranslation";

interface SettingsScreenProps {
	theme: "light" | "dark";
	onThemeChange: (theme: "light" | "dark") => void;
	language: "en" | "es" | "he";
	onLanguageChange: (language: "en" | "es" | "he") => void;
	besorahTextVersion: "delitzsch" | "hutter";
	onBesorahTextVersionChange: (version: "delitzsch" | "hutter") => void;
	showQumran: boolean;
	onQumranChange: (show: boolean) => void;
	showFullChapter: boolean;
	onFullChapterChange: (show: boolean) => void;
	seferMode: boolean;
	onSeferModeChange: (show: boolean) => void;
	hebrewOnly: boolean;
	onHebrewOnlyChange: (show: boolean) => void;
	translationOnly?: boolean;
	onDesignSystemClick?: () => void;
	onMobileDesignGuideClick?: () => void;
}
