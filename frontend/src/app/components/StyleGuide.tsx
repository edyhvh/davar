import React from 'react';
import { GlassCard } from './GlassCard';
import { DavarLogo } from './DavarLogo';

export function StyleGuide() {
  return (
    <div className="space-y-8 p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <DavarLogo size="lg" className="justify-center mb-4" />
        <h1 className="text-4xl mb-3" style={{ fontFamily: "'Suez One', serif" }}>
          Design System Guide
        </h1>
        <p className="text-lg text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          Complete style guide for the Davar Biblical Study App
        </p>
        <div className="mt-4 text-sm text-[var(--muted-foreground)]">
          Mobile-First • Glassmorphic • Reverent Design
        </div>
      </div>

      {/* Philosophy */}
      <GlassCard className="p-8">
        <h2 className="text-2xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Design Philosophy
        </h2>
        <div className="space-y-4 text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
          <p className="text-lg">
            <strong className="text-[var(--primary)]">מינימליזם קדוש</strong> (Minimalism Kadosh)
          </p>
          <p className="text-[var(--text-secondary)]">
            Beauty in functional simplicity. No distractions. Reverent design that invites deep meditation 
            on Hebrew Scripture. Every element serves a purpose, every space has meaning.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="p-4 bg-[var(--muted)] rounded-lg">
              <div className="text-sm uppercase tracking-wider mb-2">Contemplative</div>
              <div className="text-sm text-[var(--text-secondary)]">
                Design that encourages focus and reflection
              </div>
            </div>
            <div className="p-4 bg-[var(--muted)] rounded-lg">
              <div className="text-sm uppercase tracking-wider mb-2">Premium</div>
              <div className="text-sm text-[var(--text-secondary)]">
                High-quality glassmorphism and typography
              </div>
            </div>
            <div className="p-4 bg-[var(--muted)] rounded-lg">
              <div className="text-sm uppercase tracking-wider mb-2">Accessible</div>
              <div className="text-sm text-[var(--text-secondary)]">
                RTL support, readable fonts, theme options
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Brand Identity */}
      <GlassCard className="p-8">
        <h2 className="text-2xl mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          Brand Identity
        </h2>
        <div className="space-y-6">
          <div>
            <h3 className="text-lg mb-3">Logo</h3>
            <div className="bg-gradient-to-br from-blue-50 to-teal-50 dark:from-gray-800 dark:to-gray-900 p-8 rounded-lg flex items-center justify-center">
              <DavarLogo size="lg" />
            </div>
            <p className="text-sm text-[var(--text-secondary)] mt-3">
              The logo features a stylized Phoenician Dalet (ד) letter with a blue-to-teal gradient, 
              symbolizing the opening door to ancient wisdom. Paired with Hebrew text "דבר" (Davar), 
              meaning "word" or "thing."
            </p>
          </div>

          <div>
            <h3 className="text-lg mb-3">Brand Colors</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="h-32 rounded-lg bg-gradient-to-br from-[#40C4FF] to-[#006666] mb-2 flex items-center justify-center text-white">
                  Primary Gradient
                </div>
                <div className="text-xs space-y-1">
                  <div><code>#40C4FF</code> → <code>#006666</code></div>
                  <div className="text-[var(--text-secondary)]">Light blue to deep teal</div>
                </div>
              </div>
              <div>
                <div className="h-32 rounded-lg bg-gradient-to-br from-[#006666] to-[#40C4FF] mb-2 flex items-center justify-center text-white">
                  Dark Mode Variant
                </div>
                <div className="text-xs space-y-1">
                  <div><code>#006666</code> → <code>#40C4FF</code></div>
                  <div className="text-[var(--text-secondary)]">Inverted for dark theme</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Usage Guidelines */}
      <GlassCard className="p-8">
        <h2 className="text-2xl mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          Usage Guidelines
        </h2>
        <div className="space-y-6">
          <div>
            <h3 className="text-lg mb-3">Glassmorphism Best Practices</h3>
            <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
              <li>✓ Use backdrop-blur-lg (12px) for all glass surfaces</li>
              <li>✓ Maintain consistent border opacity: 0.08 (light) / 0.1 (dark)</li>
              <li>✓ Layer glass elements over gradients for depth</li>
              <li>✓ Ensure text contrast meets WCAG AA standards</li>
              <li>✓ Use subtle shadows (lg, xl, 2xl) to establish hierarchy</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg mb-3">Typography Guidelines</h3>
            <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
              <li>✓ Hebrew text always uses Cardo with 1.85 line-height</li>
              <li>✓ Letter-spacing: 0.01em for improved readability</li>
              <li>✓ UI text uses Inter for Latin, Arimo for Hebrew</li>
              <li>✓ Minimum body text size: 16px for accessibility</li>
              <li>✓ Support dynamic text scaling (small/medium/large)</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg mb-3">Interaction Patterns</h3>
            <ul className="space-y-2 text-sm text-[var(--text-secondary)]">
              <li>✓ Hover: scale-105 for buttons, scale-102 for cards</li>
              <li>✓ Active/Press: scale-95/98 for tactile feedback</li>
              <li>✓ All transitions: 300ms duration with ease curves</li>
              <li>✓ Focus rings: 2px primary color at 50% opacity</li>
              <li>✓ Minimum touch target: 44x44px for accessibility</li>
            </ul>
          </div>

          <div>
            <h3 className="text-lg mb-3">Spacing System</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <strong>Component Padding</strong>
                <ul className="mt-2 space-y-1 text-[var(--text-secondary)]">
                  <li>Small: 12px (0.75rem)</li>
                  <li>Medium: 16px (1rem)</li>
                  <li>Large: 24px (1.5rem)</li>
                </ul>
              </div>
              <div>
                <strong>Vertical Rhythm</strong>
                <ul className="mt-2 space-y-1 text-[var(--text-secondary)]">
                  <li>Tight: 8px (0.5rem)</li>
                  <li>Normal: 16px (1rem)</li>
                  <li>Relaxed: 24px (1.5rem)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Component Anatomy */}
      <GlassCard className="p-8">
        <h2 className="text-2xl mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          Component Anatomy
        </h2>
        
        <div className="space-y-8">
          {/* Verse Display */}
          <div>
            <h3 className="text-lg mb-4">Verse Display Component</h3>
            <div className="bg-[var(--muted)] p-6 rounded-lg">
              <div className="space-y-4 text-sm">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Verse Reference</strong>: 14px Inter, secondary color, centered
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Hebrew Text</strong>: 24px Cardo, RTL, primary color, 1.85 line-height
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Translation</strong>: 16px Inter, secondary color, centered
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Qumran Variant</strong> (optional): 22px DeadSeaScrolls, RTL, 80% opacity
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Word Card */}
          <div>
            <h3 className="text-lg mb-4">Word Card Component</h3>
            <div className="bg-[var(--muted)] p-6 rounded-lg">
              <div className="space-y-4 text-sm">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Word Display</strong>: 48px Cardo, RTL, centered, primary color
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Meanings List</strong>: 16px Inter, bulleted, secondary color
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Root Section</strong>: 20px Cardo, RTL, bordered top
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-[var(--primary)] rounded-full mt-2" />
                  <div>
                    <strong>Instance Cards</strong>: 3-column grid, glass cards, tappable
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Responsive Behavior */}
      <GlassCard className="p-8">
        <h2 className="text-2xl mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          Responsive Design
        </h2>
        <div className="space-y-4 text-sm">
          <div>
            <strong className="text-base">Mobile Portrait (Primary)</strong>
            <p className="text-[var(--text-secondary)] mt-2">
              Max-width: 448px (28rem). All components optimized for portrait iPhone/Android.
              This is the primary and recommended viewport for the application.
            </p>
          </div>
          <div>
            <strong className="text-base">Tablet & Desktop</strong>
            <p className="text-[var(--text-secondary)] mt-2">
              Content remains centered in a mobile-width container with shadow for card-like 
              appearance. Background extends to fill viewport.
            </p>
          </div>
          <div>
            <strong className="text-base">Font Scaling</strong>
            <p className="text-[var(--text-secondary)] mt-2">
              Users can choose small/medium/large font sizes. All components adapt proportionally.
              Default base font size: 16px.
            </p>
          </div>
        </div>
      </GlassCard>

      {/* Accessibility */}
      <GlassCard className="p-8">
        <h2 className="text-2xl mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          Accessibility Standards
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="p-4 bg-[var(--muted)] rounded-lg">
            <strong>WCAG AA Compliant</strong>
            <ul className="mt-2 space-y-1 text-[var(--text-secondary)]">
              <li>✓ 4.5:1 contrast ratio minimum</li>
              <li>✓ Focusable interactive elements</li>
              <li>✓ Keyboard navigation support</li>
            </ul>
          </div>
          <div className="p-4 bg-[var(--muted)] rounded-lg">
            <strong>Screen Reader Friendly</strong>
            <ul className="mt-2 space-y-1 text-[var(--text-secondary)]">
              <li>✓ Semantic HTML structure</li>
              <li>✓ ARIA labels on icons</li>
              <li>✓ Meaningful alt text</li>
            </ul>
          </div>
          <div className="p-4 bg-[var(--muted)] rounded-lg">
            <strong>Motor Accessibility</strong>
            <ul className="mt-2 space-y-1 text-[var(--text-secondary)]">
              <li>✓ 44x44px minimum touch targets</li>
              <li>✓ Adequate spacing between buttons</li>
              <li>✓ Large, clear tap areas</li>
            </ul>
          </div>
          <div className="p-4 bg-[var(--muted)] rounded-lg">
            <strong>Internationalization</strong>
            <ul className="mt-2 space-y-1 text-[var(--text-secondary)]">
              <li>✓ RTL support for Hebrew</li>
              <li>✓ Multi-language UI (EN/ES)</li>
              <li>✓ Unicode text rendering</li>
            </ul>
          </div>
        </div>
      </GlassCard>

      {/* Implementation Notes */}
      <GlassCard className="p-8">
        <h2 className="text-2xl mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
          Implementation Notes
        </h2>
        <div className="space-y-4 text-sm">
          <div>
            <strong className="text-base">Technology Stack</strong>
            <p className="text-[var(--text-secondary)] mt-2">
              Built with React, Tailwind CSS v4, and TypeScript. Uses CSS custom properties 
              for theming. All fonts loaded via Google Fonts CDN.
            </p>
          </div>
          <div>
            <strong className="text-base">Browser Support</strong>
            <p className="text-[var(--text-secondary)] mt-2">
              Modern browsers with backdrop-filter support (Chrome 76+, Safari 14+, Firefox 103+).
              Graceful degradation for older browsers with solid backgrounds.
            </p>
          </div>
          <div>
            <strong className="text-base">Performance</strong>
            <p className="text-[var(--text-secondary)] mt-2">
              Optimized for mobile devices. Lazy loading for heavy components. CSS animations 
              use transform and opacity for GPU acceleration.
            </p>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}
