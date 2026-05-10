import React from "react";
import type { TranslationFootnote } from "../services/verseService";

const superscriptDigitMap: Record<string, string> = {
	"⁰": "0",
	"¹": "1",
	"²": "2",
	"³": "3",
	"⁴": "4",
	"⁵": "5",
	"⁶": "6",
	"⁷": "7",
	"⁸": "8",
	"⁹": "9",
};

const superscriptPattern = /[⁰¹²³⁴⁵⁶⁷⁸⁹]+/g;
const bracketFootnotePattern = /\[([a-z0-9]+)\]/gi;
const footnoteMarkerClass =
	"ml-0.5 align-super relative -top-[0.22em] inline-block text-[0.4em] leading-none font-semibold tracking-[0.01em] tabular-nums text-[#9f6a2f] dark:text-[#d2a06b]";
const fallbackMarkerClass =
	"ml-0.5 align-super relative -top-[0.22em] inline-block text-[0.4em] leading-none font-semibold tabular-nums text-[#9f6a2f] dark:text-[#d2a06b]";
const footnoteTooltipClass =
	"pointer-events-none invisible absolute top-full left-1/2 z-30 mt-2 w-[min(320px,82vw)] -translate-x-1/2 rounded-xl border px-3 py-2 text-left opacity-0 shadow-xl backdrop-blur-[1px] transition-opacity group-hover:visible group-hover:opacity-100";

const normalizeSuperscripts = (value: string): string =>
	value
		.split("")
		.map((char) => superscriptDigitMap[char] ?? char)
		.join("");

const toSuperscriptNumber = (value: string): string =>
	value
		.split("")
		.map((char) => {
			const match = Object.entries(superscriptDigitMap).find(
				([, digit]) => digit === char,
			);
			return match?.[0] ?? char;
		})
		.join("");

const buildFootnoteLookup = (
	footnotes?: TranslationFootnote[],
): Map<string, TranslationFootnote> => {
	const lookup = new Map<string, TranslationFootnote>();
	if (!footnotes?.length) {
		return lookup;
	}

	for (const footnote of footnotes) {
		const marker = footnote.marker.trim();
		const number = footnote.number.trim();

		if (marker) {
			lookup.set(marker, footnote);
			lookup.set(`[${marker}]`, footnote);
		}

		if (number) {
			lookup.set(toSuperscriptNumber(number), footnote);
		}
	}

	return lookup;
};

