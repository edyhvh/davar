import React, { useState, useEffect } from 'react';
import { X, ChevronLeft } from 'lucide-react';

interface ChapterVerseSelectorProps {
  book: string;
  currentChapter: number;
  currentVerse: number;
  onSelect: (chapter: number, verse: number) => void;
  onClose: () => void;
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

export function ChapterVerseSelector({
  book,
  currentChapter,
  currentVerse,
  onSelect,
  onClose,
}: ChapterVerseSelectorProps) {
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);

  const chapterCount = getChapterCount(book);
  const chapters = Array.from({ length: chapterCount }, (_, i) => i + 1);

  // Lock body scroll when bottom sheet is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const handleChapterSelect = (chapter: number) => {
    setSelectedChapter(chapter);
  };

  const handleVerseSelect = (verse: number) => {
    if (selectedChapter) {
      onSelect(selectedChapter, verse);
      onClose();
    }
  };

  const verseCount = selectedChapter ? getVerseCount(book, selectedChapter) : 0;
  const verses = selectedChapter ? Array.from({ length: verseCount }, (_, i) => i + 1) : [];

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xl z-40 transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Bottom Sheet */}
      <div
        className="fixed inset-x-0 bottom-0 z-50 max-h-[75vh] animate-slide-up"
        style={{
          animation: 'slideUp 0.3s ease-out',
        }}
      >
        <div className="relative bg-[var(--background)] rounded-t-[32px] shadow-[0_-16px_64px_0_rgba(0,0,0,0.2)]">
          
          {/* Handle bar */}
          <div className="relative flex justify-center pt-4 pb-2">
            <div className="w-12 h-1 rounded-full bg-[var(--border)] opacity-40" />
          </div>

          {/* Header */}
          <div className="px-6 pb-3 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {selectedChapter && (
                <button
                  onClick={() => setSelectedChapter(null)}
                  className="p-1.5 -ml-2 rounded-full hover:bg-[var(--muted)] transition-colors"
                  aria-label="Back to chapters"
                >
                  <ChevronLeft 
                    className="w-5 h-5 text-[var(--text-secondary)]"
                  />
                </button>
              )}
              <h2 
                className="text-[var(--text-secondary)] text-lg font-semibold"
                style={{ 
                  fontFamily: "'Inter', sans-serif",
                }}
              >
                {selectedChapter ? `Chapter ${selectedChapter}` : book}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-full border border-[var(--border)] hover:bg-[var(--muted)] transition-all"
              aria-label="Close"
            >
              <X className="w-4 h-4 text-[var(--text-secondary)]" />
            </button>
          </div>

          {/* Number Grid - Compact and rounded */}
          <div className="overflow-y-auto max-h-[60vh] px-6 pb-6">
            {!selectedChapter ? (
              // Chapter Selection - Compact rounded pills
              <div className="grid grid-cols-6 gap-2 pb-6 pt-2 px-1">
                {chapters.map((chapter) => (
                  <button
                    key={chapter}
                    onClick={() => handleChapterSelect(chapter)}
                    className={`
                      aspect-square rounded-full transition-all flex items-center justify-center border-2
                      hover:scale-110 active:scale-95
                      ${chapter === currentChapter 
                        ? 'bg-[var(--primary)] border-[var(--primary)] text-white' 
                        : 'bg-[var(--background)] border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--muted)] hover:border-[var(--text-secondary)]'
                      }
                    `}
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '14px',
                      fontWeight: 600,
                    }}
                  >
                    {chapter}
                  </button>
                ))}
              </div>
            ) : (
              // Verse Selection - Compact rounded pills
              <div className="grid grid-cols-6 gap-2 pb-6 pt-2 px-1">
                {verses.map((verse) => (
                  <button
                    key={verse}
                    onClick={() => handleVerseSelect(verse)}
                    className={`
                      aspect-square rounded-full transition-all flex items-center justify-center border-2
                      hover:scale-110 active:scale-95
                      ${verse === currentVerse && selectedChapter === currentChapter
                        ? 'bg-[var(--primary)] border-[var(--primary)] text-white' 
                        : 'bg-[var(--background)] border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--muted)] hover:border-[var(--text-secondary)]'
                      }
                    `}
                    style={{
                      fontFamily: "'Inter', sans-serif",
                      fontSize: '14px',
                      fontWeight: 600,
                    }}
                  >
                    {verse}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from {
            transform: translateY(100%);
          }
          to {
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  );
}