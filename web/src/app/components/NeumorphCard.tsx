import type React from "react";

interface NeumorphCardProps {
	children: React.ReactNode;
	className?: string;
	onClick?: () => void;
	onMouseEnter?: React.MouseEventHandler<HTMLElement>;
	onMouseLeave?: React.MouseEventHandler<HTMLElement>;
	hoverable?: boolean;
	inset?: boolean;
}

export function NeumorphCard({
	children,
	className = "",
	onClick,
	onMouseEnter,
	onMouseLeave,
	hoverable = false,
	inset = false,
}: NeumorphCardProps) {
	const classNameValue = `
        relative
        bg-[var(--neomorph-bg)] 
        border border-[var(--neomorph-border)]
        rounded-2xl
        ${
					inset
						? "shadow-[inset_6px_6px_12px_var(--neomorph-inset-shadow-dark),inset_-6px_-6px_12px_var(--neomorph-inset-shadow-light)]"
						: "shadow-[6px_6px_16px_var(--neomorph-shadow-dark),-6px_-6px_16px_var(--neomorph-shadow-light)]"
				}
        transition-all duration-300
        ${hoverable ? "hover:shadow-[4px_4px_12px_var(--neomorph-shadow-dark),-4px_-4px_12px_var(--neomorph-shadow-light)] hover:scale-[1.02] cursor-pointer" : ""}
        ${className}
      `;

	if (onClick) {
		return (
			<button
				type="button"
				onClick={onClick}
				onMouseEnter={onMouseEnter}
				onMouseLeave={onMouseLeave}
				className={classNameValue}
				style={{ textAlign: "inherit" }}
			>
				<div className="relative">{children}</div>
			</button>
		);
	}

	return (
		// biome-ignore lint/a11y/noStaticElementInteractions: hover-only handlers control transient visual states
		<div
			className={classNameValue}
			onMouseEnter={onMouseEnter}
			onMouseLeave={onMouseLeave}
		>
			<div className="relative">{children}</div>
		</div>
	);
}
