import React from 'react';
import { OnboardingWordHint } from './OnboardingWordHint';
import { SwipeIndicator } from './SwipeIndicator';

interface VerseDisplayProps {
  hebrewText: string;
  translation: string;
  qumranText?: string;
  qumranTranslation?: string;
  verseRef: string;
  verseNumber: number;
  bookName: string;
  bookNameHebrew: string;
  language: 'en' | 'es' | 'he';
  onBookNameClick: () => void;
  onWordClick: (word: string) => void;
  previousVerseSnippet?: string;
  nextVerseSnippet?: string;
  showOnboardingHint?: boolean;
  showQumran?: boolean;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}

export function VerseDisplay({
  hebrewText,
  translation,
  qumranText,
  qumranTranslation,
  verseRef,
  verseNumber,
  bookName,
  bookNameHebrew,
  language,
  onBookNameClick,
  onWordClick,
  previousVerseSnippet,
  nextVerseSnippet,
  showOnboardingHint = false,
  showQumran = false,
  onSwipeUp,
  onSwipeDown,
}: VerseDisplayProps) {
  // Split Hebrew text to apply onboarding hint to first word
  const hebrewWords = hebrewText.split(' ');
  const firstWord = hebrewWords[0];
  const restOfText = hebrewWords.slice(1).join(' ');

  return (
    <div className="space-y-8">
      {/* Book Name - NEUTRAL Glassmorphic CTA */}
      <div className="flex justify-center">
        <button
          onClick={onBookNameClick}
          className="bg-[var(--glass-surface)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] rounded-full px-5 py-2.5 hover:bg-[var(--glass-surface-elevated)] hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_4px_16px_0_var(--glass-shadow)]"
        >
          <div 
            className="text-xs text-[var(--text-secondary)]"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {bookName.toUpperCase()} | <span style={{ fontFamily: "'Arimo', sans-serif" }}>{bookNameHebrew}</span>
          </div>
        </button>
      </div>

      {/* Previous Verse Snippet */}
      {previousVerseSnippet && (
        <div 
          className="text-center leading-relaxed opacity-20"
          style={{ 
            fontFamily: "'Cardo', serif",
            fontSize: '20px',
            direction: 'rtl',
          }}
        >
          {previousVerseSnippet}
        </div>
      )}

      {/* Hebrew Text with Verse Number and Onboarding Hint - Large and Centered */}
      <div 
        className="text-center leading-[2] tracking-[0.01em]"
        style={{ 
          fontFamily: "'Cardo', serif",
          fontSize: '42px',
          direction: 'rtl',
          color: 'var(--text-hebrew)',
        }}
      >
        <span 
          className="text-[var(--text-secondary)] opacity-50 ml-2"
          style={{ 
            fontFamily: "'Inter', sans-serif",
            fontSize: '14px',
          }}
        >
          [{verseNumber}]
        </span>
        <OnboardingWordHint
          word={firstWord}
          isActive={showOnboardingHint}
          onClick={() => onWordClick(firstWord)}
        />
        {' '}
        <span onClick={() => onWordClick(restOfText)} className="cursor-pointer">
          {restOfText}
        </span>
      </div>

      {/* Translation and Next Verse with Swipe Indicator */}
      <SwipeIndicator onSwipeUp={onSwipeUp} onSwipeDown={onSwipeDown}>
        <div className="space-y-8">
          {/* Translation */}
          <div 
            className="text-center text-[var(--text-secondary)] leading-relaxed px-4"
            style={{ 
              fontFamily: "'Inter', sans-serif",
              fontSize: '17px',
            }}
          >
            {translation}
          </div>

          {/* Next Verse Snippet */}
          {nextVerseSnippet && (
            <div 
              className="text-center leading-relaxed opacity-20"
              style={{ 
                fontFamily: "'Cardo', serif",
                fontSize: '20px',
                direction: 'rtl',
                color: 'var(--text-hebrew)',
              }}
            >
              {nextVerseSnippet}
            </div>
          )}
        </div>
      </SwipeIndicator>
    </div>
  );
}