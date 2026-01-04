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
      {/* Word - Large and centered with transliteration below */}
      <div className="text-center space-y-2">
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
        
        {/* Transliteration - small and gray */}
        {transliteration && (
          <div 
            className="text-sm"
            style={{ 
              fontFamily: "'Inter', sans-serif",
              color: 'var(--text-secondary)',
            }}
          >
            {transliteration}
          </div>
        )}
      </div>

      {/* Segmented Control - iOS style */}
      <div className="bg-[var(--muted)] p-1 rounded-full flex gap-1">
        <button
          onClick={() => setActiveTab('meanings')}
          className={`flex-1 px-5 py-3 rounded-full transition-all ${
            activeTab === 'meanings'
              ? 'bg-white dark:bg-[var(--surface)] text-[var(--foreground)] shadow-sm'
              : 'text-[var(--text-secondary)]'
          }`}
          style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: '15px' }}
        >
          Meanings
        </button>
        <button
          onClick={() => setActiveTab('instances')}
          className={`flex-1 px-5 py-3 rounded-full transition-all ${
            activeTab === 'instances'
              ? 'bg-white dark:bg-[var(--surface)] text-[var(--foreground)] shadow-sm'
              : 'text-[var(--text-secondary)]'
          }`}
          style={{ fontFamily: "'Inter', sans-serif", fontWeight: 600, fontSize: '15px' }}
        >
          Instances
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'meanings' ? (
        <div className="space-y-6 px-2" style={{ minHeight: '320px' }}>
          {/* Meanings - Inline with separator */}
          <div>
            <h3 
              className="text-xs uppercase tracking-wider mb-3" 
              style={{ 
                fontFamily: "'Inter', sans-serif",
                color: 'var(--text-secondary)',
              }}
            >
              Meanings
            </h3>
            <p 
              className="leading-relaxed"
              style={{ 
                fontFamily: "'Inter', sans-serif",
                fontSize: '16px',
                color: 'var(--foreground)',
              }}
            >
              {meanings.join(' • ')}
            </p>
          </div>

          {/* Root - Inline */}
          {root && (
            <div className="border-t pt-6" style={{ borderColor: 'var(--border)' }}>
              <h3 
                className="text-xs uppercase tracking-wider mb-3" 
                style={{ 
                  fontFamily: "'Inter', sans-serif",
                  color: 'var(--text-secondary)',
                }}
              >
                Root
              </h3>
              <div className="space-y-2">
                {/* Hebrew root */}
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
                
                {/* Root transliteration - lowercase */}
                {rootTransliteration && (
                  <div 
                    className="text-sm"
                    style={{ 
                      fontFamily: "'Inter', sans-serif",
                      color: 'var(--text-secondary)',
                    }}
                  >
                    {rootTransliteration.toLowerCase()}
                  </div>
                )}
                
                {/* Root meaning */}
                {rootMeaning && (
                  <div 
                    className="text-sm mt-3"
                    style={{ 
                      fontFamily: "'Inter', sans-serif",
                      color: 'var(--foreground)',
                    }}
                  >
                    {rootMeaning}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4 px-2" style={{ minHeight: '320px' }}>
          {/* Instances - Retro style */}
          <h3 
            className="text-xs uppercase tracking-wider" 
            style={{ 
              fontFamily: "'Inter', sans-serif",
              color: 'var(--text-secondary)',
            }}
          >
            Tap to navigate
          </h3>
          <div className="grid grid-cols-3 gap-2">
            {instances.map((instance, idx) => (
              <button
                key={idx}
                onClick={() => onInstanceClick(instance.verse)}
                className="px-3 py-3 rounded-xl border transition-all hover:bg-[var(--muted)]"
                style={{ 
                  backgroundColor: 'var(--surface)',
                  borderColor: 'var(--border)',
                  fontFamily: "'Inter', sans-serif",
                  fontSize: '13px',
                  fontWeight: 500,
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