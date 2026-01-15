import React from 'react';
import { Home, Search, Settings } from 'lucide-react';

interface BottomNavBarProps {
  onHomeClick?: () => void;
  onChapterVerseClick?: () => void;
  onSettingsClick?: () => void;
}

export function BottomNavBar({ onHomeClick, onChapterVerseClick, onSettingsClick }: BottomNavBarProps) {
  return (
    <div className="fixed bottom-0 left-0 right-0 z-30">
      <div className="max-w-md mx-auto px-6 pb-6">
        <nav 
          className="relative rounded-full p-2 bg-[var(--background)]"
        >
          <div className="relative flex items-center justify-around">
            {/* Home Button (Left) */}
            <button
              onClick={onHomeClick}
              className="p-4 rounded-full hover:bg-[var(--muted)] transition-all hover:scale-110 active:scale-95"
              aria-label="Home"
            >
              <Home className="w-5 h-5 text-[var(--text-secondary)]" />
            </button>

            {/* Main Action Button - Tekhelet ACCENT ONLY */}
            <button
              onClick={onChapterVerseClick}
              className="relative bg-gradient-to-br from-[var(--accent-from)] to-[var(--accent-to)] p-5 rounded-full shadow-[0_8px_24px_0_rgba(65,105,225,0.35)] hover:shadow-[0_12px_32px_0_rgba(65,105,225,0.45)] hover:scale-110 active:scale-95 transition-all"
              aria-label="Chapter & Verse"
            >
              {/* Inner glow */}
              <div className="absolute inset-0 bg-gradient-to-b from-white/20 via-transparent to-black/10 rounded-full" />
              <Search className="relative w-6 h-6 text-white" />
            </button>

            {/* Settings Button (Right) */}
            <button
              onClick={onSettingsClick}
              className="p-4 rounded-full hover:bg-[var(--muted)] transition-all hover:scale-110 active:scale-95"
              aria-label="Settings"
            >
              <Settings className="w-5 h-5 text-[var(--text-secondary)]" />
            </button>
          </div>
        </nav>
      </div>
    </div>
  );
}