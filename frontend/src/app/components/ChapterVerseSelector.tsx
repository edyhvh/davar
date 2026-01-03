import React, { useState } from 'react';
import { X } from 'lucide-react';

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
    <div className="fixed inset-0 z-50 bg-[var(--background)]">
      {/* Header with HEAVY NEUTRAL glass */}
      <div className="sticky top-0 z-10 bg-[var(--glass-surface-elevated)] backdrop-blur-[40px] border-b-2 border-[var(--glass-border)] shadow-[0_8px_32px_0_var(--glass-shadow)]">
        <div className="relative max-w-md mx-auto px-6 py-5 flex items-center justify-between">
          {/* Inner glass highlight - NEUTRAL */}
          <div className="absolute inset-0 bg-gradient-to-b from-[var(--glass-highlight)] via-transparent to-transparent pointer-events-none" />
          
          <h2 
            className="relative text-lg font-medium"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {selectedChapter ? `Chapter ${selectedChapter}` : book}
          </h2>
          <button
            onClick={onClose}
            className="relative p-3 rounded-2xl bg-[var(--glass-surface)] backdrop-blur-[40px] border border-[var(--glass-border)] hover:bg-[var(--glass-surface-elevated)] transition-all hover:scale-110 active:scale-95 shadow-[0_4px_16px_0_var(--glass-shadow)]"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-[var(--text-secondary)]" />
          </button>
        </div>
      </div>

      {/* Chapter or Verse Grid */}
      <div className="max-w-md mx-auto px-6 py-6">
        {!selectedChapter ? (
          // Chapter Selection - Chessboard Grid with NEUTRAL glass
          <div className="grid grid-cols-6 gap-2 pb-24">
            {chapters.map((chapter) => (
              <button
                key={chapter}
                onClick={() => handleChapterSelect(chapter)}
                className={`
                  aspect-square rounded-xl transition-all flex items-center justify-center font-medium
                  ${chapter === currentChapter 
                    ? 'bg-[var(--accent)] text-white shadow-lg' 
                    : 'bg-[var(--glass-surface)] backdrop-blur-[40px] border border-[var(--glass-border)] text-[var(--foreground)] hover:bg-[var(--muted)] hover:scale-105 active:scale-95'
                  }
                `}
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {chapter}
              </button>
            ))}
          </div>
        ) : (
          // Verse Selection - Chessboard Grid with NEUTRAL glass
          <div className="space-y-4">
            <button
              onClick={() => setSelectedChapter(null)}
              className="text-sm text-[var(--accent)] hover:underline"
              style={{ fontFamily: "'Inter', sans-serif" }}
            >
              ← Back to Chapters
            </button>
            <div className="grid grid-cols-6 gap-2 pb-24">
              {verses.map((verse) => (
                <button
                  key={verse}
                  onClick={() => handleVerseSelect(verse)}
                  className={`
                    aspect-square rounded-xl transition-all flex items-center justify-center font-medium
                    ${verse === currentVerse && selectedChapter === currentChapter
                      ? 'bg-[var(--accent)] text-white shadow-lg' 
                      : 'bg-[var(--glass-surface)] backdrop-blur-[40px] border border-[var(--glass-border)] text-[var(--foreground)] hover:bg-[var(--muted)] hover:scale-105 active:scale-95'
                    }
                  `}
                  style={{ fontFamily: "'Inter', sans-serif" }}
                >
                  {verse}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}