import { NeumorphCard } from "./NeumorphCard";
import { Smartphone } from "lucide-react";
import { AppUXFlows } from "./AppUXFlows";

export function MobileDesignSystemGuide() {
	return (
		<div className="space-y-8">
			{/* Header */}
			<div className="flex items-center justify-between">
				<h2 className="text-3xl" style={{ fontFamily: "'Suez One', serif" }}>
					Mobile / React Native Design System Guide
				</h2>
				<Smartphone className="w-8 h-8 text-[var(--accent)]" />
			</div>

			<NeumorphCard className="p-8 space-y-8">
				{/* Introduction */}
				<div>
					<h3
						className="text-2xl mb-4"
						style={{ fontFamily: "'Suez One', serif" }}
					>
						Overview
					</h3>
					<p
						className="text-[var(--text-secondary)]"
						style={{ fontFamily: "'Inter', sans-serif" }}
					>
						This guide provides step-by-step instructions for adapting the Davar
						web design system to a mobile-first React Native application using
						Expo. The goal is 100% compatibility for export to clean React
						Native code while maintaining the reverent, contemplative aesthetic.
					</p>
				</div>

				{/* Step 1: Figma Setup */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Step 1: Figma Page Setup
					</h3>
					<div
						className="space-y-4 text-sm"
						style={{ fontFamily: "'Inter', sans-serif" }}
					>
						<div>
							<h4 className="font-semibold mb-2">
								1.1 Create Mobile Artboards
							</h4>
							<ul className="space-y-2 text-[var(--text-secondary)] ml-4">
								<li>• iPhone 14 Pro: 393 × 852 px (common iOS)</li>
								<li>• iPhone 14 Plus: 428 × 926 px (large iOS)</li>
								<li>• Pixel 7: 412 × 915 px (common Android)</li>
								<li>• Use portrait orientation as primary</li>
								<li>• Account for safe areas: top notch, bottom gesture bar</li>
							</ul>
						</div>
						<div>
							<h4 className="font-semibold mb-2">1.2 Enable Variables</h4>
							<p className="text-[var(--text-secondary)]">
								Use Figma Variables (not styles) for colors, typography,
								spacing, and shadows to enable token-based export compatible
								with React Native.
							</p>
						</div>
					</div>
				</div>

				{/* Step 2: Design Tokens */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Step 2: Design Tokens (Figma Variables)
					</h3>

					<div className="space-y-6">
						{/* Color Variables */}
						<div>
							<h4 className="font-semibold mb-3">2.1 Color Variables</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl space-y-2 font-mono text-xs">
								<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div>
										<div className="text-[var(--text-secondary)]">
											{/* Light Mode */}
										</div>
										<div>primary: #7AA0D6</div>
										<div>primaryDark: #6389BF</div>
										<div>secondary: #B07A3C</div>
										<div>background: #FDFDF9</div>
										<div>surface: #FFFFFF</div>
										<div>textPrimary: #1a1a1a</div>
										<div>textSecondary: #6b6b6b</div>
										<div>border: rgba(0,0,0,0.08)</div>
									</div>
									<div>
										<div className="text-[var(--text-secondary)]">
											{/* Dark Mode */}
										</div>
										<div>primary: #92B5E8</div>
										<div>primaryDark: #7B9ED1</div>
										<div>secondary: #A06C35</div>
										<div>background: #0F0E12</div>
										<div>surface: #17161A</div>
										<div>textPrimary: #ebdbb2</div>
										<div>textSecondary: #a89984</div>
										<div>border: rgba(255,255,255,0.1)</div>
									</div>
								</div>
							</div>
							<p className="text-xs text-[var(--text-secondary)] mt-2">
								Create separate collections for Light and Dark modes, bound to
								same variable names.
							</p>
						</div>

						{/* Typography */}
						<div>
							<h4 className="font-semibold mb-3">
								2.2 Typography Variables (Mobile-Scaled)
							</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl space-y-2 font-mono text-xs">
								<div className="text-[var(--text-secondary)]">
									{/* Font Families */}
								</div>
								<div>
									fontHebrewScripture: "Cardo" (or SBL Hebrew, Ezra SIL)
								</div>
								<div>fontHebrewUI: "Arimo" (or Roboto for Android)</div>
								<div>fontLatinUI: "Inter" (or SF Pro for iOS)</div>
								<div>fontLogo: "Suez One"</div>
								<div className="text-[var(--text-secondary)] mt-3">
									{/* Font Sizes (pt) */}
								</div>
								<div>h1: 28</div>
								<div>h2: 24</div>
								<div>h3: 20</div>
								<div>
									hebrewVerse: 36 (48px on small screens for legibility)
								</div>
								<div>body: 16</div>
								<div>bodySmall: 14</div>
								<div>caption: 12</div>
								<div className="text-[var(--text-secondary)] mt-3">
									{/* Font Weights */}
								</div>
								<div>regular: 400</div>
								<div>medium: 500</div>
								<div>semibold: 600</div>
								<div>bold: 700</div>
								<div className="text-[var(--text-secondary)] mt-3">
									{/* Line Heights */}
								</div>
								<div>hebrewScripture: 1.8-2.0</div>
								<div>body: 1.5</div>
								<div>tight: 1.3</div>
							</div>
						</div>

						{/* Spacing */}
						<div>
							<h4 className="font-semibold mb-3">
								2.3 Spacing System (8pt Grid)
							</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl space-y-1 font-mono text-xs">
								<div>spacing-1: 4px</div>
								<div>spacing-2: 8px</div>
								<div>spacing-3: 12px</div>
								<div>spacing-4: 16px</div>
								<div>spacing-5: 20px</div>
								<div>spacing-6: 24px</div>
								<div>spacing-8: 32px</div>
								<div>spacing-10: 40px</div>
								<div>spacing-12: 48px</div>
								<div>spacing-16: 64px</div>
								<div className="text-[var(--text-secondary)] mt-2">
									{/* Safe Areas */}
								</div>
								<div>safeTop: 44px (iOS) / 24px (Android)</div>
								<div>safeBottom: 34px (iOS) / 0px (Android)</div>
							</div>
						</div>

						{/* Shadows/Elevation */}
						<div>
							<h4 className="font-semibold mb-3">
								2.4 Shadows & Elevation (Mobile-Optimized)
							</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl space-y-2 font-mono text-xs">
								<div className="text-[var(--text-secondary)]">
									{/* Neumorphic Shadows (iOS) */}
								</div>
								<div>shadowRaised: 0px 6px 12px rgba(190,190,200,0.3)</div>
								<div>shadowLight: 0px -6px 12px rgba(255,255,255,0.7)</div>
								<div>
									shadowPressed: inset 3px 3px 6px rgba(190,190,200,0.4)
								</div>
								<div className="text-[var(--text-secondary)] mt-3">
									{/* Android Elevation */}
								</div>
								<div>elevation-1: 2dp</div>
								<div>elevation-2: 4dp</div>
								<div>elevation-3: 8dp</div>
								<div>elevation-4: 12dp</div>
							</div>
							<p className="text-xs text-[var(--text-secondary)] mt-2">
								Note: React Native uses platform-specific shadows (iOS) or
								elevation (Android).
							</p>
						</div>

						{/* Border Radius */}
						<div>
							<h4 className="font-semibold mb-3">2.5 Border Radius</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl space-y-1 font-mono text-xs">
								<div>radius-sm: 8px</div>
								<div>radius-md: 12px</div>
								<div>radius-lg: 16px</div>
								<div>radius-xl: 24px</div>
								<div>radius-full: 999px (pill shape)</div>
							</div>
						</div>
					</div>
				</div>

				{/* Step 3: Components */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Step 3: Mobile Components (Auto-Layout Required)
					</h3>

					<div className="space-y-6">
						{/* Buttons */}
						<div>
							<h4 className="font-semibold mb-3">3.1 Neumorphic Buttons</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Min touch target:</strong> 44×44 px (iOS HIG), 48×48
									px (Material)
								</li>
								<li>
									• <strong>Border radius:</strong> 24px (pill shape) or 12px
									(rounded)
								</li>
								<li>
									• <strong>Padding:</strong> 12px vertical, 24px horizontal
								</li>
								<li>
									• <strong>States:</strong> Default (raised shadow), Pressed
									(inset shadow), Disabled (50% opacity)
								</li>
								<li>
									• <strong>Variants:</strong> Primary (gradient fill),
									Secondary (border only), Text (no background)
								</li>
								<li>
									• Use Auto-layout (horizontal) with 8px gap between icon +
									text
								</li>
							</ul>
						</div>

						{/* Scripture Cards */}
						<div>
							<h4 className="font-semibold mb-3">3.2 Verse Display Cards</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Layout:</strong> Vertical auto-layout (Hebrew →
									Translation → Meta)
								</li>
								<li>
									• <strong>Hebrew text:</strong> 36-48px Cardo, RTL,
									line-height 1.8-2.0, centered
								</li>
								<li>
									• <strong>Translation:</strong> 16px Inter, 24px top margin,
									centered, color: textSecondary
								</li>
								<li>
									• <strong>Card padding:</strong> 24px all sides
								</li>
								<li>
									• <strong>Background:</strong> surface color with neumorphic
									raised shadow
								</li>
								<li>
									• <strong>Swipe gestures:</strong> Add subtle up/down arrows
									or hints for TikTok-style navigation
								</li>
							</ul>
						</div>

						{/* Bottom Navigation */}
						<div>
							<h4 className="font-semibold mb-3">3.3 Bottom Tab Navigation</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Height:</strong> 64px + safeBottom (iOS) or 56px
									(Android)
								</li>
								<li>
									• <strong>Background:</strong> surface with top border (1px,
									border color)
								</li>
								<li>
									• <strong>Icons:</strong> 24×24 px, vertical auto-layout with
									4px gap to label
								</li>
								<li>
									• <strong>Labels:</strong> 12px Inter, medium weight
								</li>
								<li>
									• <strong>Active state:</strong> primary color, inactive:
									textSecondary
								</li>
								<li>
									• Use blur effect (iOS) or solid surface (Android) for
									over-scroll visibility
								</li>
							</ul>
						</div>

						{/* Text Inputs */}
						<div>
							<h4 className="font-semibold mb-3">
								3.4 Input Fields (RTL-Compatible)
							</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Height:</strong> 48px minimum
								</li>
								<li>
									• <strong>Border:</strong> 1px border color, 12px radius
								</li>
								<li>
									• <strong>Padding:</strong> 12px horizontal
								</li>
								<li>
									• <strong>Focus state:</strong> primary color border (2px),
									subtle glow
								</li>
								<li>
									• <strong>RTL support:</strong> textAlign: right for Hebrew,
									left for Latin
								</li>
								<li>
									• <strong>Placeholder:</strong> textSecondary color, 14px
								</li>
							</ul>
						</div>

						{/* Bottom Sheets */}
						<div>
							<h4 className="font-semibold mb-3">
								3.5 Bottom Sheets (Word Analysis, Settings)
							</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Handle:</strong> 32px wide × 4px tall rounded pill,
									12px from top, color: border
								</li>
								<li>
									• <strong>Max height:</strong> 90% of screen height
								</li>
								<li>
									• <strong>Background:</strong> surface color with
									top-left/top-right 24px radius
								</li>
								<li>
									• <strong>Padding:</strong> 24px horizontal, 16px top (after
									handle)
								</li>
								<li>
									• <strong>Backdrop:</strong> Semi-transparent overlay
									(rgba(0,0,0,0.5))
								</li>
								<li>• Drag gesture to dismiss (downward swipe)</li>
							</ul>
						</div>

						{/* Modals */}
						<div>
							<h4 className="font-semibold mb-3">3.6 Book Selector Modal</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Size:</strong> 90% width × 70% height, centered
								</li>
								<li>
									• <strong>Border radius:</strong> 24px all corners
								</li>
								<li>
									• <strong>Background:</strong> surface with neumorphic raised
									shadow
								</li>
								<li>
									• <strong>Close button:</strong> 32×32 px icon button,
									top-right 16px from edge
								</li>
								<li>
									• <strong>Content:</strong> ScrollView with 12px gap between
									book items
								</li>
							</ul>
						</div>

						{/* Icons */}
						<div>
							<h4 className="font-semibold mb-3">
								3.7 Icon Set (Lucide or SF Symbols)
							</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl space-y-1 text-xs">
								<div>• book-open (Scripture library)</div>
								<div>• search (Word search)</div>
								<div>• settings (Settings)</div>
								<div>• bookmark (Save verse)</div>
								<div>• languages (Translation toggle)</div>
								<div>• sun / moon (Theme toggle)</div>
								<div>• chevron-left / chevron-right (Navigation)</div>
								<div>• x (Close)</div>
								<div>• info (Variant info)</div>
								<div>• eye (Show/hide variants)</div>
							</div>
							<p className="text-xs text-[var(--text-secondary)] mt-2">
								Use 24×24 px base size, scale to 20px or 32px for specific
								contexts.
							</p>
						</div>
					</div>
				</div>

				{/* Step 4: Example Layouts */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Step 4: Example Layout Artboards
					</h3>

					<div className="space-y-6">
						<div>
							<h4 className="font-semibold mb-3">4.1 Home / Library Screen</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Safe area top:</strong> Logo + "Davar" text
									(centered)
								</li>
								<li>
									• <strong>Main content:</strong> Recent verses list (vertical
									scroll)
								</li>
								<li>
									• <strong>Card spacing:</strong> 16px gap between cards
								</li>
								<li>
									• <strong>Bottom nav:</strong> Fixed at bottom with safeBottom
									padding
								</li>
								<li>• Use ScrollView with contentInset for safe areas</li>
							</ul>
						</div>

						<div>
							<h4 className="font-semibold mb-3">
								4.2 Verse Detail Screen (TikTok-Style)
							</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Layout:</strong> Full-screen vertical centering
								</li>
								<li>
									• <strong>Top:</strong> Book/Chapter selector (fixed, 16px
									from safeTop)
								</li>
								<li>
									• <strong>Center:</strong> Verse card (Hebrew + Translation)
								</li>
								<li>
									• <strong>Bottom:</strong> Navigation bar with separator line
									above (1px gray)
								</li>
								<li>
									• <strong>Gesture:</strong> Swipe up → previous verse, swipe
									down → next verse
								</li>
								<li>
									• <strong>Hint:</strong> Subtle chevron or "Swipe for next
									verse" text at bottom
								</li>
							</ul>
						</div>

						<div>
							<h4 className="font-semibold mb-3">
								4.3 Word Analysis Bottom Sheet
							</h4>
							<ul className="space-y-2 text-sm text-[var(--text-secondary)]">
								<li>
									• <strong>Header:</strong> Hebrew word (28px Cardo, RTL),
									transliteration below (14px Inter)
								</li>
								<li>
									• <strong>Meanings:</strong> Bullet list, 16px Inter, 8px gap
								</li>
								<li>
									• <strong>Root:</strong> Highlighted section with copper
									background (#C68F55 at 10% opacity)
								</li>
								<li>
									• <strong>Instances:</strong> Scrollable list of verses, tap
									to navigate
								</li>
								<li>
									• <strong>Spacing:</strong> 24px sections, 12px sub-sections
								</li>
							</ul>
						</div>
					</div>
				</div>

				{/* Step 5: Constraints & Responsiveness */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Step 5: Constraints & Auto-Layout Best Practices
					</h3>

					<div className="space-y-4 text-sm text-[var(--text-secondary)]">
						<div>
							<h4 className="font-semibold mb-2">5.1 Auto-Layout Rules</h4>
							<ul className="space-y-1 ml-4">
								<li>• Use Auto-layout on ALL components and frames</li>
								<li>
									• Set proper resizing: Hug content (icons, text), Fill
									container (cards, backgrounds)
								</li>
								<li>
									• Define explicit gaps (8px, 16px, 24px from spacing system)
								</li>
								<li>
									• Use "Packed" alignment for centered content, "Space between"
									for nav bars
								</li>
							</ul>
						</div>

						<div>
							<h4 className="font-semibold mb-2">5.2 Constraints</h4>
							<ul className="space-y-1 ml-4">
								<li>
									• Top elements: Top + Left/Right constraints with fixed
									margins
								</li>
								<li>
									• Bottom nav: Bottom + Left + Right constraints, fixed height
								</li>
								<li>
									• Centered content: Center constraints with max width (360px
									for readability)
								</li>
								<li>
									• Scrollable areas: Top-to-bottom constraints with flexible
									height
								</li>
							</ul>
						</div>

						<div>
							<h4 className="font-semibold mb-2">
								5.3 Responsive Scaling (@2x / @3x)
							</h4>
							<ul className="space-y-1 ml-4">
								<li>
									• Export assets at @2x (iPhone 8-13) and @3x (iPhone 14 Pro+)
								</li>
								<li>• Use logical pixels (pt) in Figma, not physical pixels</li>
								<li>
									• Test layouts on small (iPhone SE 375px), medium (iPhone 14
									393px), large (Plus 428px)
								</li>
							</ul>
						</div>
					</div>
				</div>

				{/* Step 6: Export & Code */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Step 6: Export to React Native / Expo
					</h3>

					<div className="space-y-6">
						<div>
							<h4 className="font-semibold mb-3">
								6.1 Recommended Export Tools
							</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl space-y-2 text-sm">
								<div>
									• <strong>Figma to Code (native plugin):</strong> Basic
									component export
								</div>
								<div>
									• <strong>Builder.io Visual Copilot:</strong> AI-powered React
									Native conversion
								</div>
								<div>
									• <strong>Anima:</strong> Export to React Native with design
									tokens
								</div>
								<div>
									• <strong>TeleportHQ:</strong> Figma → React Native with
									auto-layout preservation
								</div>
								<div>
									• <strong>Manual:</strong> Use Figma Inspect to copy CSS →
									convert to StyleSheet
								</div>
							</div>
						</div>

						<div>
							<h4 className="font-semibold mb-3">6.2 Design Token Export</h4>
							<p className="text-[var(--text-secondary)] mb-2">
								Use Figma Variables to export a JSON token file for use in React
								Native:
							</p>
							<div className="bg-[var(--muted)] p-4 rounded-xl font-mono text-xs">
								<div className="text-[var(--text-secondary)]">
									{/* theme.ts */}
								</div>
								<div>export const colors = {"{"}</div>
								<div className="ml-4">light: {"{"}</div>
								<div className="ml-8">primary: '#7AA0D6',</div>
								<div className="ml-8">background: '#FDFDF9',</div>
								<div className="ml-8">...</div>
								<div className="ml-4">{"}"},</div>
								<div className="ml-4">
									dark: {"{"} ... {"}"}
								</div>
								<div>{"}"};</div>
							</div>
						</div>

						<div>
							<h4 className="font-semibold mb-3">
								6.3 Component Export Example
							</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl font-mono text-xs space-y-3">
								<div>
									<div className="text-[var(--text-secondary)]">
										{/* NeumorphButton.tsx */}
									</div>
									<div>
										import {"{"} Pressable, Text, StyleSheet {"}"} from
										'react-native';
									</div>
									<div className="mt-2">
										const NeumorphButton = (props) ={">"} (
									</div>
									<div className="ml-4">
										{"<"}Pressable style={"{"}styles.button{"}"}
										{"{"}...props{"}"} {">"}
									</div>
									<div className="ml-8">
										{"<"}Text style={"{"}styles.text{"}"}
										{">"}
										{"{"}props.children{"}"}
										{"{"}'/Text{">"}
									</div>
									<div className="ml-4">
										{"</"}Pressable{">"}
									</div>
									<div>);</div>
								</div>
								<div>
									<div className="text-[var(--text-secondary)]">
										{/* StyleSheet */}
									</div>
									<div>const styles = StyleSheet.create({"{"}</div>
									<div className="ml-4">button: {"{"}</div>
									<div className="ml-8">paddingVertical: 12,</div>
									<div className="ml-8">paddingHorizontal: 24,</div>
									<div className="ml-8">borderRadius: 24,</div>
									<div className="ml-8">backgroundColor: colors.surface,</div>
									<div className="ml-8">shadowColor: '#000',</div>
									<div className="ml-8">
										shadowOffset: {"{"} width: 6, height: 6 {"}"},
									</div>
									<div className="ml-8">shadowOpacity: 0.3,</div>
									<div className="ml-8">elevation: 4, {/* Android */}</div>
									<div className="ml-4">{"}"},</div>
									<div>{"}"});</div>
								</div>
							</div>
						</div>

						<div>
							<h4 className="font-semibold mb-3">
								6.4 RTL Support in React Native
							</h4>
							<div className="bg-[var(--muted)] p-4 rounded-xl font-mono text-xs">
								<div className="text-[var(--text-secondary)]">
									{/* Enable RTL */}
								</div>
								<div>
									import {"{"} I18nManager {"}"} from 'react-native';
								</div>
								<div>I18nManager.forceRTL(true);</div>
								<div className="mt-2 text-[var(--text-secondary)]">
									{/* Per-component RTL */}
								</div>
								<div>
									{"<"}Text style={"{{"}textAlign: 'right', writingDirection:
									'rtl'{"}"}
									{">"}
								</div>
								<div className="ml-4">בְּרֵאשִׁית</div>
								<div>
									{"</"}Text{">"}
								</div>
							</div>
						</div>
					</div>
				</div>

				{/* Step 7: Testing & Validation */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Step 7: Testing & Validation
					</h3>

					<div className="space-y-4 text-sm text-[var(--text-secondary)]">
						<div>
							<h4 className="font-semibold mb-2">7.1 Figma Preview</h4>
							<ul className="space-y-1 ml-4">
								<li>
									• Use Figma Mirror app on iPhone/Android to preview designs
									in-device
								</li>
								<li>• Test touch targets (min 44×44 px) with actual fingers</li>
								<li>
									• Validate text legibility at arm's length (typical phone
									reading distance)
								</li>
							</ul>
						</div>

						<div>
							<h4 className="font-semibold mb-2">7.2 Code Validation</h4>
							<ul className="space-y-1 ml-4">
								<li>• Run Expo app on iOS Simulator + Android Emulator</li>
								<li>
									• Test on physical devices (older iPhone SE, modern iPhone 14
									Pro, Pixel)
								</li>
								<li>
									• Verify Hebrew text renders correctly with nikud (diacritics)
								</li>
								<li>• Check safe area handling on notched devices</li>
							</ul>
						</div>

						<div>
							<h4 className="font-semibold mb-2">7.3 Accessibility</h4>
							<ul className="space-y-1 ml-4">
								<li>
									• Ensure min contrast ratio 4.5:1 for body text, 3:1 for large
									text (WCAG AA)
								</li>
								<li>
									• Test with VoiceOver (iOS) and TalkBack (Android) screen
									readers
								</li>
								<li>
									• Support Dynamic Type (iOS) for user font size preferences
								</li>
							</ul>
						</div>
					</div>
				</div>

				{/* Additional Notes */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Additional Implementation Notes
					</h3>

					<div className="space-y-4 text-sm text-[var(--text-secondary)]">
						<div>
							<h4 className="font-semibold mb-2">Offline-First Design</h4>
							<p>
								The design system assumes offline-first usage. Store Bible text,
								variants, and dictionary data locally using AsyncStorage or
								SQLite. Use placeholders for sync status indicators.
							</p>
						</div>

						<div>
							<h4 className="font-semibold mb-2">Performance Optimization</h4>
							<ul className="space-y-1 ml-4">
								<li>
									• Use{" "}
									<code className="px-1 py-0.5 bg-[var(--background)] rounded">
										FlatList
									</code>{" "}
									instead of ScrollView for long verse lists
								</li>
								<li>• Memoize Hebrew text components to avoid re-renders</li>
								<li>• Lazy-load bottom sheets and modals</li>
								<li>
									• Compress images and use vector icons (SVG →
									react-native-svg)
								</li>
							</ul>
						</div>

						<div>
							<h4 className="font-semibold mb-2">Platform Differences</h4>
							<p>
								iOS uses shadows (shadowColor, shadowOpacity) while Android uses
								elevation. Create platform-specific styles using{" "}
								<code className="px-1 py-0.5 bg-[var(--background)] rounded">
									Platform.select()
								</code>
								.
							</p>
						</div>

						<div>
							<h4 className="font-semibold mb-2">Animation & Gestures</h4>
							<ul className="space-y-1 ml-4">
								<li>
									• Use{" "}
									<code className="px-1 py-0.5 bg-[var(--background)] rounded">
										react-native-reanimated
									</code>{" "}
									for smooth 60fps animations
								</li>
								<li>
									• Implement swipe gestures with{" "}
									<code className="px-1 py-0.5 bg-[var(--background)] rounded">
										react-native-gesture-handler
									</code>
								</li>
								<li>
									• Keep animations subtle and contemplative (300-400ms easing)
								</li>
							</ul>
						</div>
					</div>
				</div>

				{/* Resources */}
				<div className="border-t border-[var(--neomorph-border)] pt-8">
					<h3
						className="text-xl mb-4"
						style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
					>
						Recommended Resources
					</h3>

					<div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
						<div className="bg-[var(--muted)] p-4 rounded-xl">
							<h4 className="font-semibold mb-2">Design Guidelines</h4>
							<ul className="space-y-1 text-[var(--text-secondary)]">
								<li>• iOS Human Interface Guidelines</li>
								<li>• Material Design (Android)</li>
								<li>• React Native Paper (components)</li>
							</ul>
						</div>
						<div className="bg-[var(--muted)] p-4 rounded-xl">
							<h4 className="font-semibold mb-2">Fonts for Mobile</h4>
							<ul className="space-y-1 text-[var(--text-secondary)]">
								<li>• SBL Hebrew (biblical Hebrew)</li>
								<li>• Ezra SIL (alternative Hebrew)</li>
								<li>• SF Pro (iOS system)</li>
								<li>• Roboto (Android system)</li>
							</ul>
						</div>
						<div className="bg-[var(--muted)] p-4 rounded-xl">
							<h4 className="font-semibold mb-2">Libraries</h4>
							<ul className="space-y-1 text-[var(--text-secondary)]">
								<li>• react-native-safe-area-context</li>
								<li>• react-navigation (navigation)</li>
								<li>• @gorhom/bottom-sheet</li>
								<li>• react-native-svg (icons)</li>
							</ul>
						</div>
						<div className="bg-[var(--muted)] p-4 rounded-xl">
							<h4 className="font-semibold mb-2">Export Plugins</h4>
							<ul className="space-y-1 text-[var(--text-secondary)]">
								<li>• Builder.io Visual Copilot</li>
								<li>• Anima</li>
								<li>• TeleportHQ</li>
								<li>• Design Tokens (plugin)</li>
							</ul>
						</div>
					</div>
				</div>
			</NeumorphCard>

			{/* App UX Flows & Navigation Structure - NEW SECTION */}
			<AppUXFlows />
		</div>
	);
}
