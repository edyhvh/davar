import React, { useState } from 'react';
import { OnboardingWordHint } from './OnboardingWordHint';
import { SwipeIndicator } from './SwipeIndicator';
import { FullChapterView } from './FullChapterView';
import { VerticalSwipeIndicators } from './VerticalSwipeIndicators';
import { BottomSheet } from './BottomSheet';
import { NeumorphNumberButton } from './NeumorphNumberButton';

interface VerseDisplayProps {
  hebrewText: string;
  translation: string;
  qumranText?: string;
  qumranTranslation?: string;
  verseRef: string;
  verseNumber: number;
  bookName: string;
  bookNameHebrew: string;
  book: string;
  chapter: number;
  language: 'en' | 'es' | 'he';
  onBookNameClick: () => void;
  onChapterChange: (chapter: number) => void;
  onVerseChange: (verse: number) => void;
  onWordClick: (word: string) => void;
  previousVerseSnippet?: string;
  nextVerseSnippet?: string;
  showOnboardingHint?: boolean;
  showQumran?: boolean;
  showFullChapter?: boolean;
  hebrewOnly?: boolean;
  chapterVerses?: { 
    hebrew: string; 
    translation: string;
    wordVariants?: {
      [word: string]: {
        qumranWord: string;
        masoreticWord: string;
        label: string;
        color: 'yellow' | 'pink' | 'green' | 'lime' | 'red' | 'teal';
      };
    };
  }[];
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}

// Mock data - in real app this would come from API
const getChapterCount = (book: string): number => {
  const counts: { [key: string]: number } = {
    'Genesis': 50,
    'Exodus': 40,
    'Psalms': 150,
  };
  return counts[book] || 50;
};

const getVerseCount = (book: string, chapter: number): number => {
  // Mock data - in real app this would be accurate
  if (book === 'Genesis' && chapter === 1) return 31;
  if (book === 'Psalms' && chapter === 119) return 176;
  return 25; // Default
};

