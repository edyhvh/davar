import React from 'react';
import { GlassCard } from './GlassCard';
import { GlassButton } from './GlassButton';
import { DavarLogo } from './DavarLogo';
import { ChevronDown } from 'lucide-react';

interface NavigationSelectorProps {
  book: string;
  chapter: number;
  verse: number;
  onBookChange: (book: string) => void;
  onChapterChange: (chapter: number) => void;
  onVerseChange: (verse: number) => void;
  onClose: () => void;
}

const books = [
  'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
  'Joshua', 'Judges', 'Ruth', 'Samuel', 'Kings',
  'Isaiah', 'Jeremiah', 'Ezekiel', 'Hosea', 'Joel',
  'Psalms', 'Proverbs', 'Job', 'Song of Songs', 'Ecclesiastes',
];

export function NavigationSelector({
  book,
  chapter,
  verse,
  onBookChange,
  onChapterChange,
  onVerseChange,
  onClose,
}: NavigationSelectorProps) {
  return (
    <div className="space-y-6">
      {/* Section: Book/Chapter/Verse */}
      <div className="space-y-3">
        <h3 className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          Navigation
        </h3>
        
        <GlassCard className="p-4">
          <div className="space-y-3">
            {/* Book/Chapter/Verse Selector */}
            <div className="relative">
              <select
                value={`${book}-${chapter}-${verse}`}
                onChange={(e) => {
                  const [newBook, newChapter, newVerse] = e.target.value.split('-');
                  onBookChange(newBook);
                  onChapterChange(Number(newChapter));
                  onVerseChange(Number(newVerse));
                }}
                className="w-full bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-xl px-4 py-3 pr-10 appearance-none cursor-pointer"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                <option value="Genesis-1-1">Genesis 1:1</option>
                <option value="Genesis-1-2">Genesis 1:2</option>
                <option value="Genesis-1-3">Genesis 1:3</option>
                <option value="Psalms-23-1">Psalms 23:1</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--text-secondary)] pointer-events-none" />
            </div>

            {/* Book Selector with Logo */}
            <div className="flex items-center gap-3 pt-2">
              <div className="flex-shrink-0">
                <DavarLogo size="sm" />
              </div>
              <div className="flex-1">
                <div className="text-xs text-[var(--muted-foreground)] mb-1" style={{ fontFamily: "'Inter', sans-serif" }}>
                  Sefer (Book)
                </div>
                <div
                  className="text-sm"
                  style={{
                    fontFamily: "'Arimo', sans-serif",
                    direction: 'rtl',
                  }}
                >
                  בְּרֵאשִׁית
                </div>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Section: Text Display */}
      <div className="space-y-3">
        <h3 className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          Text Primary
        </h3>
        
        <GlassCard className="p-4">
          <div className="space-y-2">
            <div className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Hebrew Script
            </div>
            <div
              style={{
                fontFamily: "'Cardo', serif",
                fontSize: '22px',
                direction: 'rtl',
              }}
            >
              Cardo 22-24px
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-4">
          <div className="space-y-2">
            <div className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              Ancient Texts
            </div>
            <div
              className="text-[var(--text-secondary)]"
              style={{
                fontFamily: "'DeadSeaScrolls-Regular', 'Cardo', serif",
                fontSize: '20px',
                direction: 'rtl',
              }}
            >
              Qumran
            </div>
            <div className="relative">
              <select
                className="w-full bg-[var(--input-background)] backdrop-blur-sm border border-[var(--glass-border)] rounded-xl px-4 py-2 pr-10 appearance-none text-sm cursor-pointer"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                <option>DeadSeaScrolls-Regular</option>
                <option>Cardo</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-secondary)] pointer-events-none" />
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Section: UI Text */}
      <div className="space-y-3">
        <h3 className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          Text Secondary
        </h3>
        
        <GlassCard className="p-4">
          <div className="space-y-2">
            <div className="text-xs text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              UI Hebrew
            </div>
            <div
              style={{
                fontFamily: "'Arimo', sans-serif",
                fontSize: '14px',
                direction: 'rtl',
              }}
            >
              Arimo 14-16px
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Section: Logo */}
      <div className="space-y-3">
        <h3 className="text-sm text-[var(--muted-foreground)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          Logo
        </h3>
        
        <GlassCard className="p-4">
          <div className="space-y-2">
            <div
              style={{
                fontFamily: "'Suez One', serif",
                fontSize: '18px',
              }}
            >
              Lap Suez One + bold serif
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Done Button */}
      <GlassButton
        variant="primary"
        size="lg"
        onClick={onClose}
        className="w-full"
      >
        Done
      </GlassButton>
    </div>
  );
}
