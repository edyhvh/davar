/**
 * Canonical cross-platform settings order (#107).
 *
 * Single source of truth for the sequence of settings options that are
 * shared between web and mobile. Platform-specific options live in
 * clearly separated platform sections at the end of each screen:
 *
 *   - Mobile only: Translation Only, Cantillation, Nikud, Clear Storage
 *   - Web only:    Design System, Mobile Design Guide
 *
 * Dependency rules (rendered state may gate visibility/disabled):
 *   - Sefer Style requires Full Chapter enabled.
 *   - Hebrew-dependent controls (Qumran, Hebrew Only, Cantillation,
 *     Nikud) are dimmed/disabled when Translation Only is active.
 */
export type SharedSettingId =
	| "theme"
	| "language"
	| "besorahTextVersion"
	| "fullChapter"
	| "seferStyle"
	| "hebrewOnly"
	| "qumran";

export const SHARED_SETTINGS_ORDER: readonly SharedSettingId[] = [
	"theme",
	"language",
	"besorahTextVersion",
	"fullChapter",
	"seferStyle",
	"hebrewOnly",
	"qumran",
] as const;
