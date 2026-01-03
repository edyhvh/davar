import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export function GlassCard({
  children,
  className = '',
  onClick,
  hoverable = false,
}: GlassCardProps) {
  return (
    <div
      onClick={onClick}
      className={`
        relative
        bg-[var(--glass-surface)] 
        backdrop-blur-[40px]
        border border-[var(--glass-border)]
        rounded-2xl
        shadow-[0_8px_32px_0_var(--glass-shadow)]
        transition-all duration-300
        ${hoverable ? 'hover:shadow-[0_16px_48px_0_var(--glass-shadow)] hover:scale-[1.02] hover:bg-[var(--glass-surface-elevated)] cursor-pointer' : ''}
        ${className}
      `}
    >
      {/* Inner glass highlight - NEUTRAL ONLY (no color tint) */}
      <div className="absolute inset-0 bg-gradient-to-b from-[var(--glass-highlight)] via-transparent to-transparent rounded-2xl pointer-events-none" />
      <div className="relative">{children}</div>
    </div>
  );
}