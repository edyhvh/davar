import type React from "react";

interface OnboardingWordHintProps {
	word: string;
	isActive: boolean;
	isPressed?: boolean;
	onClick: () => void;
}

export function OnboardingWordHint({
	word,
	isActive,
	isPressed = false,
	onClick,
}: OnboardingWordHintProps) {
	const handleKeyDown = (event: React.KeyboardEvent<HTMLSpanElement>) => {
		if (event.key === "Enter" || event.key === " ") {
			event.preventDefault();
			onClick();
		}
	};

	if (!isActive) {
		return (
			<span onClick={onClick} className="cursor-pointer">
				{word}
			</span>
		);
	}

	return (
		<span
			role="button"
			tabIndex={0}
			onClick={onClick}
			onKeyDown={handleKeyDown}
			className={`word-interactive word-hint ${isPressed ? "word-hint-pressed verse-highlight" : ""}`}
			aria-label="Select word"
		>
			{word}
		</span>
	);
}
