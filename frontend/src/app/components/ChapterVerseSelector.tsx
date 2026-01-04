import React, { useState } from 'react';
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
      {/* Header - Retro minimal with border */}
      <div 
        className="sticky top-0 z-10 border-b-2"
        style={{ 
          backgroundColor: 'var(--background)',
          borderColor: 'var(--foreground)',
        }}
      >
        <div className="relative max-w-md mx-auto px-6 py-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {selectedChapter && (
              <button
                onClick={() => setSelectedChapter(null)}
                className="p-1.5 -ml-2 rounded-lg hover:bg-[var(--muted)] transition-colors"
                aria-label="Back to chapters"
              >
                <ChevronLeft 
                  className="w-6 h-6" 
                  style={{ color: 'var(--foreground)' }} 
                />
              </button>
            )}
            <h2 
              style={{ 
                fontFamily: "'Courier New', monospace",
                fontWeight: 700,
                fontSize: '20px',
                color: 'var(--foreground)',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {selectedChapter ? `Chapter ${selectedChapter}` : book}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full border-2 flex items-center justify-center hover:bg-[var(--muted)] transition-colors"
            style={{ 
              borderColor: 'var(--foreground)',
            }}
            aria-label="Close"
          >
            <X 
              className="w-4 h-4" 
              style={{ color: 'var(--foreground)' }} 
            />
          </button>
        </div>
      </div>

      {/* Chapter or Verse Grid - Retro sketch style */}
      <div className="max-w-md mx-auto px-5 py-8">
        {!selectedChapter ? (
          // Chapter Selection - Retro grid with borders
          <div className="grid grid-cols-5 gap-3 pb-24">
            {chapters.map((chapter) => (
              <button
                key={chapter}
                onClick={() => handleChapterSelect(chapter)}
                className="aspect-square rounded-lg transition-all flex items-center justify-center border-2"
                style={{
                  backgroundColor: chapter === currentChapter 
                    ? 'var(--foreground)' 
                    : 'var(--background)',
                  borderColor: 'var(--foreground)',
                  color: chapter === currentChapter 
                    ? 'var(--background)' 
                    : 'var(--foreground)',
                  fontFamily: "'Courier New', monospace",
                  fontSize: '18px',
                  fontWeight: 700,
                  transform: 'scale(1)',
                }}
                onMouseEnter={(e) => {
                  if (chapter !== currentChapter) {
                    e.currentTarget.style.backgroundColor = 'var(--muted)';
                    e.currentTarget.style.transform = 'scale(1.05)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (chapter !== currentChapter) {
                    e.currentTarget.style.backgroundColor = 'var(--background)';
                    e.currentTarget.style.transform = 'scale(1)';
                  }
                }}
              >
                {chapter}
              </button>
            ))}
          </div>
        ) : (
          // Verse Selection - Retro grid with borders
          <div className="space-y-4">
            <div className="grid grid-cols-5 gap-3 pb-24">
              {verses.map((verse) => (
                <button
                  key={verse}
                  onClick={() => handleVerseSelect(verse)}
                  className="aspect-square rounded-lg transition-all flex items-center justify-center border-2"
                  style={{
                    backgroundColor: verse === currentVerse && selectedChapter === currentChapter
                      ? 'var(--foreground)' 
                      : 'var(--background)',
                    borderColor: 'var(--foreground)',
                    color: verse === currentVerse && selectedChapter === currentChapter
                      ? 'var(--background)' 
                      : 'var(--foreground)',
                    fontFamily: "'Courier New', monospace",
                    fontSize: '18px',
                    fontWeight: 700,
                    transform: 'scale(1)',
                  }}
                  onMouseEnter={(e) => {
                    if (!(verse === currentVerse && selectedChapter === currentChapter)) {
                      e.currentTarget.style.backgroundColor = 'var(--muted)';
                      e.currentTarget.style.transform = 'scale(1.05)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!(verse === currentVerse && selectedChapter === currentChapter)) {
                      e.currentTarget.style.backgroundColor = 'var(--background)';
                      e.currentTarget.style.transform = 'scale(1)';
                    }
                  }}
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