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
    return (
      <span onClick={onClick} className="cursor-pointer">
        {word}
      </span>
    );
  }

  return (
    <span
      onClick={onClick}
      className={`cursor-pointer inline-block word-hint ${
        mounted ? "word-hint-active" : ""
      }`}
    >
      {word}
    </span>
  );
}