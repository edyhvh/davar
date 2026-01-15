import React from 'react';
import { GlassCard } from './GlassCard';

interface NavigationBarProps {
  book: string;
  chapter: number;
  verse: number;
  onBookChange: (book: string) => void;
  onChapterChange: (chapter: number) => void;
  onVerseChange: (verse: number) => void;
}

export function NavigationBar({
  book,
  chapter,
  verse,
  onBookChange,
  onChapterChange,
  onVerseChange,
}: NavigationBarProps) {
  const books = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Psalms', 'Isaiah'];
  const chapters = Array.from({ length: 50 }, (_, i) => i + 1);
  const verses = Array.from({ length: 30 }, (_, i) => i + 1);

  return (
    <GlassCard className="p-3">
      <div className="flex items-center justify-center gap-3">
        {/* Book Selector */}
        <select
          value={book}
          onChange={(e) => onBookChange(e.target.value)}
          className="bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
          style={{ fontFamily: "'Arimo', sans-serif" }}
        >
          {books.map((b) => (
            <option key={b} value={b}>
              {b}
            </option>
          ))}
        </select>

        {/* Chapter Selector */}
        <select
          value={chapter}
          onChange={(e) => onChapterChange(Number(e.target.value))}
          className="bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          {chapters.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <span className="text-[var(--text-secondary)]">:</span>

        {/* Verse Selector */}
        <select
          value={verse}
          onChange={(e) => onVerseChange(Number(e.target.value))}
          className="bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--primary)] transition-all"
          style={{ fontFamily: "'Inter', sans-serif" }}
        >
          {verses.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </select>
      </div>
    </GlassCard>
  );
}
