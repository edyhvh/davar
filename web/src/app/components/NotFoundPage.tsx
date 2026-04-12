import { AlertCircle, BookOpen } from "lucide-react";
import { type AppLanguage, useTranslation } from "../hooks/useTranslation";

interface NotFoundPageProps {
	language: AppLanguage;
	onGoHome?: () => void;
	onGoBack?: () => void;
}

export function NotFoundPage({
	language,
	onGoHome,
	onGoBack,
}: NotFoundPageProps) {
	const { t } = useTranslation(language);

	return (
		<div className="min-h-[60vh] flex items-center justify-center">
			<div className="text-center px-6">
				{/* Icon */}
				<div className="mb-6 flex justify-center">
					<AlertCircle className="w-12 h-12 text-[var(--copper-highlight)]" />
				</div>

				{/* Title */}
				<h1
					className="text-xl mb-4 text-[var(--text-primary)]"
					style={{ fontFamily: "'Jost', sans-serif" }}
				>
					{t("errors.notFound.title")}
				</h1>

				{/* Message */}
				<p
					className="text-sm text-[var(--text-secondary)] mb-6"
					style={{ fontFamily: "'Arimo', sans-serif" }}
				>
					{t("errors.notFound.message")}
				</p>

				{/* Go Back to Verse Button */}
				{onGoBack ? (
					<button
						type="button"
						onClick={onGoBack}
						className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-dark)] transition-colors"
						style={{ fontFamily: "'Jost', sans-serif" }}
					>
						<BookOpen className="w-4 h-4" />
						{t("errors.notFound.goToVerse")}
					</button>
				) : onGoHome ? (
					<button
						type="button"
						onClick={onGoHome}
						className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-dark)] transition-colors"
						style={{ fontFamily: "'Jost', sans-serif" }}
					>
						<BookOpen className="w-4 h-4" />
						{t("errors.notFound.goToVerse")}
					</button>
				) : (
					<a
						href="/verse"
						className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-dark)] transition-colors"
						style={{ fontFamily: "'Jost', sans-serif" }}
					>
						<BookOpen className="w-4 h-4" />
						{t("errors.notFound.goToVerse")}
					</a>
				)}
			</div>
		</div>
	);
}
