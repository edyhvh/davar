import { AnimatePresence, motion } from "motion/react";
import type React from "react";
import { useEffect } from "react";

interface BottomSheetProps {
	isOpen: boolean;
	onClose: () => void;
	onAfterClose?: () => void;
	children: React.ReactNode;
	title?: string;
}

export function BottomSheet({
	isOpen,
	onClose,
	onAfterClose,
	children,
	title,
}: BottomSheetProps) {
	// Prevent scroll on body when bottom sheet is open
	useEffect(() => {
		if (isOpen) {
			document.body.style.overflow = "hidden";
		} else {
			document.body.style.overflow = "unset";
		}
		return () => {
			document.body.style.overflow = "unset";
		};
	}, [isOpen]);

	return (
		<AnimatePresence onExitComplete={onAfterClose}>
			{isOpen && (
				<>
					{/* Backdrop */}
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0, transition: { duration: 0.1 } }}
						transition={{ duration: 0.2 }}
						className="fixed inset-0 bg-black/40 z-[200]"
						onClick={onClose}
					/>

					{/* Bottom Sheet */}
					<motion.div
						initial={{ y: "100%", opacity: 0 }}
						animate={{ y: 0, opacity: 1 }}
						exit={{ y: "100%", opacity: 0, transition: { duration: 0.01 } }}
						transition={{ type: "spring", damping: 30, stiffness: 300 }}
						className="fixed bottom-0 left-0 right-0 z-[201] bg-[var(--neomorph-bg)] rounded-t-[32px] shadow-[0_-8px_32px_var(--neomorph-shadow-dark)] max-h-[80vh] flex flex-col"
						style={{
							maxHeight:
								"min(80vh, calc(100dvh - env(safe-area-inset-top) - 8px))",
							paddingBottom: "max(0px, env(safe-area-inset-bottom))",
						}}
					>
						{/* Handle bar */}
						<div className="flex justify-center pt-3 pb-2">
							<div
								className="w-12 h-1.5 rounded-full bg-[var(--neomorph-border)]"
								style={{
									boxShadow:
										"inset 2px 2px 4px var(--neomorph-inset-shadow-dark), inset -2px -2px 4px var(--neomorph-inset-shadow-light)",
								}}
							/>
						</div>

						{/* Title */}
						{title && (
							<div
								className="px-6 py-3 text-center text-[var(--text-primary)]"
								style={{
									fontFamily: "'Inter', sans-serif",
									fontSize: "18px",
									fontWeight: 600,
								}}
							>
								{title}
							</div>
						)}

						{/* Scrollable Content */}
						<div
							className="overflow-y-auto px-6 pt-2"
							style={{
								paddingBottom: "calc(2rem + env(safe-area-inset-bottom))",
							}}
						>
							{children}
						</div>
					</motion.div>
				</>
			)}
		</AnimatePresence>
	);
}
