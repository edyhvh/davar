import React from 'react';

interface Verse {
  hebrew: string;
  translation: string;
}

interface FullChapterViewProps {
  verses: Verse[];
  bookName: string;
  bookNameHebrew: string;
  chapter: number;
  language: 'en' | 'es' | 'he';
  hebrewOnly: boolean;
  onBookNameClick: () => void;
  onWordClick: (word: string) => void;
}

export function FullChapterView({
  verses,
  bookName,
  bookNameHebrew,
  chapter,
  language,
  hebrewOnly,
  onBookNameClick,
  onWordClick,
}: FullChapterViewProps) {
  return (
    <div className="space-y-6 transition-all duration-500">
      {/* Book Name & Chapter Header */}
      <div className="flex justify-center items-center gap-2 sticky top-0 z-10 bg-[var(--background)] py-4">
        <button
          onClick={onBookNameClick}
          className="bg-[var(--glass-surface)] backdrop-blur-[40px] border-2 border-[var(--glass-border)] rounded-full px-5 py-2.5 hover:bg-[var(--glass-surface-elevated)] hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_4px_16px_0_var(--glass-shadow)]"
        >
          <div 
            className="text-xs text-[var(--text-secondary)]"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {bookName.toUpperCase()} {chapter} | <span style={{ fontFamily: "'Arimo', sans-serif" }}>{bookNameHebrew} {chapter}</span>
          </div>
        </button>
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
              {verse.hebrew.split(' ').map((word, wordIdx) => (
                <span key={wordIdx}>
                  <span 
                    onClick={() => onWordClick(word)} 
                    className="cursor-pointer hover:text-[var(--accent)] transition-colors duration-200"
                  >
                    {word}
                  </span>
                  {wordIdx < verse.hebrew.split(' ').length - 1 && ' '}
                </span>
              ))}
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