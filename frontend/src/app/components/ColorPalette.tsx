import React from 'react';

/**
 * Davar Color Palette Documentation
 * Updated with Tekhelet (Ancient Biblical Blue) Theme
 */

export function ColorPalette() {
  const colorGroups = [
    {
      title: 'Primary Tekhelet Blue',
      description: 'Sacred blue - Adapted for light/dark themes',
      colors: [
        { name: 'Base', value: '#0038B8', var: '--accent (light)', desc: 'Primary tekhelet - Light theme' },
        { name: 'Mid', value: '#002B80', var: '--accent-to', desc: 'Gradient middle' },
        { name: 'Deep', value: '#001F59', var: '--accent-deep', desc: 'Gradient end' },
        { name: 'Bright', value: '#0044CC', var: '--accent (dark)', desc: 'Brighter variant - Dark theme' },
      ],
    },
    {
      title: 'Copper Onboarding',
      description: 'Warm copper tones for subtle onboarding hints',
      colors: [
        { name: 'Copper Base', value: '#B87333', var: '--copper-base', desc: 'Main copper accent' },
        { name: 'Copper Highlight', value: '#CD7F32', var: '--copper-highlight', desc: 'Glow effect' },
        { name: 'Copper Glow', value: 'rgba(205, 127, 50, 0.1)', var: '--copper-glow', desc: 'Subtle glow' },
        { name: 'Copper Background', value: 'rgba(184, 115, 51, 0.05)', var: '--copper-background-subtle', desc: 'Hint background' },
      ],
    },
    {
      title: 'Tekhelet RGBA (Glassmorphism)',
      description: 'Transparent variants for subtle glows and glass effects',
      colors: [
        { name: 'Base 10%', value: 'rgba(0, 56, 184, 0.1)', var: '--accent-glow', desc: 'Subtle glow' },
        { name: 'Dark 15%', value: 'rgba(0, 43, 128, 0.15)', var: '--accent-glow-dark', desc: 'Deeper glow' },
      ],
    },
    {
      title: 'Light Theme Backgrounds',
      description: 'Warm, contemplative backgrounds for light mode',
      colors: [
        { name: 'Light BG', value: '#faf6f0', var: '--background (light)', desc: 'Main background' },
        { name: 'Light Text', value: '#1a1a1a', var: '--text-primary (light)', desc: 'Primary text' },
      ],
    },
    {
      title: 'Dark Theme Backgrounds',
      description: 'Deep, reverent backgrounds for dark mode',
      colors: [
        { name: 'Dark BG', value: '#32302f', var: '--background (dark)', desc: 'Main background - Warm charcoal' },
        { name: 'Dark Text', value: '#ffffff', var: '--text-primary (dark)', desc: 'Primary text' },
        { name: 'Dark Hebrew', value: '#ebdbb2', var: '--text-hebrew (dark)', desc: 'Hebrew text - Warm cream' },
      ],
    },
  ];

  return (
    <div className="space-y-8 p-6">
      <div>
        <h2 
          className="text-2xl mb-2"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Davar Color System
        </h2>
        <p 
          className="text-[var(--text-secondary)] text-sm"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Tekhelet-inspired minimalist palette for reverent scripture reading
        </p>
      </div>

      {/* Primary Gradient Preview */}
      <div className="rounded-2xl overflow-hidden h-32" style={{
        background: 'linear-gradient(135deg, #0038B8 0%, #002B80 50%, #001F59 100%)',
      }}>
        <div className="h-full flex items-center justify-center">
          <div className="text-center text-white">
            <div style={{ fontFamily: "'Suez One', serif", fontSize: '24px' }}>תְּכֵלֶת</div>
            <div className="text-sm opacity-80 mt-1" style={{ fontFamily: "'Inter', sans-serif" }}>
              Tekhelet Gradient
            </div>
          </div>
        </div>
      </div>

      {/* Color Groups */}
      {colorGroups.map((group) => (
        <div key={group.title} className="space-y-4">
          <div>
            <h3 
              className="text-lg"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              {group.title}
            </h3>
            <p 
              className="text-[var(--text-secondary)] text-xs"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              {group.description}
            </p>
          </div>
          
          <div className="grid gap-3">
            {group.colors.map((color) => (
              <div 
                key={color.name}
                className="bg-[var(--glass-surface)] backdrop-blur-xl border border-[var(--glass-border)] rounded-xl p-4"
              >
                <div className="flex items-center gap-4">
                  <div
                    className="w-16 h-16 rounded-lg border border-[var(--glass-border)] flex-shrink-0"
                    style={{ background: color.value }}
                  />
                  <div className="flex-1 min-w-0">
                    <div 
                      className="font-medium text-sm"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {color.name}
                    </div>
                    <div 
                      className="text-xs text-[var(--text-secondary)] font-mono mt-1"
                      style={{ fontFamily: "'JetBrains Mono', monospace" }}
                    >
                      {color.value}
                    </div>
                    <div 
                      className="text-xs text-[var(--text-secondary)] mt-1"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      var({color.var}) · {color.desc}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Usage Guidelines */}
      <div className="bg-[var(--glass-surface)] backdrop-blur-xl border border-[var(--glass-border)] rounded-xl p-6 space-y-4">
        <h3 
          className="text-lg"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Usage Guidelines
        </h3>
        <ul className="space-y-2 text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          <li>• Use Primary Base (#0038B8) for buttons, links, and primary actions</li>
          <li>• Apply the tekhelet gradient for logo, launch screen, and hero elements</li>
          <li>• Use RGBA variants for glassmorphism effects and subtle glows</li>
          <li>• Maintain WCAG AA contrast ratio for all text</li>
          <li>• Dark theme uses same tekhelet intensity for consistency</li>
        </ul>
      </div>

      {/* Contrast Examples */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-[var(--accent)] text-white p-4 rounded-xl text-center">
          <div style={{ fontFamily: "'Cardo', serif", fontSize: '20px', direction: 'rtl' }}>
            בְּרֵאשִׁית
          </div>
          <div className="text-xs opacity-80 mt-2" style={{ fontFamily: "'Inter', sans-serif" }}>
            Hebrew on Tekhelet
          </div>
        </div>
        <div className="bg-white text-[var(--accent)] p-4 rounded-xl text-center border border-[var(--glass-border)]">
          <div style={{ fontFamily: "'Cardo', serif", fontSize: '20px', direction: 'rtl' }}>
            בְּרֵאשִׁית
          </div>
          <div className="text-xs opacity-80 mt-2" style={{ fontFamily: "'Inter', sans-serif" }}>
            Tekhelet on White
          </div>
        </div>
      </div>
    </div>
  );
}