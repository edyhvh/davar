import React from 'react';

interface NeumorphCardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
  inset?: boolean;
}

export function NeumorphCard({
  children,
  className = '',
  onClick,
  hoverable = false,
  inset = false,
}: NeumorphCardProps) {
  return (
    <div
      onClick={onClick}
      className={`
        relative
        bg-[var(--neomorph-bg)] 
        border border-[var(--neomorph-border)]
        rounded-2xl
        ${inset 
          ? 'shadow-[inset_6px_6px_12px_var(--neomorph-inset-shadow-dark),inset_-6px_-6px_12px_var(--neomorph-inset-shadow-light)]' 
          : 'shadow-[6px_6px_16px_var(--neomorph-shadow-dark),-6px_-6px_16px_var(--neomorph-shadow-light)]'
        }
        transition-all duration-300
        ${hoverable ? 'hover:shadow-[4px_4px_12px_var(--neomorph-shadow-dark),-4px_-4px_12px_var(--neomorph-shadow-light)] hover:scale-[1.02] cursor-pointer' : ''}
        ${className}
      `}
    >
      <div className="relative">{children}</div>
    </div>
  );
}
