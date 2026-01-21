import React from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface VerticalSwipeIndicatorsProps {
  showUpIndicator?: boolean;
  showDownIndicator?: boolean;
}

export function VerticalSwipeIndicators({ 
  showUpIndicator = true, 
  showDownIndicator = true 
}: VerticalSwipeIndicatorsProps) {
  return (
    <>
      {/* Swipe Up Indicator (Previous Verse) */}
      {showUpIndicator && (
        <div 
          className="absolute top-24 left-1/2 -translate-x-1/2 pointer-events-none z-10"
          style={{
            animation: 'bounceUp 2s ease-in-out infinite',
          }}
        >
          <div className="flex flex-col items-center gap-1">
            <ChevronUp 
              className="w-6 h-6 opacity-30"
              style={{ color: 'var(--text-secondary)' }}
            />
            <ChevronUp 
              className="w-6 h-6 -mt-4 opacity-20"
              style={{ color: 'var(--text-secondary)' }}
            />
          </div>
        </div>
      )}

      {/* Swipe Down Indicator (Next Verse) */}
      {showDownIndicator && (
        <div 
          className="absolute bottom-24 left-1/2 -translate-x-1/2 pointer-events-none z-10"
          style={{
            animation: 'bounceDown 2s ease-in-out infinite',
          }}
        >
          <div className="flex flex-col items-center gap-1">
            <ChevronDown 
              className="w-6 h-6 -mb-4 opacity-20"
              style={{ color: 'var(--text-secondary)' }}
            />
            <ChevronDown 
              className="w-6 h-6 opacity-30"
              style={{ color: 'var(--text-secondary)' }}
            />
          </div>
        </div>
      )}

      <style>{`
        @keyframes bounceUp {
          0%, 100% {
            transform: translateY(0);
            opacity: 0.6;
          }
          50% {
            transform: translateY(-8px);
            opacity: 0.3;
          }
        }

        @keyframes bounceDown {
          0%, 100% {
            transform: translateY(0);
            opacity: 0.6;
          }
          50% {
            transform: translateY(8px);
            opacity: 0.3;
          }
        }
      `}</style>
    </>
  );
}
