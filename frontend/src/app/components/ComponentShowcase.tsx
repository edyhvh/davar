import React from 'react';
import { GlassButton } from './GlassButton';
import { GlassCard } from './GlassCard';
import { DavarLogo } from './DavarLogo';

export function ComponentShowcase() {
  return (
    <div className="space-y-8 p-6">
      <h2 className="text-2xl text-center mb-6" style={{ fontFamily: "'Inter', sans-serif" }}>
        Component Library
      </h2>

      {/* Logo Variants */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Logo Variants
        </h3>
        <div className="flex items-center gap-6 flex-wrap">
          <DavarLogo size="sm" theme="light" />
          <DavarLogo size="md" theme="light" />
          <DavarLogo size="lg" theme="light" />
        </div>
      </GlassCard>

      {/* Buttons */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Button Variants & States
        </h3>
        <div className="space-y-4">
          <div className="flex gap-3 flex-wrap">
            <GlassButton variant="primary" size="sm">
              Small Primary
            </GlassButton>
            <GlassButton variant="primary" size="md">
              Medium Primary
            </GlassButton>
            <GlassButton variant="primary" size="lg">
              Large Primary
            </GlassButton>
          </div>
          <div className="flex gap-3 flex-wrap">
            <GlassButton variant="secondary" size="sm">
              Small Secondary
            </GlassButton>
            <GlassButton variant="secondary" size="md">
              Medium Secondary
            </GlassButton>
            <GlassButton variant="secondary" size="lg">
              Large Secondary
            </GlassButton>
          </div>
          <div className="flex gap-3 flex-wrap">
            <GlassButton variant="primary" size="md" disabled>
              Disabled Primary
            </GlassButton>
            <GlassButton variant="secondary" size="md" disabled>
              Disabled Secondary
            </GlassButton>
          </div>
        </div>
      </GlassCard>

      {/* Glass Cards */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Glass Card Variants
        </h3>
        <div className="space-y-3">
          <GlassCard className="p-4">
            <p className="text-sm">Standard Glass Card</p>
          </GlassCard>
          <GlassCard className="p-4" hoverable>
            <p className="text-sm">Hoverable Glass Card (try hovering)</p>
          </GlassCard>
        </div>
      </GlassCard>

      {/* Form Elements */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Form Elements
        </h3>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Text Input"
            className="w-full px-4 py-2 bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-lg outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
          />
          <select
            className="w-full px-4 py-2 bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-lg outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
          >
            <option>Select Option 1</option>
            <option>Select Option 2</option>
            <option>Select Option 3</option>
          </select>
          <textarea
            placeholder="Textarea"
            rows={3}
            className="w-full px-4 py-2 bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-lg outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all resize-none"
          />
        </div>
      </GlassCard>

      {/* Gradient Backgrounds */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Gradient Backgrounds
        </h3>
        <div className="space-y-3">
          <div className="h-24 rounded-lg bg-gradient-to-r from-[var(--accent-from)] to-[var(--accent-to)] flex items-center justify-center text-white">
            Horizontal Gradient
          </div>
          <div className="h-24 rounded-lg bg-gradient-to-br from-[var(--accent-from)] to-[var(--accent-to)] flex items-center justify-center text-white">
            Diagonal Gradient
          </div>
          <div className="h-24 rounded-lg bg-gradient-to-b from-[var(--accent-from)] to-[var(--accent-to)] flex items-center justify-center text-white">
            Vertical Gradient
          </div>
        </div>
      </GlassCard>

      {/* Layered Glass Effects */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Layered Glassmorphism
        </h3>
        <div className="relative h-48 rounded-xl overflow-hidden">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-400 via-teal-500 to-green-400" />
          
          {/* First glass layer */}
          <div className="absolute inset-4 bg-[var(--glass-surface)] backdrop-blur-lg border border-[var(--glass-border)] rounded-xl p-4">
            <p className="text-sm mb-3">First glass layer</p>
            
            {/* Second glass layer */}
            <div className="bg-[var(--glass-surface)] backdrop-blur-lg border border-[var(--glass-border)] rounded-lg p-3">
              <p className="text-xs">Nested glass layer</p>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Animation Examples */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Animation & Transitions
        </h3>
        <div className="space-y-3">
          <div className="p-4 bg-[var(--glass-surface)] rounded-lg border border-[var(--glass-border)] hover:scale-105 transition-transform duration-300 cursor-pointer">
            Hover to scale up (105%)
          </div>
          <div className="p-4 bg-[var(--glass-surface)] rounded-lg border border-[var(--glass-border)] hover:shadow-xl transition-shadow duration-300 cursor-pointer">
            Hover to increase shadow
          </div>
          <div className="p-4 bg-gradient-to-r from-[var(--accent-from)] to-[var(--accent-to)] rounded-lg text-white hover:from-[var(--accent-to)] hover:to-[var(--accent-from)] transition-all duration-500 cursor-pointer">
            Hover to reverse gradient
          </div>
        </div>
      </GlassCard>

      {/* Typography Hierarchy */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Typography Hierarchy
        </h3>
        <div className="space-y-3">
          <h1 style={{ fontFamily: "'Cardo', serif", fontSize: '32px' }}>
            Heading 1 - Cardo 32px
          </h1>
          <h2 style={{ fontFamily: "'Cardo', serif", fontSize: '28px' }}>
            Heading 2 - Cardo 28px
          </h2>
          <h3 style={{ fontFamily: "'Inter', sans-serif", fontSize: '24px' }}>
            Heading 3 - Inter 24px
          </h3>
          <p style={{ fontFamily: "'Inter', sans-serif", fontSize: '16px' }}>
            Body text - Inter 16px. This is the standard body text used throughout the application for readable content.
          </p>
          <p className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
            Small text - Inter 14px. Used for secondary information and metadata.
          </p>
          <p className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
            Extra small text - Inter 12px. Used for captions and helper text.
          </p>
        </div>
      </GlassCard>

      {/* Color Swatches */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Interactive Color Swatches
        </h3>
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-2">
            <div className="h-20 rounded-lg bg-[var(--primary)] hover:scale-105 transition-transform cursor-pointer" />
            <p className="text-xs text-center">Primary</p>
          </div>
          <div className="space-y-2">
            <div className="h-20 rounded-lg bg-[var(--background)] border border-[var(--glass-border)] hover:scale-105 transition-transform cursor-pointer" />
            <p className="text-xs text-center">Background</p>
          </div>
          <div className="space-y-2">
            <div className="h-20 rounded-lg bg-[var(--foreground)] hover:scale-105 transition-transform cursor-pointer" />
            <p className="text-xs text-center">Foreground</p>
          </div>
        </div>
      </GlassCard>

      {/* Spacing Guide */}
      <GlassCard className="p-6 space-y-4">
        <h3 className="text-sm uppercase tracking-wider text-[var(--text-secondary)]">
          Spacing Scale
        </h3>
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-16 h-2 bg-[var(--primary)] rounded" />
            <span className="text-xs">2px</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-16 h-3 bg-[var(--primary)] rounded" />
            <span className="text-xs">12px (0.75rem)</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-16 h-4 bg-[var(--primary)] rounded" />
            <span className="text-xs">16px (1rem)</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-16 h-6 bg-[var(--primary)] rounded" />
            <span className="text-xs">24px (1.5rem)</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-16 h-8 bg-[var(--primary)] rounded" />
            <span className="text-xs">32px (2rem)</span>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}