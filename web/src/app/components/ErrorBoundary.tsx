import React, { Component, type ErrorInfo, type ReactNode } from "react";
import { getStoredReadingState } from "../utils/storageHelpers";
import { translate } from "../hooks/useTranslation";

interface ErrorBoundaryProps {
	children: ReactNode;
}

interface ErrorBoundaryState {
	hasError: boolean;
}

export class ErrorBoundary extends Component<
	ErrorBoundaryProps,
	ErrorBoundaryState
> {
	state: ErrorBoundaryState = { hasError: false };

	static getDerivedStateFromError(): ErrorBoundaryState {
		return { hasError: true };
	}

	componentDidCatch(error: Error, info: ErrorInfo) {
		console.error("UI error boundary:", error, info);
	}

	render() {
		if (this.state.hasError) {
			const language = getStoredReadingState()?.language ?? "en";
			return (
				<div className="min-h-screen flex items-center justify-center text-center px-6">
					<div>
						<h1 className="text-xl font-semibold text-[var(--text-primary)]">
							{translate(language, "errors.uiFallbackTitle")}
						</h1>
						<p className="mt-2 text-sm text-[var(--text-secondary)]">
							{translate(language, "errors.uiFallbackMessage")}
						</p>
					</div>
				</div>
			);
		}

		return this.props.children;
	}
}
