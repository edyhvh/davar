import React, { useState } from 'react';
import { GlassCard } from './GlassCard';

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
}

export function WordCard({ 
  word, 
  transliteration, 
  meanings, 
  root, 
  rootTransliteration, 
  rootMeaning, 
  instances, 
  onInstanceClick 
}: WordCardProps) {
  const [activeTab, setActiveTab] = useState<'meanings' | 'instances'>('meanings');

  return (
    <div className="space-y-6 py-4">
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
          {word}
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
              ? 'var(--primary)' 
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
              ? 'var(--primary)' 
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
            <p 
              style={{ 
                fontFamily: "'Inter', sans-serif",
                fontSize: '18px',
                lineHeight: 1.5,
                fontWeight: 400,
              }}
              className="dark:text-[var(--text-secondary)]"
            >
              {meanings.join(', ')}
            </p>
          </div>

          {/* Root Section */}
          {root && (
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
                {/* Hebrew root */}
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
                  {root}
                </div>
                
                {/* Root transliteration - smaller */}
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
                
                {/* Root meaning */}
                {rootMeaning && (
                  <div 
                    style={{ 
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '15px',
                      lineHeight: 1.5,
                      marginTop: '12px',
                    }}
                    className="dark:text-[var(--text-secondary)]"
                  >
                    {rootMeaning}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4 text-center">
          {/* Instances Section */}
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
            {instances.map((instance, idx) => (
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
            ))}
          </div>
        </div>
      )}
    </div>
  );
}