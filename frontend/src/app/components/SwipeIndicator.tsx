import React, { useState, useRef } from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface SwipeIndicatorProps {
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  children: React.ReactNode;
}

export function SwipeIndicator({ onSwipeUp, onSwipeDown, children }: SwipeIndicatorProps) {
  const [showIndicator, setShowIndicator] = useState(false);
  const longPressTimerRef = useRef<NodeJS.Timeout | null>(null);

  const handleTouchStart = () => {
    longPressTimerRef.current = setTimeout(() => {
      setShowIndicator(true);
      // Hide after 2 seconds
      setTimeout(() => setShowIndicator(false), 2000);
    }, 500); // 500ms long press
  };

  const handleTouchEnd = () => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }
  };

  const handleMouseDown = () => {
    longPressTimerRef.current = setTimeout(() => {
      setShowIndicator(true);
      // Hide after 2 seconds
      setTimeout(() => setShowIndicator(false), 2000);
    }, 500); // 500ms long press
  };

  const handleMouseUp = () => {
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }
  };

  return (
    <div className="relative">
      {/* Content */}
      <div
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {children}
      </div>

      {/* Swipe Indicator Overlay */}
      {showIndicator && (
        <div 
          className="absolute inset-0 pointer-events-none flex items-center justify-center"
          style={{
            animation: 'fadeIn 0.3s ease-in-out',
          }}
        >
          <style>
            {`
              @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
              }
              @keyframes pulseGlow {
                0%, 100% {
                  opacity: 0.4;
                  transform: scale(1);
                }
                50% {
                  opacity: 0.7;
                  transform: scale(1.1);
                }
              }
            `}
          </style>
          
          <div className="bg-[var(--glass-surface)] backdrop-blur-xl border border-[var(--glass-border)] rounded-2xl px-6 py-4 shadow-2xl">
            <div className="flex flex-col items-center gap-2">
              <ChevronUp 
                className="w-6 h-6 text-[var(--accent)]"
                style={{
                  animation: 'pulseGlow 1.5s ease-in-out infinite',
                }}
              />
              <div 
                className="text-xs text-[var(--text-secondary)]"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                Swipe to navigate
              </div>
              <ChevronDown 
                className="w-6 h-6 text-[var(--accent)]"
                style={{
                  animation: 'pulseGlow 1.5s ease-in-out infinite',
                  animationDelay: '0.75s',
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
