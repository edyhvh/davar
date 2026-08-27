import { useEffect, useMemo, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { useTranslation } from "../hooks/useTranslation";
import {
	getChapterCount,
	getChapterVerses,
	type VerseResponse,
} from "../services/staticData";
import { formatBookDisplayName } from "../utils/bookNameFormatter";

interface TthSectionProps {
	books: { id: string; name: string; hebrew_name: string; spanish_name: string }[];
	language: "en" | "es" | "he";
	initialBook?: string;
	initialChapter?: number;
	onBack: () => void;
}

export function TthSection({
	books,
	language,
	initialBook,
	initialChapter,
	onBack,
}: TthSectionProps) {
	const { t } = useTranslation(language);
	const [selectedBook, setSelectedBook] = useState<string | null>(
		initialBook ?? null,
	);
	const [chapterNumbers, setChapterNumbers] = useState<number[]>([]);
	const [selectedChapter, setSelectedChapter] = useState<number | null>(
		initialChapter ?? null,
	);
	const [verses, setVerses] = useState<VerseResponse[]>([]);
	const [search, setSearch] = useState("");
	const [isLoadingChapters, setIsLoadingChapters] = useState(false);
	const [isLoadingVerses, setIsLoadingVerses] = useState(false);
	const [error, setError] = useState<string | null>(null);

	// Only books that actually exist in the TTH dataset are offered here;
	// the caller pre-filters via the TTH book mapping.
	const filteredBooks = useMemo(() => {
		const normalizedSearch = search.trim().toLowerCase();
		if (!normalizedSearch) return books;
		return books.filter((item) => {
			const haystack = [
				item.name,
				item.spanish_name,
				item.hebrew_name,
			]
				.filter(Boolean)
				.join(" ")
				.toLowerCase();
			return haystack.includes(normalizedSearch);
		});
	}, [books, search]);

	useEffect(() => {
		if (!selectedBook) return;
		let isMounted = true;
		setIsLoadingChapters(true);
		setError(null);
		getChapterCount(selectedBook.toLowerCase())
			.then((count) => {
				if (!isMounted) return;
				setChapterNumbers(
					Array.from({ length: Math.max(count, 0) }, (_, i) => i + 1),
				);
			})
			.catch(() => {
				if (isMounted) setError(t("errors.loadVerses"));
			})
			.finally(() => {
				if (isMounted) setIsLoadingChapters(false);
			});
		return () => {
			isMounted = false;
		};
	}, [selectedBook, t]);

	useEffect(() => {
		if (!selectedBook || !selectedChapter) return;
		let isMounted = true;
		setIsLoadingVerses(true);
		setError(null);
		setVerses([]);
		getChapterVerses(selectedBook.toLowerCase(), selectedChapter, {
			language: "es",
			showDss: false,
			hebrewOnly: false,
		})
			.then((loadedVerses) => {
				if (!isMounted) return;
				setVerses(loadedVerses);
			})
			.catch(() => {
				if (isMounted) setError(t("errors.loadVerses"));
			})
			.finally(() => {
				if (isMounted) setIsLoadingVerses(false);
			});
		return () => {
			isMounted = false;
		};
	}, [selectedBook, selectedChapter, t]);

	const selectedBookDisplay = selectedBook
		? formatBookDisplayName(
				books.find(
					(item) => item.name.toLowerCase() === selectedBook.toLowerCase(),
				)?.spanish_name || selectedBook,
			)
		: null;

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between gap-4">
				<button
					type="button"
					onClick={onBack}
					className="flex items-center gap-2 rounded-full px-4 py-2 text-sm transition-all md:hover:scale-[1.02] md:active:scale-[0.98]"
					style={{
						fontFamily: "'Inter', sans-serif",
						backgroundColor: "var(--neomorph-bg)",
						border: "1px solid var(--neomorph-border)",
						boxShadow:
							"6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)",
					}}
					aria-label={t("navigation.backToApp")}
				>
					<ArrowLeft className="w-3 h-3 text-[var(--text-primary)]" />
					<span className="text-[var(--text-primary)]">
						{t("navigation.backToApp")}
					</span>
				</button>
				<h1
					className="text-lg font-semibold text-[var(--text-primary)]"
					style={{ fontFamily: "'Inter', sans-serif" }}
				>
					{t("navigation.tthSection")}
				</h1>
			</div>

			{!selectedBook && (
				<div className="space-y-4">
					<input
						value={search}
						onChange={(event) => setSearch(event.target.value)}
						placeholder={t("navigation.tthSearchBooks")}
						className="w-full rounded-full px-4 py-2 text-base md:text-sm text-[var(--text-primary)]"
						style={{
							fontFamily: "'Inter', sans-serif",
							backgroundColor: "var(--neomorph-bg)",
							border: "1px solid var(--neomorph-border)",
							boxShadow:
								"inset 3px 3px 6px var(--neomorph-inset-shadow-dark), inset -3px -3px 6px var(--neomorph-inset-shadow-light)",
						}}
					/>
					{filteredBooks.length === 0 ? (
						<p
							className="py-8 text-center text-sm text-[var(--text-secondary)]"
							style={{ fontFamily: "'Inter', sans-serif" }}
						>
							{t("navigation.tthNoBooksFound")}
						</p>
					) : (
						<div className="grid grid-cols-1 gap-2 sm:grid-cols-2 md:grid-cols-3">
							{filteredBooks.map((item) => (
								<button
									type="button"
									key={item.id}
									onClick={() => setSelectedBook(item.name)}
									className="flex w-full items-center justify-between rounded-xl px-4 py-3 transition-all md:hover:scale-[1.01]"
									style={{
										fontFamily: "'Inter', sans-serif",
										backgroundColor: "var(--muted)",
									}}
								>
									<span className="text-xs tracking-wide uppercase text-[var(--text-primary)]">
										{formatBookDisplayName(item.spanish_name || item.name)}
									</span>
									<span
										className="text-sm text-[var(--text-secondary)]"
										style={{ fontFamily: "'Suez One', serif" }}
									>
										{item.hebrew_name}
									</span>
								</button>
							))}
						</div>
					)}
				</div>
			)}

			{selectedBook && !selectedChapter && (
				<div className="space-y-4">
					<h2
						className="text-base font-medium text-[var(--text-primary)]"
						style={{ fontFamily: "'Inter', sans-serif" }}
					>
						{selectedBookDisplay} — {t("navigation.tthSelectChapter")}
					</h2>
					{isLoadingChapters ? (
						<p
							className="py-8 text-center text-sm text-[var(--text-secondary)]"
							style={{ fontFamily: "'Inter', sans-serif" }}
						>
							{t("common.loading")}
						</p>
					) : chapterNumbers.length === 0 ? (
						<p
							className="py-8 text-center text-sm text-[var(--text-secondary)]"
							style={{ fontFamily: "'Inter', sans-serif" }}
						>
							{t("navigation.noChapters")}
						</p>
					) : (
						<div className="grid grid-cols-5 gap-2 md:grid-cols-10">
							{chapterNumbers.map((item) => (
								<button
									type="button"
									key={item}
									onClick={() => setSelectedChapter(item)}
									className="rounded-xl px-2 py-2 text-xs transition-all md:hover:scale-[1.05]"
									style={{
										fontFamily: "'Inter', sans-serif",
										backgroundColor: "var(--muted)",
										color: "var(--text-primary)",
									}}
								>
									{item}
								</button>
							))}
						</div>
					)}
				</div>
			)}

			{selectedBook && selectedChapter && (
				<div className="space-y-4">
					<div className="flex flex-wrap items-center justify-between gap-2">
						<h2
							className="text-base font-medium text-[var(--text-primary)]"
							style={{ fontFamily: "'Inter', sans-serif" }}
						>
							{selectedBookDisplay} {selectedChapter}
						</h2>
						<div className="flex gap-2">
							<button
								type="button"
								onClick={() => setSelectedChapter(null)}
								className="rounded-full px-4 py-1.5 text-xs transition-all md:hover:scale-[1.02]"
								style={{
									fontFamily: "'Inter', sans-serif",
									backgroundColor: "var(--muted)",
									color: "var(--text-primary)",
								}}
							>
								{t("navigation.tthSelectChapter")}
							</button>
							<button
								type="button"
								onClick={() => {
									setSelectedChapter(null);
									setSelectedBook(null);
								}}
								className="rounded-full px-4 py-1.5 text-xs transition-all md:hover:scale-[1.02]"
								style={{
									fontFamily: "'Inter', sans-serif",
									backgroundColor: "var(--muted)",
									color: "var(--text-primary)",
								}}
							>
								{t("navigation.book")}
							</button>
						</div>
					</div>

					{isLoadingVerses ? (
						<p
							className="py-8 text-center text-sm text-[var(--text-secondary)]"
							style={{ fontFamily: "'Inter', sans-serif" }}
						>
							{t("common.loading")}
						</p>
					) : error ? (
						<p
							className="py-8 text-center text-sm text-[var(--text-secondary)]"
							style={{ fontFamily: "'Inter', sans-serif" }}
						>
							{error}
						</p>
					) : verses.length === 0 ? (
						<p
							className="py-8 text-center text-sm text-[var(--text-secondary)]"
							style={{ fontFamily: "'Inter', sans-serif" }}
						>
							{t("navigation.noVerses")}
						</p>
					) : (
						<div className="space-y-3">
							{verses.map((verse) => (
								<p
									key={verse.verse}
									className="text-sm leading-7 text-[var(--text-primary)]"
									style={{ fontFamily: "'Inter', sans-serif" }}
								>
									<span className="mr-2 align-super text-[10px] text-[var(--text-secondary)]">
										{verse.verse}
									</span>
									{verse.translation?.trim() ||
										verse.hebrew.trim() ||
										t("verse.missingSpanishTranslation")}
								</p>
							))}
						</div>
					)}
				</div>
			)}

			<p
				className="pt-4 text-center text-[11px] leading-snug text-[var(--text-secondary)]"
				style={{ fontFamily: "'Inter', sans-serif" }}
			>
				{t("navigation.tthLicenseNotice")}
			</p>
		</div>
	);
}
