import type React from "react";

interface SwipeIndicatorProps {
	children: React.ReactNode;
}

export function SwipeIndicator({ children }: SwipeIndicatorProps) {
	return <div className="relative">{children}</div>;
}
