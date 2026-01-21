import React, { useState } from 'react';
import { X } from 'lucide-react';
import { normalizeHebrew, stripCantillation } from '../utils/hebrew';

interface WordInstance {
  verse: string;
  text: string;
}

interface WordCardProps {
  word: string;
  transliteration?: string;
  meanings: string[];
  root?: string;
  rootTransliteration?: string;
  rootMeaning?: string;
  instances: WordInstance[];
  onInstanceClick: (verse: string) => void;
  isLoading?: boolean;
  onClose?: () => void;
}

export function WordCard({ 
  word, 
  transliteration, 
  meanings, 
  root, 
  rootTransliteration, 
  rootMeaning, 
  instances, 
  onInstanceClick,
  isLoading = false,
  onClose,
}: WordCardProps) {
  const [activeTab, setActiveTab] = useState<'meanings' | 'instances'>('meanings');

  return (
    <div className="space-y-6 py-2">
      <div className="flex justify-end">
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-full p-2 transition-all hover:scale-105 active:scale-95"
            style={{
              backgroundColor: 'var(--neomorph-bg)',
              border: '1px solid var(--neomorph-border)',
              boxShadow: '6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)',
            }}
            aria-label="Close word meaning"
          >
            <X className="w-4 h-4 text-[var(--text-secondary)]" />
          </button>
        )}
      </div>
      {isLoading && (
        <div className="text-center text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          Loading word analysis…
        </div>
      )}

      {/* Word - Large centered */}
      <div className="text-center space-y-2 pb-6">
        <div 
          style={{ 
            fontFamily: "'Cardo', serif",
            fontSize: '64px',
            direction: 'rtl',
            lineHeight: 1,
            color: 'var(--text-hebrew)',
            fontWeight: 600,
          }}
        >
          {normalizeHebrew(word).replace(/\//g, '')}
        </div>
        
        {/* Transliteration */}
        {transliteration && (
          <div 
            style={{ 
              fontFamily: "'Inter', sans-serif",
              fontSize: '11px',
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.15em',
              fontWeight: 500,
              marginTop: '12px',
            }}
          >
            {transliteration}
          </div>
        )}
      </div>

      {/* Segmented Control - Pill style with border */}
      <div 
        className="grid grid-cols-2 gap-2 border-2 border-[var(--primary)] rounded-full p-1"
        style={{ overflow: 'hidden' }}
      >
        <button
          onClick={() => setActiveTab('meanings')}
          className="py-3 transition-all rounded-full"
          style={{ 
            fontFamily: "'Inter', sans-serif", 
            fontWeight: 700, 
            fontSize: '11px',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            backgroundColor: activeTab === 'meanings' 
              ? 'var(--accent-strong)' 
              : 'transparent',
            color: activeTab === 'meanings'
              ? '#ffffff'
              : 'var(--text-secondary)',
          }}
        >
          Meanings
        </button>
        <button
          onClick={() => setActiveTab('instances')}
          className="py-3 transition-all rounded-full"
          style={{ 
            fontFamily: "'Inter', sans-serif", 
            fontWeight: 700, 
            fontSize: '11px',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            backgroundColor: activeTab === 'instances' 
              ? 'var(--accent-strong)' 
              : 'transparent',
            color: activeTab === 'instances'
              ? '#ffffff'
              : 'var(--text-secondary)',
          }}
        >
          Instances
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'meanings' ? (
        <div className="space-y-6 text-center">
          {/* Meanings Section */}
          <div className="pb-6">
            <h3 
              className="mb-4"
              style={{ 
                fontFamily: "'Inter', sans-serif",
                fontSize: '11px',
                color: 'var(--text-secondary)',
                fontWeight: 700,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
              }}
            >
              Meanings
            </h3>
            <div 
              style={{ 
                fontFamily: "'Inter', sans-serif",
                fontSize: '18px',
                lineHeight: 1.5,
                fontWeight: 400,
              }}
              className="dark:text-[var(--text-secondary)]"
            >
              {meanings.length > 0 ? (
                <div className="space-y-2 text-center">
                  {meanings
                    .flatMap((m) => (m ? m.split(/[,;]\s*/).map((s) => s.trim()) : []))
                    .map((m, i) => (
                      <div key={i} style={{ whiteSpace: 'normal' }}>
                        {stripCantillation(m).replace(/\//g, '').trim()}
                      </div>
                    ))}
                </div>
              ) : (
                'No meanings available yet.'
              )}
            </div>
          </div>

          {/* Root Section */}
          {/* Root Section — always show; if no root, show ALREADY ROOT */}
          <div className="pb-6">
            <h3 
              className="mb-4"
              style={{ 
                fontFamily: "'Inter', sans-serif",
                fontSize: '11px',
                color: 'var(--text-secondary)',
                fontWeight: 700,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
              }}
            >
              Root
            </h3>
            <div className="space-y-2">
              {root ? (
                <>
                  <div 
                    style={{ 
                      fontFamily: "'Cardo', serif",
                      fontSize: '48px',
                      direction: 'rtl',
                      color: 'var(--primary)',
                      fontWeight: 600,
                      lineHeight: 1,
                    }}
                  >
                    {normalizeHebrew(root).replace(/\//g, '')}
                  </div>

                  {rootTransliteration && (
                    <div 
                      style={{ 
                        fontFamily: "'Inter', sans-serif",
                        fontSize: '11px',
                        color: 'var(--text-secondary)',
                        textTransform: 'uppercase',
                        letterSpacing: '0.12em',
                        fontWeight: 500,
                        marginTop: '8px',
                      }}
                    >
                      {rootTransliteration}
                    </div>
                  )}

                  <div 
                    style={{ 
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '15px',
                      lineHeight: 1.5,
                      marginTop: '12px',
                    }}
                    className="dark:text-[var(--text-secondary)]"
                  >
                    {rootMeaning ? normalizeHebrew(rootMeaning).replace(/\//g, '') : '—'}
                  </div>
                </>
              ) : (
                <div 
                  style={{ 
                    fontFamily: "'Inter', sans-serif",
                    fontSize: '15px',
                    lineHeight: 1.5,
                    textAlign: 'center'
                  }}
                  className="dark:text-[var(--text-secondary)]"
                >
                  <strong>ALREADY ROOT</strong>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6 text-center pb-6">
          {/* Instances Section */}
          <div className="pb-6">
            <h3
              className="mb-4"
              style={{ 
                fontFamily: "'Inter', sans-serif",
                fontSize: '11px',
                color: 'var(--text-secondary)',
                fontWeight: 700,
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
              }}
            >
              Tap to Navigate
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {instances.length > 0 ? (
                instances.map((instance, idx) => (
                  <button
                    key={idx}
                    onClick={() => onInstanceClick(instance.verse)}
                    className="py-4 transition-all hover:bg-[var(--primary)] hover:text-white rounded-[20px]"
                    style={{ 
                      backgroundColor: 'var(--muted)',
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '13px',
                      fontWeight: 600,
                      color: 'var(--foreground)',
                    }}
                  >
                    {instance.verse}
                  </button>
                ))
              ) : (
                <div className="col-span-3 text-sm text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
                  No instances available yet.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}