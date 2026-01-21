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
  currentIndex?: number;
  totalWords?: number;
  onSwipe?: (direction: 'left' | 'right') => void;
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
  currentIndex = 0,
  totalWords = 1,
  onSwipe,
}: WordCardProps) {
  const [activeTab, setActiveTab] = useState<'meanings' | 'instances'>('meanings');
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);

  // Minimum swipe distance (in px)
  const minSwipeDistance = 50;

  const onTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd || !onSwipe) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;
    
    if (isLeftSwipe) {
      onSwipe('left');
    } else if (isRightSwipe) {
      onSwipe('right');
    }
  };

  return (
    <div 
      className="space-y-6 py-4"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
    >
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
        <div className="space-y-6 text-center" style={{ minHeight: '400px' }}>
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

              {/* Progress Navigation - Below root definitions */}
              {totalWords > 1 && (
                <div className="flex justify-center items-center gap-3 pt-8 pb-4" dir="rtl">
                  {/* Arrow button pointing left for RTL */}
                  <button
                    onClick={() => onSwipe?.('left')}
                    className="w-14 h-14 rounded-full flex items-center justify-center transition-all hover:scale-105 active:scale-95"
                    style={{
                      backgroundColor: 'var(--primary)',
                      border: '3px solid var(--background)',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    }}
                    aria-label="Next word"
                  >
                    <svg 
                      width="24" 
                      height="24" 
                      viewBox="0 0 24 24" 
                      fill="none" 
                      stroke="white" 
                      strokeWidth="3"
                      strokeLinecap="round" 
                      strokeLinejoin="round"
                    >
                      <polyline points="15 18 9 12 15 6" />
                    </svg>
                  </button>
                  
                  {/* Progress dots - RTL order */}
                  <div className="flex items-center gap-2" dir="rtl">
                    {Array.from({ length: totalWords }).map((_, idx) => (
                      <div
                        key={idx}
                        style={{
                          width: '10px',
                          height: '10px',
                          borderRadius: '50%',
                          backgroundColor: idx === currentIndex 
                            ? 'var(--primary)' 
                            : 'var(--muted)',
                          transition: 'all 0.3s ease',
                          opacity: idx === currentIndex ? 1 : 0.4,
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6 text-center pb-6" style={{ minHeight: '400px' }}>
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
        </div>
      )}
    </div>
  );
}