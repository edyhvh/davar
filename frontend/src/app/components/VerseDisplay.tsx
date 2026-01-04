import React, { useState, useRef, useEffect } from 'react';
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
  onSwipeUp,
  onSwipeDown,
}: VerseDisplayProps) {
  const [isChapterOpen, setIsChapterOpen] = useState(false);
  const [isVerseOpen, setIsVerseOpen] = useState(false);
  const chapterDropdownRef = useRef<HTMLDivElement>(null);
  const verseDropdownRef = useRef<HTMLDivElement>(null);

  const chapterCount = getChapterCount(book);
  const verseCount = getVerseCount(book, chapter);
  
  const chapters = Array.from({ length: chapterCount }, (_, i) => i + 1);
  const verses = Array.from({ length: verseCount }, (_, i) => i + 1);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (chapterDropdownRef.current && !chapterDropdownRef.current.contains(event.target as Node)) {
        setIsChapterOpen(false);
      }
      if (verseDropdownRef.current && !verseDropdownRef.current.contains(event.target as Node)) {
        setIsVerseOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Split Hebrew text to apply onboarding hint to first word
  const hebrewWords = hebrewText.split(' ');
  const firstWord = hebrewWords[0];
  const restOfText = hebrewWords.slice(1).join(' ');

  return (
    <div className="space-y-8">
      {/* Book Name & Chapter - NEUTRAL Glassmorphic CTA */}
      <div className="flex justify-center items-center gap-2">
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
        
        {/* Chapter Selector */}
        <div className="relative" ref={chapterDropdownRef}>
          <button
            onClick={() => {
              setIsChapterOpen(!isChapterOpen);
              setIsVerseOpen(false);
            }}
            className="bg-[var(--glass-surface)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] rounded-full px-4 py-2.5 hover:bg-[var(--glass-surface-elevated)] hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_4px_16px_0_var(--glass-shadow)] min-w-[50px] flex items-center justify-center gap-1"
          >
            <span 
              className="text-xs text-[var(--text-secondary)]" 
              style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500 }}
            >
              {chapter}
            </span>
            <svg 
              className={`w-3 h-3 text-[var(--text-secondary)] transition-transform ${isChapterOpen ? 'rotate-180' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {/* Chapter Dropdown List */}
          {isChapterOpen && (
            <div 
              className="absolute top-full left-1/2 -translate-x-1/2 mt-2 bg-[var(--glass-surface-elevated)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] rounded-2xl shadow-[0_12px_48px_var(--glass-shadow)] overflow-hidden z-[100]"
              style={{ maxHeight: '300px', overflowY: 'auto', minWidth: '80px' }}
            >
              {chapters.map((ch) => (
                <button
                  key={ch}
                  onClick={() => {
                    onChapterChange(ch);
                    setIsChapterOpen(false);
                  }}
                  className={`w-full px-5 py-3 flex items-center justify-center hover:bg-[var(--muted)] transition-all ${
                    ch === chapter ? 'bg-[#1C2254]' : ''
                  }`}
                >
                  <span 
                    className={`text-base ${ch === chapter ? 'text-white' : 'text-[var(--foreground)]'}`}
                    style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500 }}
                  >
                    {ch}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
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
        className="text-center leading-[2] tracking-[0.01em] relative"
        style={{ 
          fontFamily: "'Cardo', serif",
          fontSize: '42px',
          direction: 'rtl',
          color: 'var(--text-hebrew)',
        }}
      >
        {/* Verse Number - Clickable Dropdown */}
        <div className="relative inline-block" ref={verseDropdownRef}>
          <button
            onClick={() => {
              setIsVerseOpen(!isVerseOpen);
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

          {/* Verse Dropdown List */}
          {isVerseOpen && (
            <div 
              className="absolute top-full left-1/2 -translate-x-1/2 mt-2 bg-[var(--glass-surface-elevated)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] rounded-2xl shadow-[0_12px_48px_var(--glass-shadow)] overflow-hidden z-[100]"
              style={{ maxHeight: '300px', overflowY: 'auto', minWidth: '80px' }}
            >
              {verses.map((v) => (
                <button
                  key={v}
                  onClick={() => {
                    onVerseChange(v);
                    setIsVerseOpen(false);
                  }}
                  className={`w-full px-5 py-3 flex items-center justify-center hover:bg-[var(--muted)] transition-all ${
                    v === verseNumber ? 'bg-[#1C2254]' : ''
                  }`}
                >
                  <span 
                    className={`text-base ${v === verseNumber ? 'text-white' : 'text-[var(--foreground)]'}`}
                    style={{ fontFamily: "'Inter', sans-serif", fontWeight: 500 }}
                  >
                    {v}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
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