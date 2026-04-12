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
	if (!isActive) {
		return (
			<button type="button" onClick={onClick} className="cursor-pointer">
				{word}
			</button>
		);
	}

	return (
		<button
			type="button"
			onClick={onClick}
			className={`word-interactive word-hint ${isPressed ? "word-hint-pressed verse-highlight" : ""}`}
			aria-label="Select word"
		>
			{word}
		</button>
	);
}
