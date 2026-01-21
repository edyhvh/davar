import React from 'react';
import type { DssVariant, VerseResponse, WordResponse } from '../services/verseService';

interface FullChapterViewProps {
  verses: VerseResponse[];
  bookName: string;
  bookNameHebrew: string;
  chapter: number;
  language: 'en' | 'es' | 'he';
  hebrewOnly: boolean;
  onWordClick: (word: WordResponse) => void;
  showQumran?: boolean;
  selectedWord?: string | null;
}

export function FullChapterView({
  verses,
  bookName,
  bookNameHebrew,
  chapter,
  language,
  hebrewOnly,
  onWordClick,
  showQumran,
  selectedWord,
}: FullChapterViewProps) {
  return (
    <div className="space-y-6 transition-all duration-500">
      {/* Book Name & Chapter Header */}
      <div className="flex justify-center items-center gap-2 sticky top-0 z-10 bg-[var(--background)] py-4">
        <div
          className="bg-[var(--neomorph-bg)] border border-[var(--neomorph-border)] rounded-full px-5 py-2.5 shadow-[4px_4px_12px_var(--neomorph-shadow-dark),-4px_-4px_12px_var(--neomorph-shadow-light)]"
        >
          <div 
            className="text-xs text-[var(--text-secondary)]"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {bookName.toUpperCase()} {chapter} | <span style={{ fontFamily: "'Arimo', sans-serif" }}>{bookNameHebrew} {chapter}</span>
          </div>
        </div>
      </div>

      {/* Chapter Verses */}
      <div className="space-y-8 px-2">
        {verses.map((verse, idx) => (
          <div 
            key={idx} 
            className="space-y-3 transition-all duration-300"
          >
            {/* Hebrew Text with Verse Number */}
            <div 
              className="leading-relaxed tracking-[0.01em]"
              style={{ 
                fontFamily: "'Cardo', serif",
                fontSize: '32px',
                direction: 'rtl',
                color: 'var(--text-hebrew)',
              }}
            >
              <span 
                className="text-[var(--text-secondary)] opacity-40 ml-2"
                style={{ 
                  fontFamily: "'Inter', sans-serif",
                  fontSize: '13px',
                }}
              >
                [{idx + 1}]
              </span>
              {(() => {
                const dssMap = new Map<number, string>();
                verse.dss?.forEach((variant) => dssMap.set(variant.word_position, variant.dss_text));

                return verse.words.map((word, wordIdx) => {
                  const variantText = showQumran ? dssMap.get(word.position) : undefined;
                const displayText = variantText ?? word.text;
                const isSelected = selectedWord === word.text || selectedWord === displayText;

                  return (
                    <span key={word.position}>
                      <span 
                        onClick={() => onWordClick(word)} 
                        className={`cursor-pointer transition-colors duration-200 ${isSelected ? 'verse-highlight' : ''}`}
                        style={variantText ? { color: 'var(--copper-highlight)' } : undefined}
                      >
                        {displayText}
                      </span>
                      {wordIdx < verse.words.length - 1 && ' '}
                    </span>
                  );
                });
              })()}
            </div>

            {/* Translation - only show if not Hebrew Only mode */}
            {!hebrewOnly && (
              <div 
                className="text-[var(--text-secondary)] leading-relaxed"
                style={{ 
                  fontFamily: "'Inter', sans-serif",
                  fontSize: '15px',
                }}
              >
                [{verse.translation}]
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}