const renderTextSegment = (
	text: string,
	italic: boolean,
	keyPrefix: string,
	hideSuperscripts: boolean,
	footnoteLookup: Map<string, TranslationFootnote>,
): React.ReactNode[] => {
	const nodes: React.ReactNode[] = [];
	let lastIndex = 0;
	let matchIndex = 0;

	// Find all matches (both superscript digits and bracket footnotes)
	const allMatches: Array<{
		type: "superscript" | "bracket";
		start: number;
		end: number;
		content: string;
	}> = [];

	// Find superscript digit matches
	for (const match of text.matchAll(superscriptPattern)) {
		if (match.index === undefined) continue;
		allMatches.push({
			type: "superscript",
			start: match.index,
			end: match.index + match[0].length,
			content: match[0],
		});
	}

	// Find bracket footnote matches
	for (const match of text.matchAll(bracketFootnotePattern)) {
		if (match.index === undefined) continue;
		allMatches.push({
			type: "bracket",
			start: match.index,
			end: match.index + match[0].length,
			content: match[0],
		});
	}

	// Sort matches by position
	allMatches.sort((a, b) => a.start - b.start);

	for (const match of allMatches) {
		const start = match.start;
		const end = match.end;
		const plainText = text.slice(lastIndex, start);

		if (plainText) {
			nodes.push(
				italic ? (
					<span key={`${keyPrefix}-text-${matchIndex}`} className="italic">
						{plainText}
					</span>
				) : (
					<React.Fragment key={`${keyPrefix}-text-${matchIndex}`}>
						{plainText}
					</React.Fragment>
				),
			);
		}

		if (!hideSuperscripts) {
			if (match.type === "superscript") {
				const normalized = normalizeSuperscripts(match.content);
				const footnote = footnoteLookup.get(match.content);

				if (footnote) {
					nodes.push(
						<span
							key={`${keyPrefix}-sup-${matchIndex}`}
							className="group relative inline-flex"
						>
							<sup className={`${footnoteMarkerClass}${italic ? " italic" : ""}`}>
								{normalized}
							</sup>
							<span
								className={footnoteTooltipClass}
								style={{
									background: "var(--background, #f6f1e8)",
									borderColor: "var(--neomorph-border, rgba(122, 95, 62, 0.35))",
									color: "var(--text-primary, #2a2118)",
									boxShadow:
										"0 10px 24px rgba(29, 23, 17, 0.24), 0 2px 8px rgba(29, 23, 17, 0.16)",
								}}
							>
								{footnote.word ? (
									<span className="mb-1 block text-[13px] font-semibold">
										{footnote.word}
									</span>
								) : null}
								<span className="block text-[12px] leading-snug">
									{footnote.explanation}
								</span>
							</span>
						</span>,
					);
				} else {
					nodes.push(
						<sup
							key={`${keyPrefix}-sup-${matchIndex}`}
							className={`${fallbackMarkerClass}${italic ? " italic" : ""}`}
						>
							{normalized}
						</sup>,
					);
				}
			} else if (match.type === "bracket") {
				// Render bracket footnotes as superscripts
				const marker = match.content.slice(1, -1);
				const footnote =
					footnoteLookup.get(match.content) ?? footnoteLookup.get(marker);

				if (footnote) {
					nodes.push(
						<span
							key={`${keyPrefix}-bracket-${matchIndex}`}
							className="group relative inline-flex"
						>
							<sup className={`${footnoteMarkerClass}${italic ? " italic" : ""}`}>
								{marker}
							</sup>
							<span
								className={footnoteTooltipClass}
								style={{
									background: "var(--background, #f6f1e8)",
									borderColor: "var(--neomorph-border, rgba(122, 95, 62, 0.35))",
									color: "var(--text-primary, #2a2118)",
									boxShadow:
										"0 10px 24px rgba(29, 23, 17, 0.24), 0 2px 8px rgba(29, 23, 17, 0.16)",
								}}
							>
								{footnote.word ? (
									<span className="mb-1 block text-[13px] font-semibold">
										{footnote.word}
									</span>
								) : null}
								<span className="block text-[12px] leading-snug">
									{footnote.explanation}
								</span>
							</span>
						</span>,
					);
				} else {
					nodes.push(
						<sup
							key={`${keyPrefix}-bracket-${matchIndex}`}
							className={`${fallbackMarkerClass}${italic ? " italic" : ""}`}
						>
							{marker}
						</sup>,
					);
				}
			}
		}

		lastIndex = end;
		matchIndex += 1;
	}

	const trailingText = text.slice(lastIndex);
	if (trailingText) {
		nodes.push(
			italic ? (
				<span key={`${keyPrefix}-text-tail`} className="italic">
					{trailingText}
				</span>
			) : (
				<React.Fragment key={`${keyPrefix}-text-tail`}>
					{trailingText}
				</React.Fragment>
			),
		);
	}

	return nodes;
};

export const renderTranslation = (
	translation: string,
	options?: {
		hideSuperscripts?: boolean;
		footnotes?: TranslationFootnote[];
	},
): React.ReactNode[] => {
	if (!translation) return [];

	const { hideSuperscripts = false, footnotes } = options || {};
	const footnoteLookup = buildFootnoteLookup(footnotes);
	const tokens = translation
		.split(/(<\/?em>)/i)
		.filter((token) => token !== "");
	const nodes: React.ReactNode[] = [];
	let italic = false;

	tokens.forEach((token, index) => {
		const lowerToken = token.toLowerCase();

		if (lowerToken === "<em>") {
			italic = true;
			return;
		}

		if (lowerToken === "</em>") {
			italic = false;
			return;
		}

		nodes.push(
			...renderTextSegment(
				token,
				italic,
				`seg-${index}`,
				hideSuperscripts,
				footnoteLookup,
			),
		);
	});

	return nodes;
};
