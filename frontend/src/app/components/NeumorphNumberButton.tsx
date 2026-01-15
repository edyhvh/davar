import React from 'react';

interface NeumorphNumberButtonProps {
  number: number;
  isSelected: boolean;
  onClick: () => void;
}

export function NeumorphNumberButton({ number, isSelected, onClick }: NeumorphNumberButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        relative w-full aspect-square rounded-3xl transition-all duration-300
        ${isSelected 
          ? 'bg-gradient-to-br from-[var(--accent-from)] to-[var(--accent-to)] text-white shadow-[inset_3px_3px_8px_rgba(0,0,0,0.2),inset_-3px_-3px_8px_rgba(255,255,255,0.1)] scale-95' 
          : 'bg-[var(--neomorph-bg)] text-[var(--text-primary)] shadow-[6px_6px_12px_var(--neomorph-shadow-dark),-6px_-6px_12px_var(--neomorph-shadow-light)] hover:shadow-[4px_4px_8px_var(--neomorph-shadow-dark),-4px_-4px_8px_var(--neomorph-shadow-light)] active:shadow-[inset_3px_3px_6px_var(--neomorph-inset-shadow-dark),inset_-3px_-3px_6px_var(--neomorph-inset-shadow-light)] active:scale-95'
        }
      `}
      style={{
        fontFamily: "'Inter', sans-serif",
        fontSize: '28px',
        fontWeight: 600,
      }}
    >
      {number}
    </button>
  );
}