export function VerseDisplay({
  hebrewText,
  translation,
  qumranText,
  qumranTranslation,
  verseRef,
  verseNumber,
  bookName,
  bookNameHebrew,
  book,
  chapter,
  language,
  onBookNameClick,
  onChapterChange,
  onVerseChange,
  onWordClick,
  previousVerseSnippet,
  nextVerseSnippet,
  showOnboardingHint = false,
  showQumran = false,
  showFullChapter = false,
  hebrewOnly = false,
  chapterVerses,
  onSwipeUp,
  onSwipeDown,
}: VerseDisplayProps) {
  const [isChapterOpen, setIsChapterOpen] = useState(false);
  const [isVerseOpen, setIsVerseOpen] = useState(false);

  const chapterCount = getChapterCount(book);
  const verseCount = getVerseCount(book, chapter);
  
  const chapters = Array.from({ length: chapterCount }, (_, i) => i + 1);
  const verses = Array.from({ length: verseCount }, (_, i) => i + 1);

  // Function to render Hebrew text with word variants
  const renderHebrewText = () => {
    const words = hebrewText.split(' ');
    
    return words.map((word, index) => {
      const variant = chapterVerses && chapterVerses[verseNumber - 1] && chapterVerses[verseNumber - 1].wordVariants && chapterVerses[verseNumber - 1].wordVariants[word];
      
      // Special handling for first word with onboarding hint
      if (index === 0) {
        if (variant && showQumran) {
          return (
            <span key={index}>
              <span
                onClick={() => onWordClick(variant.qumranWord)}
                className="cursor-pointer transition-colors"
                style={{ color: 'var(--copper-highlight)' }}
              >
                {variant.qumranWord}
              </span>
              {index < words.length - 1 && ' '}
            </span>
          );
        } else {
          return (
            <span key={index}>
              <OnboardingWordHint
                word={word}
                isActive={showOnboardingHint}
                onClick={() => onWordClick(word)}
              />
              {index < words.length - 1 && ' '}
            </span>
          );
        }
      }
      
      // Regular words with potential variants - use copper color for Qumran
      if (variant && showQumran) {
        return (
          <span key={index}>
            <span
              onClick={() => onWordClick(variant.qumranWord)}
              className="cursor-pointer transition-colors"
              style={{ color: 'var(--copper-highlight)' }}
            >
              {variant.qumranWord}
            </span>
            {index < words.length - 1 && ' '}
          </span>
        );
      }
      
      // Regular word without variant
      return (
        <span key={index}>
          <span onClick={() => onWordClick(word)} className="cursor-pointer">
            {word}
          </span>
          {index < words.length - 1 && ' '}
        </span>
      );
    });
  };

  // If full chapter mode is enabled and we have verses, show the full chapter view
  if (showFullChapter && chapterVerses && chapterVerses.length > 0) {
    return (
      <div className="transition-opacity duration-500">
        <FullChapterView
          verses={chapterVerses}
          bookName={bookName}
          bookNameHebrew={bookNameHebrew}
          chapter={chapter}
          language={language}
          hebrewOnly={hebrewOnly}
          onBookNameClick={onBookNameClick}
          onWordClick={onWordClick}
          showQumran={showQumran}
        />
      </div>
    );
  }

  // Otherwise show the single verse view
  return (
    <div className="space-y-8 relative">
      {/* Animated Swipe Indicators - TikTok/YouTube Shorts style */}
      <VerticalSwipeIndicators 
        showUpIndicator={!!previousVerseSnippet} 
        showDownIndicator={!!nextVerseSnippet} 
      />

      {/* Book Name & Chapter - Neumorphic CTA */}
      <div className="flex justify-center items-center gap-2">
        <button
          onClick={onBookNameClick}
          className="bg-[var(--neomorph-bg)] border border-[var(--neomorph-border)] rounded-full px-5 py-2.5 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[4px_4px_12px_var(--neomorph-shadow-dark),-4px_-4px_12px_var(--neomorph-shadow-light)] hover:shadow-[2px_2px_8px_var(--neomorph-shadow-dark),-2px_-2px_8px_var(--neomorph-shadow-light)] active:shadow-[inset_2px_2px_6px_var(--neomorph-inset-shadow-dark),inset_-2px_-2px_6px_var(--neomorph-inset-shadow-light)]"
        >
          <div 
            className="text-xs text-[var(--text-secondary)]"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {bookName.toUpperCase()} | <span style={{ fontFamily: "'Arimo', sans-serif" }}>{bookNameHebrew}</span>
          </div>
        </button>
        
        {/* Chapter Selector */}
        <button
          onClick={() => {
            setIsChapterOpen(true);
            setIsVerseOpen(false);
          }}
          className="bg-[var(--neomorph-bg)] border border-[var(--neomorph-border)] rounded-full px-4 py-2.5 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[4px_4px_12px_var(--neomorph-shadow-dark),-4px_-4px_12px_var(--neomorph-shadow-light)] hover:shadow-[2px_2px_8px_var(--neomorph-shadow-dark),-2px_-2px_8px_var(--neomorph-shadow-light)] active:shadow-[inset_2px_2px_6px_var(--neomorph-inset-shadow-dark),inset_-2px_-2px_6px_var(--neomorph-inset-shadow-light)] min-w-[50px] flex items-center justify-center"
        >
          <span 
            className="text-xs text-[var(--text-secondary)]" 
            style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500 }}
          >
            {chapter}
          </span>
        </button>
      </div>

      {/* Chapter Selection Bottom Sheet */}
      <BottomSheet 
        isOpen={isChapterOpen} 
        onClose={() => setIsChapterOpen(false)}
        title="Select Chapter"
      >
        <div className="grid grid-cols-4 gap-3 pb-4">
          {chapters.map((ch) => (
            <NeumorphNumberButton
              key={ch}
              number={ch}
              isSelected={ch === chapter}
              onClick={() => {
                onChapterChange(ch);
                setIsChapterOpen(false);
              }}
            />
          ))}
        </div>
      </BottomSheet>

      {/* Verse Selection Bottom Sheet */}
      <BottomSheet 
        isOpen={isVerseOpen} 
        onClose={() => setIsVerseOpen(false)}
        title="Select Verse"
      >
        <div className="grid grid-cols-4 gap-3 pb-4">
          {verses.map((v) => (
            <NeumorphNumberButton
              key={v}
              number={v}
              isSelected={v === verseNumber}
              onClick={() => {
                onVerseChange(v);
                setIsVerseOpen(false);
              }}
            />
          ))}
        </div>
      </BottomSheet>

      {/* Hebrew Text with Verse Number and Onboarding Hint - Large and Centered */}
      <div 
        className="text-center leading-[2] tracking-[0.01em] relative"
        style={{ 
          fontFamily: "'Cardo', serif",
          fontSize: '42px',
          direction: 'rtl',
          color: 'var(--text-hebrew)',
        }}
      >
        {/* Verse Number - Clickable */}
        <button
          onClick={() => {
            setIsVerseOpen(true);
            setIsChapterOpen(false);
          }}
          className="text-[var(--text-secondary)] opacity-50 ml-2 cursor-pointer hover:opacity-70 transition-opacity"
          style={{ 
            fontFamily: "'Inter', sans-serif",
            fontSize: '14px',
          }}
        >
          [{verseNumber}]
        </button>
        {renderHebrewText()}
      </div>

      {/* Translation - Only show if not Hebrew Only mode */}
      {!hebrewOnly && (
        <SwipeIndicator onSwipeUp={onSwipeUp} onSwipeDown={onSwipeDown}>
          <div 
            className="text-center leading-relaxed px-4 transition-all duration-500 text-[var(--text-secondary)]"
            style={{ 
              fontFamily: "'Inter', sans-serif",
              fontSize: '17px',
            }}
          >
            {translation}
          </div>
        </SwipeIndicator>
      )}
    </div>
  );
}