import { WifiOff } from "lucide-react";

interface ConnectionErrorPageProps {
	onRetry?: () => void;
}

export function ConnectionErrorPage({ onRetry }: ConnectionErrorPageProps) {
	return (
		<div className="flex min-h-screen flex-col items-center justify-center p-4 text-center">
			<WifiOff className="mb-4 h-16 w-16 text-gray-400" />
			<h1 className="mb-2 text-2xl font-bold">Connection Error</h1>
			<p className="mb-6 max-w-md text-gray-600">
				Unable to load content. Please check your internet connection and try
				again.
			</p>
			{onRetry && (
				<button
					onClick={onRetry}
					className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
				>
					Retry
				</button>
			)}
		</div>
	);
}
