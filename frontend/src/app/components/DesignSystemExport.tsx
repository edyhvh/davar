import React from 'react';
import { DavarLogo } from './DavarLogo';
import { GlassButton } from './GlassButton';
import { GlassCard } from './GlassCard';
import { Globe, Book, Search, Settings, Sun, Moon, X } from 'lucide-react';

interface DesignSystemExportProps {
  theme: 'light' | 'dark';
  onThemeChange: (theme: 'light' | 'dark') => void;
  onClose?: () => void;
}

export function DesignSystemExport({ theme, onThemeChange, onClose }: DesignSystemExportProps) {
  const colorTokens = {
    light: {
      primary: [
        { name: 'Primary Base', value: '#2E347A', desc: 'Main earthy tekhelet blue' },
        { name: 'Primary Dark', value: '#252B6B', desc: 'Pressed states/gradient mid' },
        { name: 'Primary Darker', value: '#1C2254', desc: 'Shadows/gradient end' },
        { name: 'Primary Light', value: '#5C6199', desc: 'Inactive/subtle highlights' },
      ],
      copper: [
        { name: 'Copper Light', value: '#B87333', desc: 'Onboarding hint' },
        { name: 'Copper Base', value: '#CD7F32', desc: 'Hint accent' },
      ],
      neutral: [
        { name: 'Background', value: '#FDFDF9', desc: 'Warm ivory page background' },
        { name: 'Surface', value: '#FFFFFF', desc: 'Card surfaces' },
        { name: 'Surface Elevated', value: '#F5F4F0', desc: 'Raised surfaces' },
        { name: 'Foreground', value: '#1a1a1a', desc: 'Primary text' },
        { name: 'Muted Foreground', value: '#6b6b6b', desc: 'Secondary text' },
        { name: 'Border', value: 'rgba(0, 0, 0, 0.08)', desc: 'Dividers' },
      ],
      glass: [
        { name: 'Glass Surface', value: 'rgba(255, 255, 255, 0.25)', desc: 'Card background' },
        { name: 'Glass Surface Elevated', value: 'rgba(255, 255, 255, 0.35)', desc: 'Hover state' },
        { name: 'Glass Border', value: 'rgba(255, 255, 255, 0.3)', desc: '2px border' },
        { name: 'Glass Shadow', value: 'rgba(0, 0, 0, 0.1)', desc: 'Drop shadow' },
        { name: 'Glass Highlight', value: 'rgba(255, 255, 255, 0.5)', desc: 'Inner glow' },
      ],
    },
    dark: {
      primary: [
        { name: 'Primary Base', value: '#2E347A', desc: 'Main earthy tekhelet blue' },
        { name: 'Primary Dark', value: '#252B6B', desc: 'Pressed states/gradient mid' },
        { name: 'Primary Darker', value: '#1C2254', desc: 'Shadows/gradient end' },
        { name: 'Primary Light', value: '#5C6199', desc: 'Inactive/subtle highlights' },
      ],
      copper: [
        { name: 'Copper Light', value: '#B87333', desc: 'Onboarding hint' },
        { name: 'Copper Base', value: '#CD7F32', desc: 'Hint accent' },
      ],
      neutral: [
        { name: 'Background', value: '#0F0E12', desc: 'Warm deep charcoal' },
        { name: 'Surface', value: '#17161A', desc: 'Elevated surface' },
        { name: 'Surface Elevated', value: '#1F1E23', desc: 'Raised surfaces' },
        { name: 'Foreground', value: '#ebdbb2', desc: 'Warm cream text' },
        { name: 'Muted Foreground', value: '#a89984', desc: 'Secondary text' },
        { name: 'Border', value: 'rgba(255, 255, 255, 0.12)', desc: 'Dividers' },
      ],
      glass: [
        { name: 'Glass Surface', value: 'rgba(23, 22, 26, 0.92)', desc: 'Card background' },
        { name: 'Glass Surface Elevated', value: 'rgba(31, 30, 35, 0.95)', desc: 'Hover state' },
        { name: 'Glass Border', value: 'rgba(60, 60, 80, 0.5)', desc: '2px border' },
        { name: 'Glass Shadow', value: 'rgba(0, 0, 0, 0.5)', desc: 'Drop shadow' },
        { name: 'Glass Highlight', value: 'rgba(80, 80, 90, 0.15)', desc: 'Inner glow' },
      ],
    },
  };

  const typography = [
    {
      name: 'Hebrew Scripture',
      family: 'Cardo',
      weight: '400',
      size: '32px',
      lineHeight: '1.8',
      usage: 'Main Hebrew text',
      example: 'בְּרֵאשִׁית בָּרָא אֱלֹהִים',
      isHebrew: true,
    },
    {
      name: 'UI Hebrew',
      family: 'Arimo',
      weight: '400',
      size: '16px',
      lineHeight: '1.5',
      usage: 'Hebrew UI labels, book names',
      example: 'בראשית',
      isHebrew: true,
    },
    {
      name: 'Latin UI',
      family: 'Inter',
      weight: '400, 500, 600',
      size: '14-16px',
      lineHeight: '1.5',
      usage: 'English UI, settings, labels',
      example: 'The quick brown fox',
      isHebrew: false,
    },
    {
      name: 'Logo',
      family: 'Suez One',
      weight: '400',
      size: 'Variable',
      lineHeight: '1.2',
      usage: 'Brand logo text',
      example: 'Davar',
      isHebrew: false,
    },
  ];

  const spacing = [
    { token: '1', value: '4px', usage: 'Tight spacing' },
    { token: '2', value: '8px', usage: 'Default gap' },
    { token: '3', value: '12px', usage: 'Small padding' },
    { token: '4', value: '16px', usage: 'Medium padding' },
    { token: '6', value: '24px', usage: 'Large padding' },
    { token: '8', value: '32px', usage: 'Section spacing' },
    { token: '12', value: '48px', usage: 'Major sections' },
    { token: '16', value: '64px', usage: 'Page spacing' },
  ];

  const currentColors = colorTokens[theme];

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] p-8">
      <div className="max-w-7xl mx-auto space-y-16">
        
        {/* Header */}
        <header className="text-center space-y-6 py-12">
          <DavarLogo size="xl" theme={theme} className="mb-8" />
          <h1 className="text-5xl" style={{ fontFamily: "'Suez One', serif" }}>
            Davar Design System
          </h1>
          <p className="text-xl text-[var(--muted-foreground)] max-w-2xl mx-auto" style={{ fontFamily: "'Inter', sans-serif" }}>
            Minimalism Kadosh - Beauty in functional simplicity with reverent design inviting deep meditation
          </p>
          
          {/* Theme Toggle */}
          <div className="flex items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onThemeChange('light')}
              className={`flex items-center gap-2 px-6 py-3 rounded-2xl transition-all ${
                theme === 'light' 
                  ? 'bg-[var(--accent)] text-white' 
                  : 'bg-[var(--muted)] text-[var(--muted-foreground)]'
              }`}
            >
              <Sun className="w-5 h-5" />
              <span style={{ fontFamily: "'Inter', sans-serif" }}>Light</span>
            </button>
            <button
              onClick={() => onThemeChange('dark')}
              className={`flex items-center gap-2 px-6 py-3 rounded-2xl transition-all ${
                theme === 'dark' 
                  ? 'bg-[var(--accent)] text-white' 
                  : 'bg-[var(--muted)] text-[var(--muted-foreground)]'
              }`}
            >
              <Moon className="w-5 h-5" />
              <span style={{ fontFamily: "'Inter', sans-serif" }}>Dark</span>
            </button>
          </div>

          <div className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
            Version 1.0 • Mobile-First Biblical Study App
          </div>
        </header>

        {/* Design Principles */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Design Principles
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GlassCard className="p-6 space-y-3">
              <h3 className="text-xl" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Minimalism Kadosh
              </h3>
              <p className="text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                Sacred minimalism - beauty through functional simplicity with no distractions
              </p>
            </GlassCard>
            <GlassCard className="p-6 space-y-3">
              <h3 className="text-xl" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Reverent Aesthetics
              </h3>
              <p className="text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                Warm charcoal backgrounds, contemplative spacing, premium glassmorphism
              </p>
            </GlassCard>
            <GlassCard className="p-6 space-y-3">
              <h3 className="text-xl" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Hebrew-First
              </h3>
              <p className="text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                Proper RTL support, ample line height, warm cream text on dark mode
              </p>
            </GlassCard>
          </div>
        </section>

        {/* Color System */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Color System - {theme === 'light' ? 'Light Theme' : 'Dark Theme'}
          </h2>

          {/* Primary Colors */}
          <div className="space-y-6 mb-8">
            <h3 className="text-xl text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Primary - Earthy Tekhelet (Warm Indigo Blue)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {currentColors.primary.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2 border-[var(--border)]"
                    style={{ backgroundColor: color.value }}
                  />
                  <div>
                    <div className="font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Copper Colors */}
          <div className="space-y-6 mb-8">
            <h3 className="text-xl text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Copper - Onboarding Hints
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentColors.copper.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2 border-[var(--border)]"
                    style={{ backgroundColor: color.value }}
                  />
                  <div>
                    <div className="font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Neutral Colors */}
          <div className="space-y-6 mb-8">
            <h3 className="text-xl text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Neutral Colors
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {currentColors.neutral.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2 border-[var(--border)]"
                    style={{ backgroundColor: color.value }}
                  />
                  <div>
                    <div className="font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Glassmorphism Colors */}
          <div className="space-y-6">
            <h3 className="text-xl text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Glassmorphism Tokens
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {currentColors.glass.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2"
                    style={{ 
                      backgroundColor: color.value,
                      borderColor: color.name.includes('Border') ? color.value : 'var(--border)',
                    }}
                  />
                  <div>
                    <div className="font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Typography */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Typography
          </h2>
          <div className="space-y-6">
            {typography.map((type) => (
              <GlassCard key={type.name} className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                      {type.name}
                    </h3>
                    <div className="space-y-2 text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      <div><strong>Family:</strong> {type.family}</div>
                      <div><strong>Weight:</strong> {type.weight}</div>
                      <div><strong>Size:</strong> {type.size}</div>
                      <div><strong>Line Height:</strong> {type.lineHeight}</div>
                      <div><strong>Usage:</strong> {type.usage}</div>
                    </div>
                  </div>
                  <div className="flex items-center justify-center">
                    <div 
                      className="text-3xl"
                      style={{ 
                        fontFamily: `'${type.family}', ${type.family === 'Inter' ? 'sans-serif' : 'serif'}`,
                        direction: type.isHebrew ? 'rtl' : 'ltr',
                      }}
                    >
                      {type.example}
                    </div>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        </section>

        {/* Spacing System */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Spacing System
          </h2>
          <GlassCard className="p-6">
            <div className="space-y-4">
              {spacing.map((space) => (
                <div key={space.token} className="flex items-center gap-6">
                  <div className="w-20 text-sm font-mono text-[var(--muted-foreground)]">
                    {space.value}
                  </div>
                  <div 
                    className="h-8 bg-[var(--accent)] rounded"
                    style={{ width: space.value }}
                  />
                  <div className="flex-1 text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                    {space.usage}
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </section>

        {/* Glassmorphism Specs */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Glassmorphism - "Liquid Glass" Specs
          </h2>
          <GlassCard className="p-8">
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                    Layer Structure
                  </h3>
                  <div className="space-y-3 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                    <div className="flex justify-between">
                      <span className="text-[var(--muted-foreground)]">Backdrop Blur:</span>
                      <span className="font-semibold">45px</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[var(--muted-foreground)]">Border Width:</span>
                      <span className="font-semibold">2px</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[var(--muted-foreground)]">Border Radius:</span>
                      <span className="font-semibold">16px / 24px</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[var(--muted-foreground)]">Background Opacity:</span>
                      <span className="font-semibold">25-35%</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                    Shadow System
                  </h3>
                  <div className="space-y-3 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                    <div>
                      <div className="text-[var(--muted-foreground)] mb-1">Outer Shadow:</div>
                      <div className="font-mono text-xs">0 8px 32px rgba(0,0,0,0.1)</div>
                      <div className="font-mono text-xs">0 4px 16px rgba(0,0,0,0.08)</div>
                    </div>
                    <div>
                      <div className="text-[var(--muted-foreground)] mb-1">Inner Highlight:</div>
                      <div className="font-mono text-xs">inset 0 1px 0 rgba(255,255,255,0.5)</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Example */}
              <div className="mt-8 pt-8 border-t border-[var(--border)]">
                <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                  Live Example
                </h3>
                <div className="flex items-center justify-center p-12 bg-gradient-to-br from-blue-50 to-teal-50 dark:from-gray-800 dark:to-gray-900 rounded-2xl">
                  <GlassCard className="p-8 max-w-sm">
                    <h4 className="text-xl mb-3" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                      Glass Card Example
                    </h4>
                    <p className="text-[var(--muted-foreground)] mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
                      45px backdrop blur with 2px border, inner highlight, and layered shadows.
                    </p>
                    <GlassButton variant="primary">
                      Primary Action
                    </GlassButton>
                  </GlassCard>
                </div>
              </div>
            </div>
          </GlassCard>
        </section>

        {/* Components */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Components
          </h2>
          
          <div className="space-y-8">
            {/* Buttons */}
            <GlassCard className="p-6">
              <h3 className="text-xl mb-6" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Glass Buttons
              </h3>
              <div className="flex flex-wrap gap-4">
                <GlassButton variant="primary">Primary</GlassButton>
                <GlassButton variant="secondary">Secondary</GlassButton>
                <GlassButton variant="outline">Outline</GlassButton>
              </div>
            </GlassCard>

            {/* Icons */}
            <GlassCard className="p-6">
              <h3 className="text-xl mb-6" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Icon System - Lucide React
              </h3>
              <div className="flex flex-wrap gap-8">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Book className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Book</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Search className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Search</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Settings className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Settings</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Globe className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Globe</span>
                </div>
              </div>
            </GlassCard>

            {/* Logo Variants */}
            <GlassCard className="p-6">
              <h3 className="text-xl mb-6" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Logo - Theme Adaptive
              </h3>
              <div className="flex items-center gap-8 flex-wrap">
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="sm" theme={theme} />
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Small (24px)</span>
                </div>
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="md" theme={theme} />
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Medium (32px)</span>
                </div>
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="lg" theme={theme} />
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Large (48px)</span>
                </div>
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="xl" theme={theme} />
                  <span className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>Extra Large (120px)</span>
                </div>
              </div>
              <div className="mt-6 pt-6 border-t border-[var(--border)]">
                <div className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  <strong>Light Mode:</strong> Tekhelet Blue (#0038B8)<br />
                  <strong>Dark Mode:</strong> Warm Cream (#ebdbb2)
                </div>
              </div>
            </GlassCard>
          </div>
        </section>

        {/* RTL Support */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            RTL Support - Hebrew Text
          </h2>
          <GlassCard className="p-8">
            <div className="space-y-8">
              <div>
                <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                  Hebrew Scripture Example
                </h3>
                <div 
                  className="text-3xl leading-relaxed text-center"
                  style={{ 
                    fontFamily: "'Cardo', serif",
                    direction: 'rtl',
                    lineHeight: '1.8',
                  }}
                >
                  בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ
                </div>
                <div className="text-center text-sm text-[var(--muted-foreground)] mt-4" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Genesis 1:1 • Cardo 32px • Line Height 1.8 • RTL
                </div>
              </div>

              <div className="pt-6 border-t border-[var(--border)]">
                <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                  RTL Implementation Notes
                </h3>
                <ul className="space-y-2 text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  <li>• Use <code className="px-2 py-1 bg-[var(--muted)] rounded">direction: rtl</code> for Hebrew text containers</li>
                  <li>• Line height 1.8 for scripture (better readability with nikud)</li>
                  <li>• Cardo font for main Hebrew text, Arimo for UI Hebrew</li>
                  <li>• Warm cream (#ebdbb2) color in dark mode for reduced eye strain</li>
                  <li>• Book names should be displayed in UPPERCASE</li>
                </ul>
              </div>
            </div>
          </GlassCard>
        </section>

        {/* Mobile Specs */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Mobile Specifications
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <GlassCard className="p-6">
              <h3 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Target Devices
              </h3>
              <div className="space-y-3 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                <div className="flex justify-between">
                  <span className="text-[var(--muted-foreground)]">iPhone 14 Pro:</span>
                  <span className="font-semibold">390 × 844px</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--muted-foreground)]">Pixel 7:</span>
                  <span className="font-semibold">412 × 915px</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--muted-foreground)]">Orientation:</span>
                  <span className="font-semibold">Portrait Only</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <h3 className="text-xl mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Design Guidelines
              </h3>
              <ul className="space-y-2 text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                <li>• Ample whitespace for contemplative feel</li>
                <li>• Centered content alignment</li>
                <li>• Touch targets minimum 44×44px</li>
                <li>• Subtle animations (avoid distractions)</li>
                <li>• Safe area padding for notches</li>
              </ul>
            </GlassCard>
          </div>
        </section>

        {/* Export Info */}
        <section className="border-t border-[var(--border)] pt-12">
          <div className="text-center space-y-4">
            <h2 className="text-2xl" style={{ fontFamily: "'Suez One', serif" }}>
              Ready to Build in Figma
            </h2>
            <p className="text-[var(--muted-foreground)] max-w-2xl mx-auto" style={{ fontFamily: "'Inter', sans-serif" }}>
              This comprehensive design system specification provides all the foundations, components, and guidelines 
              needed to recreate the Davar design in Figma. Reference this page when building your design file.
            </p>
            <div className="pt-4 text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              💡 Tip: Use Figma Variables for colors, Tokens Studio plugin for import, and create Component Variants for state management
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}