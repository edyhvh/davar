import React from 'react';
import { DavarLogo } from './DavarLogo';
import { NeumorphButton } from './NeumorphButton';
import { NeumorphCard } from './NeumorphCard';
import { Globe, Book, Search, Settings, Sun, Moon, Heart } from 'lucide-react';

interface DesignSystemExportProps {
  theme: 'light' | 'dark';
  onThemeChange: (theme: 'light' | 'dark') => void;
  onClose?: () => void;
}

export function DesignSystemExport({ theme, onThemeChange, onClose }: DesignSystemExportProps) {
  const colorTokens = {
    light: {
      accent: [
        { name: 'Accent Base', value: '#7AA0D6', desc: 'Primary interactive elements' },
        { name: 'Accent From', value: '#7AA0D6', desc: 'Gradient start' },
        { name: 'Accent To', value: '#6389BF', desc: 'Gradient end, hover base' },
        { name: 'Accent Dark', value: '#6389BF', desc: 'Hover states' },
        { name: 'Accent Deep', value: '#4C72A8', desc: 'Pressed/deep states' },
        { name: 'Accent Light', value: '#A8C8F0', desc: 'Soft fills, selected states' },
        { name: 'Accent Darker', value: '#3D5A8C', desc: 'Darker blue for donate button' },
      ],
      copper: [
        { name: 'Copper Base', value: '#B07A3C', desc: 'Main copper' },
        { name: 'Copper Highlight', value: '#C68F55', desc: 'Qumran variants highlighting' },
      ],
      neutral: [
        { name: 'Background', value: '#FDFDF9', desc: 'Warm ivory page background' },
        { name: 'Surface', value: '#FFFFFF', desc: 'Card surfaces' },
        { name: 'Surface Elevated', value: '#F8F7F3', desc: 'Raised surfaces' },
        { name: 'Text Primary', value: '#1a1a1a', desc: 'Main text + Hebrew' },
        { name: 'Text Secondary', value: '#6b6b6b', desc: 'Secondary text' },
        { name: 'Border', value: 'rgba(0, 0, 0, 0.08)', desc: 'Dividers' },
      ],
      neomorph: [
        { name: 'Neomorph BG', value: '#FDFDF9', desc: 'Button/card background' },
        { name: 'Shadow Dark', value: 'rgba(190, 190, 200, 0.4)', desc: 'Dark shadow' },
        { name: 'Shadow Light', value: 'rgba(255, 255, 255, 0.8)', desc: 'Light shadow' },
        { name: 'Border', value: 'rgba(200, 200, 220, 0.2)', desc: 'Subtle borders' },
      ],
    },
    dark: {
      accent: [
        { name: 'Accent Base', value: '#92B5E8', desc: 'Primary interactive elements' },
        { name: 'Accent From', value: '#92B5E8', desc: 'Gradient start' },
        { name: 'Accent To', value: '#7B9ED1', desc: 'Gradient end, hover base' },
        { name: 'Accent Dark', value: '#7B9ED1', desc: 'Hover states' },
        { name: 'Accent Deep', value: '#4C72A8', desc: 'Pressed/deep states' },
        { name: 'Accent Light', value: '#BCD8FF', desc: 'Soft fills, selected states' },
        { name: 'Accent Darker', value: '#3D5A8C', desc: 'Darker blue for donate button' },
      ],
      copper: [
        { name: 'Copper Base', value: '#A06C35', desc: 'Main copper - darker mode' },
        { name: 'Copper Highlight', value: '#B5814A', desc: 'Qumran variants highlighting' },
      ],
      neutral: [
        { name: 'Background', value: '#0F0E12', desc: 'Warm deep charcoal' },
        { name: 'Surface', value: '#17161A', desc: 'Elevated surface' },
        { name: 'Surface Elevated', value: '#1F1E23', desc: 'Raised surfaces' },
        { name: 'Text Primary', value: '#ebdbb2', desc: 'Warm cream text' },
        { name: 'Text Secondary', value: '#a89984', desc: 'Secondary text' },
        { name: 'Border', value: 'rgba(255, 255, 255, 0.10)', desc: 'Dividers' },
      ],
      neomorph: [
        { name: 'Neomorph BG', value: '#17161A', desc: 'Button/card background' },
        { name: 'Shadow Dark', value: 'rgba(0, 0, 0, 0.5)', desc: 'Dark shadow' },
        { name: 'Shadow Light', value: 'rgba(40, 40, 50, 0.3)', desc: 'Light shadow' },
        { name: 'Border', value: 'rgba(70, 80, 110, 0.25)', desc: 'Subtle borders' },
      ],
    },
  };

  const typography = [
    {
      name: 'Hebrew Scripture',
      family: 'Cardo',
      weight: '400',
      size: '32-42px',
      lineHeight: '1.8-2.0',
      usage: 'Main Hebrew text',
      example: 'בְּרֵאשִׁית בָּרָא אֱלֹהִים',
      isHebrew: true,
    },
    {
      name: 'UI Hebrew',
      family: 'Arimo',
      weight: '400',
      size: '14-16px',
      lineHeight: '1.5',
      usage: 'Hebrew UI labels, book names',
      example: 'בראשית',
      isHebrew: true,
    },
    {
      name: 'Latin UI',
      family: 'Inter',
      weight: '400, 500, 600',
      size: '14-18px',
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
          <p className="text-xl text-[var(--text-secondary)] max-w-2xl mx-auto" style={{ fontFamily: "'Inter', sans-serif" }}>
            Kadosh Minimalism - Beauty in functional simplicity with reverent design inviting deep meditation
          </p>
          
          {/* Theme Toggle */}
          <div className="flex items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onThemeChange('light')}
              className={`flex items-center gap-2 px-6 py-3 rounded-2xl transition-all ${
                theme === 'light' 
                  ? 'bg-gradient-to-br from-[var(--accent-from)] to-[var(--accent-to)] text-white' 
                  : 'bg-[var(--muted)] text-[var(--text-secondary)]'
              }`}
            >
              <Sun className="w-5 h-5" />
              <span style={{ fontFamily: "'Inter', sans-serif" }}>Light</span>
            </button>
            <button
              onClick={() => onThemeChange('dark')}
              className={`flex items-center gap-2 px-6 py-3 rounded-2xl transition-all ${
                theme === 'dark' 
                  ? 'bg-gradient-to-br from-[var(--accent-from)] to-[var(--accent-to)] text-white' 
                  : 'bg-[var(--muted)] text-[var(--text-secondary)]'
              }`}
            >
              <Moon className="w-5 h-5" />
              <span style={{ fontFamily: "'Inter', sans-serif" }}>Dark</span>
            </button>
          </div>

          <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
            Version 2.0 • Mobile-First Biblical Study • Neumorphism Design
          </div>
        </header>

        {/* Design Principles */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Design Philosophy
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <NeumorphCard className="p-6 space-y-3">
              <h3 className="text-xl" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Kadosh Minimalism
              </h3>
              <p className="text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                Sacred minimalism - beauty through functional simplicity with no distractions
              </p>
            </NeumorphCard>
            <NeumorphCard className="p-6 space-y-3">
              <h3 className="text-xl" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Tactile Serenity
              </h3>
              <p className="text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                Neumorphic design with soft shadows creating contemplative depth and tactile interfaces
              </p>
            </NeumorphCard>
            <NeumorphCard className="p-6 space-y-3">
              <h3 className="text-xl" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Hebrew-First
              </h3>
              <p className="text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                Proper RTL support, generous line height, warm text colors for long reading comfort
              </p>
            </NeumorphCard>
          </div>
        </section>

        {/* Color System */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Color System - {theme === 'light' ? 'Light Theme' : 'Dark Theme'}
          </h2>

          {/* Accent Colors */}
          <div className="space-y-6 mb-8">
            <h3 className="text-xl text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Soft Earthy Tekhelet (Airy Pastel Blue)
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {currentColors.accent.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2 border-[var(--neomorph-border)]"
                    style={{ backgroundColor: color.value }}
                  />
                  <div>
                    <div className="font-semibold text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-xs text-[var(--text-secondary)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Copper Colors */}
          <div className="space-y-6 mb-8">
            <h3 className="text-xl text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Softened Copper (Qumran Highlighting)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentColors.copper.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2 border-[var(--neomorph-border)]"
                    style={{ backgroundColor: color.value }}
                  />
                  <div>
                    <div className="font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-sm text-[var(--text-secondary)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Neutral Colors */}
          <div className="space-y-6 mb-8">
            <h3 className="text-xl text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Neutral Colors
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {currentColors.neutral.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2 border-[var(--neomorph-border)]"
                    style={{ backgroundColor: color.value }}
                  />
                  <div>
                    <div className="font-semibold text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-xs text-[var(--text-secondary)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.desc}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Neumorphism Tokens */}
          <div className="space-y-6">
            <h3 className="text-xl text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Neumorphism Shadow Tokens
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {currentColors.neomorph.map((color) => (
                <div key={color.name} className="space-y-3">
                  <div 
                    className="h-24 rounded-2xl border-2"
                    style={{ 
                      backgroundColor: color.value,
                      borderColor: color.name.includes('Border') ? color.value : 'var(--neomorph-border)',
                    }}
                  />
                  <div>
                    <div className="font-semibold" style={{ fontFamily: "'Inter', sans-serif" }}>
                      {color.name}
                    </div>
                    <div className="text-sm text-[var(--text-secondary)] font-mono">
                      {color.value}
                    </div>
                    <div className="text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
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
              <NeumorphCard key={type.name} className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                      {type.name}
                    </h3>
                    <div className="space-y-2 text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
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
              </NeumorphCard>
            ))}
          </div>
        </section>

        {/* Neumorphism Specs */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Neumorphism - "Soft UI" Specifications
          </h2>
          <NeumorphCard className="p-8">
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                    Shadow System
                  </h3>
                  <div className="space-y-3 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                    <div className="flex justify-between">
                      <span className="text-[var(--text-secondary)]">Raised State:</span>
                      <span className="font-semibold">Dual shadows</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[var(--text-secondary)]">Pressed State:</span>
                      <span className="font-semibold">Inset shadows</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[var(--text-secondary)]">Border Radius:</span>
                      <span className="font-semibold">24-32px</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                    Implementation
                  </h3>
                  <div className="space-y-3 text-sm" style={{ fontFamily: "'Inter', sans-serif" }}>
                    <div>
                      <div className="text-[var(--text-secondary)] mb-1">Raised (Light):</div>
                      <div className="font-mono text-xs">6px 6px 12px var(--neomorph-shadow-dark)</div>
                      <div className="font-mono text-xs">-6px -6px 12px var(--neomorph-shadow-light)</div>
                    </div>
                    <div>
                      <div className="text-[var(--text-secondary)] mb-1">Pressed (Inset):</div>
                      <div className="font-mono text-xs">inset 3px 3px 6px var(--neomorph-inset-shadow-dark)</div>
                      <div className="font-mono text-xs">inset -3px -3px 6px var(--neomorph-inset-shadow-light)</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Examples */}
              <div className="mt-8 pt-8 border-t border-[var(--neomorph-border)]">
                <h3 className="text-lg mb-6" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                  Live Examples
                </h3>
                <div className="flex flex-wrap items-center gap-6">
                  <NeumorphButton>Default Button</NeumorphButton>
                  <NeumorphButton variant="primary">Primary Action</NeumorphButton>
                  <button
                    className="bg-[var(--accent-darker)] text-white px-6 py-3 rounded-full flex items-center gap-2 hover:scale-105 active:scale-95 transition-all shadow-[0_4px_16px_rgba(61,90,140,0.3)]"
                    style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}
                  >
                    <Heart className="w-4 h-4" />
                    Donate
                  </button>
                </div>
              </div>
            </div>
          </NeumorphCard>
        </section>

        {/* Components */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            Component Library
          </h2>
          
          <div className="space-y-8">
            {/* Buttons */}
            <NeumorphCard className="p-6">
              <h3 className="text-xl mb-6" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Neumorphic Buttons
              </h3>
              <div className="flex flex-wrap gap-4">
                <NeumorphButton>Default</NeumorphButton>
                <NeumorphButton variant="primary">Primary</NeumorphButton>
                <NeumorphButton variant="secondary">Secondary</NeumorphButton>
              </div>
            </NeumorphCard>

            {/* Icons */}
            <NeumorphCard className="p-6">
              <h3 className="text-xl mb-6" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Icon System - Lucide React
              </h3>
              <div className="flex flex-wrap gap-8">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Book className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Book</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Search className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Search</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Settings className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Settings</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-2xl bg-[var(--accent)]/10 flex items-center justify-center">
                    <Globe className="w-6 h-6 text-[var(--accent)]" />
                  </div>
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Globe</span>
                </div>
              </div>
            </NeumorphCard>

            {/* Logo Variants */}
            <NeumorphCard className="p-6">
              <h3 className="text-xl mb-6" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                Logo - Theme Adaptive
              </h3>
              <div className="flex items-center gap-8 flex-wrap">
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="sm" theme={theme} />
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Small</span>
                </div>
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="md" theme={theme} />
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Medium</span>
                </div>
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="lg" theme={theme} />
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Large</span>
                </div>
                <div className="flex flex-col items-center gap-3">
                  <DavarLogo size="xl" theme={theme} />
                  <span className="text-xs text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>Extra Large</span>
                </div>
              </div>
            </NeumorphCard>
          </div>
        </section>

        {/* RTL Support */}
        <section>
          <h2 className="text-3xl mb-6" style={{ fontFamily: "'Suez One', serif" }}>
            RTL Support - Hebrew Text
          </h2>
          <NeumorphCard className="p-8">
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
                <div className="text-center text-sm text-[var(--text-secondary)] mt-4" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Genesis 1:1 • Cardo 32px • Line Height 1.8 • RTL
                </div>
              </div>

              <div className="pt-6 border-t border-[var(--neomorph-border)]">
                <h3 className="text-lg mb-4" style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600 }}>
                  RTL Implementation Notes
                </h3>
                <ul className="space-y-2 text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  <li>• Use <code className="px-2 py-1 bg-[var(--muted)] rounded">direction: rtl</code> for Hebrew text containers</li>
                  <li>• Line height 1.8-2.0 for scripture (better readability with nikud)</li>
                  <li>• Cardo font for main Hebrew text, Arimo for UI Hebrew</li>
                  <li>• Warm cream (#ebdbb2) color in dark mode for reduced eye strain</li>
                  <li>• Qumran variants highlighted with copper color (#C68F55 / #B5814A)</li>
                </ul>
              </div>
            </div>
          </NeumorphCard>
        </section>

      </div>
    </div>
  );
}
