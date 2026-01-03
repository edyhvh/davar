import React, { useState } from 'react';
import { GlassCard } from './GlassCard';
import { GlassButton } from './GlassButton';

interface WordInstance {
  verse: string;
  text: string;
}

interface WordCardProps {
  word: string;
  meanings: string[];
  root?: string;
  instances: WordInstance[];
  onInstanceClick: (verse: string) => void;
}

export function WordCard({ word, meanings, root, instances, onInstanceClick }: WordCardProps) {
  const [activeTab, setActiveTab] = useState<'meanings' | 'instances'>('meanings');

  return (
    <div className="space-y-6 py-4">
      {/* Title */}
      <div className="text-center">
        <h2 
          className="text-lg font-medium"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Word Analysis
        </h2>
      </div>

      {/* Word - Large and centered */}
      <div 
        className="text-center"
        style={{ 
          fontFamily: "'Cardo', serif",
          fontSize: '52px',
          direction: 'rtl',
          lineHeight: 1.2,
          color: 'var(--text-hebrew)',
        }}
      >
        {word}
      </div>

      {/* Tabs - NEUTRAL glass, Tekhelet ONLY when selected */}
      <div className="flex gap-3">
        <button
          onClick={() => setActiveTab('meanings')}
          className={`flex-1 px-5 py-4 rounded-2xl transition-all shadow-[0_4px_16px_var(--glass-shadow)] ${
            activeTab === 'meanings'
              ? 'bg-[var(--accent)] text-white scale-105 shadow-[0_8px_24px_rgba(65,105,225,0.35)]'
              : 'bg-[var(--glass-surface)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] text-[var(--text-secondary)] hover:scale-105 hover:bg-[var(--glass-surface-elevated)]'
          }`}
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Meanings
        </button>
        <button
          onClick={() => setActiveTab('instances')}
          className={`flex-1 px-5 py-4 rounded-2xl transition-all shadow-[0_4px_16px_var(--glass-shadow)] ${
            activeTab === 'instances'
              ? 'bg-[var(--accent)] text-white scale-105 shadow-[0_8px_24px_rgba(65,105,225,0.35)]'
              : 'bg-[var(--glass-surface)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] text-[var(--text-secondary)] hover:scale-105 hover:bg-[var(--glass-surface-elevated)]'
          }`}
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          Instances
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'meanings' ? (
        <div className="space-y-5">
          {/* Meanings - HEAVY GLASS */}
          <GlassCard className="p-6">
            <h3 className="text-xs uppercase tracking-wider text-[var(--text-secondary)] mb-5" style={{ fontFamily: "'Inter', sans-serif" }}>
              Meanings
            </h3>
            <ul className="space-y-4">
              {meanings.map((meaning, idx) => (
                <li 
                  key={idx} 
                  className="text-base text-[var(--foreground)] flex items-start gap-3"
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  <span className="text-[var(--accent)] mt-1 text-lg">•</span>
                  <span>{meaning}</span>
                </li>
              ))}
            </ul>
          </GlassCard>

          {/* Root - HEAVY GLASS */}
          {root && (
            <GlassCard className="p-6">
              <h3 className="text-xs uppercase tracking-wider text-[var(--text-secondary)] mb-4" style={{ fontFamily: "'Inter', sans-serif" }}>
                Root
              </h3>
              <div 
                className="text-3xl"
                style={{ 
                  fontFamily: "'Cardo', serif",
                  direction: 'rtl',
                  color: 'var(--text-hebrew)',
                }}
              >
                {root}
              </div>
            </GlassCard>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {/* Instances Grid */}
          <h3 className="text-xs uppercase tracking-wider text-[var(--text-secondary)] px-2" style={{ fontFamily: "'Inter', sans-serif" }}>
            Tap to navigate
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {instances.map((instance, idx) => (
              <GlassCard
                key={idx}
                hoverable
                onClick={() => onInstanceClick(instance.verse)}
                className="p-5 text-center"
              >
                <div className="text-xs font-medium text-[var(--accent)] mb-3" style={{ fontFamily: "'Inter', sans-serif" }}>
                  {instance.verse}
                </div>
                <div 
                  className="text-sm leading-relaxed"
                  style={{ 
                    fontFamily: "'Cardo', serif",
                    direction: 'rtl',
                    color: 'var(--text-hebrew)',
                  }}
                >
                  {instance.text}
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}