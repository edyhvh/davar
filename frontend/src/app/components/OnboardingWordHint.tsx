import React, { useState, useEffect } from 'react';

interface OnboardingWordHintProps {
  word: string;
  isActive: boolean;
  onClick: () => void;
}

export function OnboardingWordHint({ word, isActive, onClick }: OnboardingWordHintProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!isActive) {
    return <span onClick={onClick} className="cursor-pointer">{word}</span>;
  }

  return (
    <span className="relative inline-block">
      <style>
        {`
          @keyframes copperBreathing {
            0%, 100% {
              transform: scale(1);
              filter: drop-shadow(0 0 12px rgba(205, 127, 50, 0.4));
            }
            50% {
              transform: scale(1.1);
              filter: drop-shadow(0 0 20px rgba(205, 127, 50, 0.7));
            }
          }
        `}
      </style>
      
      <span
        onClick={onClick}
        className="cursor-pointer inline-block transition-all"
        style={{
          animation: mounted ? 'copperBreathing 2.5s ease-in-out infinite' : 'none',
          color: '#B87333',
          backgroundColor: 'rgba(184, 115, 51, 0.08)',
          borderRadius: '8px',
          padding: '2px 8px',
        }}
      >
        {word}
      </span>
    </span>
  );
}