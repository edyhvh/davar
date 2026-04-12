import { NeumorphCard } from "./NeumorphCard";

export function AppUXFlows() {
	return (
		<div className="mt-16 border-t-4 border-[var(--accent)] pt-8">
			<h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
				App UX Flows & Navigation Structure
			</h2>

			<NeumorphCard className="p-8 space-y-8">
				{/* Navigation Hierarchy Map */}
				<div>
					<h3
						className="text-2xl mb-4"
						style={{ fontFamily: "'Suez One', serif" }}
					>
						1. Navigation Hierarchy Map
					</h3>
					<p
						className="text-[var(--text-secondary)] mb-6"
						style={{ fontFamily: "'Inter', sans-serif" }}
					>
						Create a landscape artboard (1200×800 px) showing the complete app
						structure with the following elements:
					</p>

					{/* Main Tab Bar Structure */}
					<div className="bg-[var(--muted)] p-6 rounded-xl mb-6">
						<h4 className="font-semibold mb-4 text-lg">
							Main Bottom Tab Bar (Fixed Navigation)
						</h4>
						<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
							<div className="bg-[var(--background)] p-4 rounded-lg text-center">
								<div className="text-3xl mb-2">📖</div>
								<div className="font-semibold">Home / Library</div>
								<div className="text-xs text-[var(--text-secondary)] mt-1">
									Icon: book-open
								</div>
								<div className="text-xs text-[var(--text-secondary)]">
									Recent verses
								</div>
							</div>
							<div className="bg-[var(--background)] p-4 rounded-lg text-center">
								<div className="text-3xl mb-2">🔍</div>
								<div className="font-semibold">Search</div>
								<div className="text-xs text-[var(--text-secondary)] mt-1">
									Icon: search
								</div>
								<div className="text-xs text-[var(--text-secondary)]">
									Word/verse search
								</div>
							</div>
							<div className="bg-[var(--background)] p-4 rounded-lg text-center">
								<div className="text-3xl mb-2">🔖</div>
								<div className="font-semibold">Bookmarks</div>
								<div className="text-xs text-[var(--text-secondary)] mt-1">
									Icon: bookmark
								</div>
								<div className="text-xs text-[var(--text-secondary)]">
									Saved verses
								</div>
							</div>
							<div className="bg-[var(--background)] p-4 rounded-lg text-center">
								<div className="text-3xl mb-2">⚙️</div>
								<div className="font-semibold">Settings</div>
								<div className="text-xs text-[var(--text-secondary)] mt-1">
									Icon: settings
								</div>
								<div className="text-xs text-[var(--text-secondary)]">
									App preferences
								</div>
							</div>
						</div>
					</div>

					{/* Key User Flows */}
					<div className="space-y-6">
						<h4 className="font-semibold text-lg mb-3">
							Key User Flows (Draw with Arrows & Labels)
						</h4>

						{/* Flow 1: Home to Verse Detail */}
						<div className="border-2 border-[var(--accent)]/30 rounded-xl p-4 bg-[var(--accent)]/5">
							<h5 className="font-semibold mb-3 text-[var(--accent)]">
								Flow 1: Reading Journey
							</h5>
							<div className="space-y-2 text-sm">
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										1
									</div>
									<div>
										<strong>Home/Library Screen</strong> → Vertical scrollable
										list of recent Verse Cards
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)]">
									• Display: Last 10 read verses, each in neumorphic card with
									book name, chapter:verse, snippet
								</div>
								<div className="flex items-center gap-3 mt-2">
									<div className="text-2xl">↓</div>
									<div className="text-xs text-[var(--text-secondary)]">
										Tap on any card
									</div>
								</div>
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										2
									</div>
									<div>
										<strong>Verse Detail Screen</strong> → Full-screen immersive
										verse reading
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)]">
									• Center: Large Hebrew text (48px Cardo RTL), translation
									below (16px Inter)
									<br />• Top: Book/Chapter selector (Genesis 1:1)
									<br />• Bottom: Subtle toolbar (variants toggle, bookmark,
									share icons)
								</div>
							</div>
						</div>

						{/* Flow 2: Vertical Verse Navigation */}
						<div className="border-2 border-[var(--accent)]/30 rounded-xl p-4 bg-[var(--accent)]/5">
							<h5 className="font-semibold mb-3 text-[var(--accent)]">
								Flow 2: TikTok-Style Vertical Navigation
							</h5>
							<div className="space-y-2 text-sm">
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										↑
									</div>
									<div>
										<strong>Swipe Up Gesture</strong> → Go to Previous Verse
										(Genesis 1:2 → 1:1)
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)]">
									• Smooth transition animation (300ms ease-out)
									<br />• Show previous verse snippet above during swipe (ghost
									effect)
								</div>
								<div className="flex items-center gap-3 mt-2">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										↓
									</div>
									<div>
										<strong>Swipe Down Gesture</strong> → Go to Next Verse
										(Genesis 1:1 → 1:2)
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)]">
									• Same smooth transition
									<br />• Show next verse snippet below during swipe
									<br />• Visual hint: Thin gray line + "Swipe for next verse"
									on first load
								</div>
							</div>
						</div>

						{/* Flow 3: Word Analysis */}
						<div className="border-2 border-[var(--accent)]/30 rounded-xl p-4 bg-[var(--accent)]/5">
							<h5 className="font-semibold mb-3 text-[var(--accent)]">
								Flow 3: Deep Word Study
							</h5>
							<div className="space-y-2 text-sm">
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										1
									</div>
									<div>
										<strong>Verse Detail</strong> → User taps on any Hebrew word
										(e.g., בְּרֵאשִׁית)
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)]">
									• Word highlights with copper accent (#C68F55) on tap
								</div>
								<div className="flex items-center gap-3 mt-2">
									<div className="text-2xl">↓</div>
									<div className="text-xs text-[var(--text-secondary)]">
										Immediate transition (200ms)
									</div>
								</div>
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										2
									</div>
									<div>
										<strong>Word Analysis Bottom Sheet</strong> → Slides up from
										bottom (80% screen height)
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)] space-y-1">
									<div>
										• Header: Hebrew word (28px Cardo RTL) + transliteration
										(14px Inter gray)
									</div>
									<div>• Meanings: Bullet list (16px Inter, 8px gaps)</div>
									<div>
										• Root: Highlighted section with copper bg (#C68F55 at 10%
										opacity)
									</div>
									<div>
										• Instances: Scrollable list → tap verse ref → navigate to
										that verse
									</div>
									<div>• Dismiss: Swipe down or tap backdrop</div>
								</div>
							</div>
						</div>

						{/* Flow 4: Search */}
						<div className="border-2 border-[var(--accent)]/30 rounded-xl p-4 bg-[var(--accent)]/5">
							<h5 className="font-semibold mb-3 text-[var(--accent)]">
								Flow 4: Search & Discovery
							</h5>
							<div className="space-y-2 text-sm">
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										1
									</div>
									<div>
										<strong>Search Screen</strong> → RTL-compatible search input
										at top
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)]">
									• Input: 48px height, 12px border radius, RTL support
									<br />• Placeholder: "Search Hebrew or English..."
									(textSecondary color)
								</div>
								<div className="flex items-center gap-3 mt-2">
									<div className="text-2xl">↓</div>
									<div className="text-xs text-[var(--text-secondary)]">
										Live results as user types
									</div>
								</div>
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										2
									</div>
									<div>
										<strong>Results List</strong> → Scrollable Verse Cards below
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)]">
									• Each result: Mini Verse Card (compact version: book+ref,
									Hebrew snippet, match highlighting)
									<br />• Tap any result → Navigate to Verse Detail screen
								</div>
							</div>
						</div>

						{/* Flow 5: Settings */}
						<div className="border-2 border-[var(--accent)]/30 rounded-xl p-4 bg-[var(--accent)]/5">
							<h5 className="font-semibold mb-3 text-[var(--accent)]">
								Flow 5: Settings & Preferences
							</h5>
							<div className="space-y-2 text-sm">
								<div className="flex items-center gap-3">
									<div className="bg-[var(--accent)] text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
										⚙
									</div>
									<div>
										<strong>Settings Screen</strong> → Simple vertical list with
										controls
									</div>
								</div>
								<div className="ml-9 text-[var(--text-secondary)] space-y-1">
									<div>
										• <strong>Theme Toggle:</strong> Light/Dark mode (pill
										toggle, 80×40px)
									</div>
									<div>
										• <strong>Font Size:</strong> Slider (Small 36px → Large
										56px for Hebrew)
									</div>
									<div>
										• <strong>Show Qumran Variants:</strong> On/Off toggle
										button (64px circular)
									</div>
									<div>
										• <strong>Language:</strong> Dropdown (English, Español,
										עברית)
									</div>
									<div>
										• <strong>Offline Sync:</strong> Status indicator + manual
										sync button
									</div>
									<div>
										• <strong>Design System:</strong> Link to view web design
										guide
									</div>
									<div>
										• <strong>Mobile Guide:</strong> Link to view this mobile
										guide
									</div>
								</div>
							</div>
						</div>
					</div>

					{/* Visual Design Notes */}
					<div className="mt-6 bg-[var(--background)] border-2 border-[var(--border)] rounded-xl p-4">
						<h4 className="font-semibold mb-3">
							Visual Design for Flow Diagram
						</h4>
						<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
							<li>
								• Use <strong>arrows</strong> with labels for transitions (e.g.,
								"Tap", "Swipe Up", "Drag Down")
							</li>
							<li>
								• Color code by interaction type: Tap = #7AA0D6 (blue), Gesture
								= #B07A3C (copper), Auto = gray
							</li>
							<li>
								• Screen thumbnails: Use rounded rectangles (24px radius)
								representing iPhone 14 Pro (393×852 ratio)
							</li>
							<li>
								• Group related flows with background rectangles (subtle fill,
								8px padding)
							</li>
							<li>
								• Add state indicators: Active (solid accent border), Inactive
								(dotted gray)
							</li>
						</ul>
					</div>
				</div>

				{/* Detailed Screen Flows - Using text since this will be implemented in Figma */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-2xl mb-4"
						style={{ fontFamily: "'Suez One', serif" }}
					>
						2. Detailed Screen Specifications
					</h3>
					<p
						className="text-[var(--text-secondary)] mb-4"
						style={{ fontFamily: "'Inter', sans-serif" }}
					>
						Create portrait artboards (iPhone 14 Pro: 393×852 px) for each
						screen. Link them with prototyping connections. All specifications
						reference existing design tokens, typography, and components from
						the Mobile Design System Guide.
					</p>
					<div className="bg-[var(--muted)] p-4 rounded-xl text-sm text-[var(--text-secondary)]">
						<p className="font-semibold mb-2">Implementation Note:</p>
						<p>
							This section provides the complete navigation structure and user
							flows. When creating the Figma artboards, ensure all colors,
							typography, spacing, and components match the design tokens and
							components defined in Steps 1-7 of the Mobile Design System Guide
							above. Use Figma's prototyping tools to link screens and
							demonstrate gesture interactions.
						</p>
					</div>
				</div>

				{/* Integration Checklist */}
				<div className="border-t border-[var(--neomorph-border)] pt-8 bg-[var(--accent)]/5 p-6 rounded-xl">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						✅ UX Flows Integration Checklist
					</h3>
					<div className="space-y-3 text-sm">
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">1.</div>
							<div>
								All screens reference existing design tokens (colors,
								typography, spacing, shadows)
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">2.</div>
							<div>
								Components reuse defined elements: Neumorphic Buttons, Verse
								Cards, Bottom Sheets
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">3.</div>
							<div>
								Auto-layout applied to all frames with proper constraints
								(Fill/Hug/Fixed)
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">4.</div>
							<div>
								Prototyping links created for primary user flows (Home → Verse →
								Word Analysis)
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">5.</div>
							<div>
								Safe areas marked on all artboards (44px top iOS, 34px bottom
								iOS)
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">6.</div>
							<div>
								RTL support verified on all Hebrew text elements (Cardo font,
								right-aligned)
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">7.</div>
							<div>
								Dark/Light mode variables applied, both themes previewable via
								mode switching
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">8.</div>
							<div>
								TikTok-style vertical swipe gestures implemented with Smart
								Animate for verse navigation
							</div>
						</div>
						<div className="flex items-start gap-2">
							<div className="text-[var(--accent)] font-bold">9.</div>
							<div>
								Export-ready: All components named consistently, groups
								organized, layers cleaned up
							</div>
						</div>
					</div>
				</div>
			</NeumorphCard>
		</div>
	);
}
