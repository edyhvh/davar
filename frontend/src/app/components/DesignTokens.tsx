import React from 'react';
import { GlassCard } from './GlassCard';

export function DesignTokens() {
  return (
    <div className="space-y-8 p-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl mb-2" style={{ fontFamily: "'Suez One', serif" }}>
          Davar Design System
        </h1>
        <p className="text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          Complete design tokens and component library
        </p>
      </div>

      {/* Color Tokens */}
      <GlassCard className="p-6">
        <h2 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Color Tokens
        </h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Primary Gradient
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <div className="h-20 rounded-lg bg-[#0038B8] mb-2" />
                <code className="text-xs">#0038B8</code>
                <p className="text-xs text-[var(--text-secondary)]">Primary Base</p>
              </div>
              <div>
                <div className="h-20 rounded-lg bg-[#002B80] mb-2" />
                <code className="text-xs">#002B80</code>
                <p className="text-xs text-[var(--text-secondary)]">Primary Dark</p>
              </div>
              <div>
                <div className="h-20 rounded-lg bg-[#001F59] mb-2" />
                <code className="text-xs">#001F59</code>
                <p className="text-xs text-[var(--text-secondary)]">Primary Deep</p>
              </div>
            </div>
            <div className="mt-4">
              <div className="h-20 rounded-lg mb-2" style={{ background: 'linear-gradient(135deg, #0038B8 0%, #002B80 50%, #001F59 100%)' }} />
              <code className="text-xs">linear-gradient(135deg, #0038B8, #002B80, #001F59)</code>
              <p className="text-xs text-[var(--text-secondary)]">Tekhelet Gradient</p>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Light Theme
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="h-16 rounded-lg bg-[#faf6f0] border border-gray-300 mb-2" />
                <code className="text-xs">#faf6f0</code>
                <p className="text-xs text-[var(--text-secondary)]">Background</p>
              </div>
              <div>
                <div className="h-16 rounded-lg bg-white/95 border border-gray-300 mb-2" />
                <code className="text-xs">rgba(255,255,255,0.95)</code>
                <p className="text-xs text-[var(--text-secondary)]">Glass Surface</p>
              </div>
              <div>
                <div className="h-16 rounded-lg bg-black mb-2" />
                <code className="text-xs">#000000</code>
                <p className="text-xs text-[var(--text-secondary)]">Text Primary</p>
              </div>
              <div>
                <div className="h-16 rounded-lg bg-[#333333] mb-2" />
                <code className="text-xs">#333333</code>
                <p className="text-xs text-[var(--text-secondary)]">Text Secondary</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Dark Theme
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="h-16 rounded-lg bg-[#1a1a1a] border border-gray-700 mb-2" />
                <code className="text-xs">#1a1a1a</code>
                <p className="text-xs text-[var(--text-secondary)]">Background</p>
              </div>
              <div>
                <div className="h-16 rounded-lg" style={{ backgroundColor: 'rgba(30,30,30,0.95)' }} />
                <code className="text-xs">rgba(30,30,30,0.95)</code>
                <p className="text-xs text-[var(--text-secondary)]">Glass Surface</p>
              </div>
              <div>
                <div className="h-16 rounded-lg bg-white mb-2" />
                <code className="text-xs">#ffffff</code>
                <p className="text-xs text-[var(--text-secondary)]">Text Primary</p>
              </div>
              <div>
                <div className="h-16 rounded-lg bg-[#cccccc] mb-2" />
                <code className="text-xs">#cccccc</code>
                <p className="text-xs text-[var(--text-secondary)]">Text Secondary</p>
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Typography Tokens */}
      <GlassCard className="p-6">
        <h2 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Typography Tokens
        </h2>
        
        <div className="space-y-6">
          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Bible Hebrew - Cardo
            </h3>
            <div className="space-y-2">
              <div style={{ fontFamily: "'Cardo', serif", fontSize: '24px', lineHeight: 1.85, letterSpacing: '0.01em', direction: 'rtl' }}>
                בְּרֵאשִׁית בָּרָא אֱלֹהִים
              </div>
              <code className="text-xs">24px / 1.85 line-height / 0.01em letter-spacing</code>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Qumran Variants - DeadSeaScrolls-Regular (simulated)
            </h3>
            <div className="space-y-2">
              <div style={{ fontFamily: "'DeadSeaScrolls-Regular', 'Cardo', serif", fontSize: '22px', lineHeight: 1.85, direction: 'rtl' }}>
                בְּרֵאשִׁית בָּרָא אֱלֹהִים
              </div>
              <code className="text-xs">22px / 1.85 line-height</code>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              UI Hebrew - Arimo
            </h3>
            <div className="space-y-2">
              <div style={{ fontFamily: "'Arimo', sans-serif", fontSize: '16px', direction: 'rtl' }}>
                דבר - אפליקציה ללימוד תנך
              </div>
              <code className="text-xs">14-18px / Medium weight</code>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              UI Latin - Inter
            </h3>
            <div className="space-y-2">
              <div style={{ fontFamily: "'Inter', sans-serif", fontSize: '16px' }}>
                Minimalism kadosh - beauty in functional simplicity
              </div>
              <code className="text-xs">14-18px / Regular & Medium weights</code>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Logo - Suez One
            </h3>
            <div className="space-y-2">
              <div style={{ fontFamily: "'Suez One', serif", fontSize: '24px' }}>
                דבר Davar
              </div>
              <code className="text-xs">24-36px / Bold serif alternative</code>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Spacing Tokens */}
      <GlassCard className="p-6">
        <h2 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Spacing & Layout Tokens
        </h2>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Border Radius
            </h3>
            <div className="flex gap-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-[var(--primary)] rounded-lg mb-2" />
                <code className="text-xs">12px (lg)</code>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-[var(--primary)] rounded-xl mb-2" />
                <code className="text-xs">16px (xl)</code>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-[var(--primary)] rounded-3xl mb-2" />
                <code className="text-xs">24px (3xl)</code>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Container
            </h3>
            <p className="text-sm">
              Max-width: 448px (28rem) - Mobile phone portrait orientation
            </p>
          </div>
        </div>
      </GlassCard>

      {/* Effects Tokens */}
      <GlassCard className="p-6">
        <h2 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Glassmorphism Effects
        </h2>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Light Theme Glass
            </h3>
            <div className="relative h-32 rounded-lg overflow-hidden bg-gradient-to-br from-blue-100 to-teal-100">
              <div className="absolute inset-4 bg-white/95 backdrop-blur-lg border border-black/[0.08] rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-sm">backdrop-blur-lg + rgba(255,255,255,0.95)</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Dark Theme Glass
            </h3>
            <div className="relative h-32 rounded-lg overflow-hidden bg-gradient-to-br from-gray-800 to-gray-900">
              <div className="absolute inset-4 backdrop-blur-lg border border-white/10 rounded-xl flex items-center justify-center shadow-lg" style={{ backgroundColor: 'rgba(30,30,30,0.95)' }}>
                <span className="text-sm text-white">backdrop-blur-lg + rgba(30,30,30,0.95)</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Shadow Styles
            </h3>
            <div className="space-y-3">
              <div className="p-4 bg-[var(--glass-surface)] rounded-lg shadow-md">
                shadow-md - Default cards
              </div>
              <div className="p-4 bg-[var(--glass-surface)] rounded-lg shadow-lg">
                shadow-lg - Glass cards
              </div>
              <div className="p-4 bg-[var(--glass-surface)] rounded-lg shadow-xl">
                shadow-xl - Elevated surfaces
              </div>
              <div className="p-4 bg-[var(--glass-surface)] rounded-lg shadow-2xl">
                shadow-2xl - Modals and sheets
              </div>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Interaction States */}
      <GlassCard className="p-6">
        <h2 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Interaction States
        </h2>
        
        <div className="space-y-4">
          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Hover Effects
            </h3>
            <p className="text-sm mb-2">scale-102 / scale-105 + shadow increase</p>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Active/Press States
            </h3>
            <p className="text-sm mb-2">scale-95 / scale-98</p>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Transitions
            </h3>
            <p className="text-sm mb-2">duration-300 (300ms) - Standard interactions</p>
          </div>

          <div>
            <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)] mb-3">
              Focus Ring
            </h3>
            <input 
              type="text" 
              placeholder="Focus me"
              className="w-full px-4 py-2 bg-[var(--input-background)] border border-[var(--glass-border)] rounded-lg outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
            />
          </div>
        </div>
      </GlassCard>

      {/* Accessibility */}
      <GlassCard className="p-6">
        <h2 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Accessibility Features
        </h2>
        
        <ul className="space-y-2 text-sm">
          <li>✓ Font size scaling support (small/medium/large)</li>
          <li>✓ High contrast mode compatible</li>
          <li>✓ RTL (Right-to-Left) support for Hebrew</li>
          <li>✓ Keyboard navigation friendly</li>
          <li>✓ Screen reader labels (aria-label)</li>
          <li>✓ Focus indicators on interactive elements</li>
          <li>✓ Minimum touch target size: 44x44px</li>
        </ul>
      </GlassCard>

      {/* Export Format */}
      <GlassCard className="p-6">
        <h2 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
          Token Export Format
        </h2>
        
        <div className="bg-black/5 dark:bg-white/5 rounded-lg p-4 overflow-x-auto">
          <pre className="text-xs">
{`{
  "colors": {
    "tekhelet": {
      "base": "#0038B8",
      "dark": "#002B80",
      "deep": "#001F59",
      "gradient": "linear-gradient(135deg, #0038B8 0%, #002B80 50%, #001F59 100%)"
    },
    "light": {
      "background": "#f5f5f7",
      "surface": "rgba(255,255,255,0.8)",
      "text": {
        "primary": "#1d1d1f",
        "secondary": "#6e6e73"
      }
    },
    "dark": {
      "background": "#1c1c1e",
      "surface": "rgba(28,28,30,0.8)",
      "text": {
        "primary": "#f5f5f7",
        "secondary": "#aeaeb2"
      }
    }
  },
  "typography": {
    "bible-hebrew": {
      "family": "Cardo",
      "size": "42px",
      "lineHeight": 2,
      "letterSpacing": "0.01em"
    },
    "ui-latin": {
      "family": "Inter",
      "size": "16px"
    }
  },
  "effects": {
    "glass": {
      "backdrop": "blur(12px)",
      "border": "rgba(0,0,0,0.08)",
      "shadow": "lg"
    }
  }
}`}
          </pre>
        </div>
      </GlassCard>
    </div>
  );
}