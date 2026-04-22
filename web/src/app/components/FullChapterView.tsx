import { useTranslation } from "../hooks/useTranslation";
import type { VerseResponse, WordResponse } from "../services/verseService";
import {
	getPrefixSegments,
	removeMaqafForDisplay,
	removeSofPasukForDisplay,
	stripCantillation,
	stripMeteg,
	stripNikud,
} from "../utils/hebrew";
import {
	getTranslationKey,
	shouldHideSuperscripts,
	shouldHideTranslationText,
} from "../utils/translationConfig";
import { renderTranslation } from "../utils/translationFormatter";

interface FullChapterViewProps {
	verses: VerseResponse[];
	bookName: string;
	bookNameHebrew: string;
	chapter: number;
	language: "en" | "es" | "he";
	hebrewOnly: boolean;
	translationOnly?: boolean;
	seferMode?: boolean;
	onWordClick: (word: WordResponse) => void;
	showQumran?: boolean;
	selectedWord?: string | null;
	showNikud?: boolean;
	showCantillation?: boolean;
	isBesorah?: boolean;
}

export function FullChapterView({
	verses,
	language,
	hebrewOnly,
	translationOnly = false,
	seferMode = false,
	onWordClick,
	showQumran,
	selectedWord,
	showNikud = true,
	showCantillation = true,
	isBesorah = false,
}: FullChapterViewProps) {
	const { t } = useTranslation(language);
	const shouldShowSefer = seferMode && (hebrewOnly || translationOnly);
	const spanishMissingTranslation = t("verse.missingSpanishTranslation");
	const hideSuperscripts = shouldHideSuperscripts(getTranslationKey(language));
	const hideTranslationText =
		shouldHideTranslationText(language, hebrewOnly) && !translationOnly;

	const normalizeForMatch = (text: string) => {
		let normalized = stripNikud(text);
		normalized = stripCantillation(normalized);
		normalized = stripMeteg(normalized);
		normalized = normalized.replace(/\//g, "");
		return normalized.replace(/\u05BE/g, "");
	};

	const normalizedSelected = selectedWord
		? normalizeForMatch(selectedWord)
		: null;

	const renderVerseWords = (verse: VerseResponse) => {
		const dssMap = new Map<number, string>();
		verse.dss?.forEach((variant) => {
			if (
				typeof variant.position !== "number" ||
				variant.position < 0 ||
				!variant.dss_word
			)
				return;
			dssMap.set(variant.position, variant.dss_word);
		});

		return verse.words.map((word, wordIdx) => {
			const variantText = showQumran ? dssMap.get(word.position) : undefined;
			const rawText = variantText ?? word.text;

			// Apply nikud and cantillation settings
			let displayText = rawText;
			if (!showNikud) {
				displayText = stripNikud(displayText);
			}
			if (!showCantillation) {
				displayText = stripCantillation(displayText);
			}
			displayText = stripMeteg(displayText);
			// Remove "/" separators from display
			displayText = displayText.replace(/\//g, "");
			displayText = removeMaqafForDisplay(displayText);
			if (isBesorah) {
				displayText = removeSofPasukForDisplay(displayText);
			}

			// Always compare against the original Masoretic word text, not the
			// display text which may be a DSS variant.
			const normalizedWord = normalizeForMatch(word.text);
			const isSelected =
				Boolean(normalizedSelected) && normalizedSelected === normalizedWord;

			const prefixSegments = word.prefixes?.length
				? getPrefixSegments(displayText, word.prefixes)
				: null;

			return (
				<span key={word.position}>
					<button
						type="button"
						onClick={() => onWordClick(word)}
						className={`word-interactive cursor-pointer ${isSelected ? "verse-highlight" : ""}`}
						style={
							variantText
								? {
										color: "var(--text-hebrew)",
									}
								: undefined
						}
					>
						{prefixSegments?.prefixes?.length ? (
							<>
								<span
									style={{ color: "var(--text-secondary)" }}
									className="cursor-pointer hover:opacity-80"
									title={t("verse.prefixLabel", {
										prefix: word.prefixes?.join(", ") ?? "",
									})}
								>
									{prefixSegments.prefixes.join("")}
								</span>
								<span style={{ color: "var(--text-hebrew)" }}>
									{prefixSegments.root}
								</span>
							</>
						) : (
							displayText
						)}
					</button>
					{wordIdx < verse.words.length - 1 && " "}
				</span>
			);
		});
	};

	return (
		<div className="space-y-6 transition-all duration-500 full-chapter-scroll">
			{/* Chapter Verses */}
			{shouldShowSefer ? (
				<div className="px-2">
					{translationOnly ? (
						<div className="leading-relaxed">
							{verses.map((verse, idx) => (
								<span key={verse.verse}>
									<span
										style={{
											fontFamily: "'Inter', sans-serif",
											fontSize: "16px",
											letterSpacing: "0.08em",
											textTransform: "uppercase",
											color: "var(--text-hebrew)",
											opacity: 0.68,
											marginRight: "8px",
										}}
									>
										{verse.verse}
									</span>
									<span
										style={{
											fontFamily: "'Inter', sans-serif",
											fontSize: "26px",
											color: "var(--text-hebrew)",
											opacity: 1,
											fontWeight: 400,
										}}
									>
										{language === "es" && !(verse.translation ?? "").trim()
											? spanishMissingTranslation
											: renderTranslation(verse.translation ?? "", {
													hideSuperscripts,
													footnotes:
														language === "es" ? verse.translation_footnotes : undefined,
												})}
									</span>
									{idx < verses.length - 1 && " "}
								</span>
							))}
						</div>
					) : (
						<div
							className="leading-relaxed tracking-[0.01em]"
							style={{
								fontFamily: "'Cardo', serif",
								fontSize: "48px",
								direction: "rtl",
								color: "var(--text-hebrew)",
								lineHeight: 1.9,
								letterSpacing: "0.01em",
							}}
						>
							{verses.map((verse, idx) => (
								<span key={verse.verse}>
									<span
										className="text-[var(--text-secondary)] opacity-40 ml-2"
										style={{
											fontFamily: "'Inter', sans-serif",
											fontSize: "14px",
										}}
									>
										[{idx + 1}]
									</span>
									{renderVerseWords(verse)}
									{idx < verses.length - 1 && " "}
								</span>
							))}
						</div>
					)}
				</div>
			) : (
				<div className="space-y-8 px-2">
					{verses.map((verse, idx) => (
						<div
							key={verse.verse}
							className="space-y-3 transition-all duration-300 verse-block"
						>
							{/* Hebrew Text with Verse Number */}
							{!translationOnly && (
								<div
									className="leading-relaxed tracking-[0.01em]"
									style={{
										fontFamily: "'Cardo', serif",
										fontSize: "48px",
										direction: "rtl",
										color: "var(--text-hebrew)",
										lineHeight: 1.85,
									}}
								>
									<span
										className="text-[var(--text-secondary)] opacity-40 ml-2"
										style={{
											fontFamily: "'Inter', sans-serif",
											fontSize: "14px",
										}}
									>
										[{idx + 1}]
									</span>
									{renderVerseWords(verse)}
								</div>
							)}

							{/* Translation - only show if not Hebrew Only mode */}
							{!hideTranslationText && (
								<div
									className="leading-relaxed"
									style={{
										fontFamily: "'Inter', sans-serif",
										fontSize: translationOnly ? "22px" : "15px",
										color: translationOnly
											? "var(--text-hebrew)"
											: "var(--text-secondary)",
										opacity: 1,
									}}
								>
									{translationOnly ? (
										<>
											<span
												style={{
													fontSize: "15px",
													letterSpacing: "0.08em",
													textTransform: "uppercase",
													color: "var(--text-hebrew)",
													opacity: 0.68,
													marginRight: "8px",
												}}
											>
												{verse.verse}
											</span>
											{language === "es" && !(verse.translation ?? "").trim()
												? spanishMissingTranslation
												: renderTranslation(verse.translation ?? "", {
														hideSuperscripts,
														footnotes:
															translationOnly && language === "es"
																? verse.translation_footnotes
																: undefined,
													})}
										</>
									) : (
										<>
											[
											{language === "es" && !(verse.translation ?? "").trim()
												? spanishMissingTranslation
												: renderTranslation(verse.translation ?? "", {
														hideSuperscripts,
													})}
											]
										</>
									)}
								</div>
							)}
						</div>
					))}
				</div>
			)}
		</div>
	);
}
