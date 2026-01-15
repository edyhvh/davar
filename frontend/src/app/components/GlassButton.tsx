import React from 'react';

interface GlassButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
}

export function GlassButton({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
}: GlassButtonProps) {
  const baseClasses = 'relative overflow-hidden transition-all duration-300 rounded-2xl';
  
  const variantClasses = {
    primary: `
      bg-gradient-to-br from-[var(--accent-from)] to-[var(--accent-to)]
      text-white 
      shadow-[0_8px_24px_0_rgba(0,56,184,0.25)]
      hover:shadow-[0_12px_32px_0_rgba(0,56,184,0.35)] hover:scale-105
      active:scale-95
      border border-white/20
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    secondary: `
      bg-[var(--glass-surface)] backdrop-blur-[40px]
      text-[var(--foreground)]
      border border-[var(--glass-border)]
      shadow-[0_8px_32px_0_var(--glass-shadow)]
      hover:bg-[var(--glass-surface-elevated)] hover:shadow-[0_12px_40px_0_var(--glass-shadow)] hover:scale-102
      active:scale-98
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-5 py-2.5 text-base',
    lg: 'px-7 py-3.5 text-lg',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
      style={{ fontFamily: "'Inter', sans-serif" }}
    >
      {/* Inner glass highlight - NEUTRAL (no color) */}
      <span className="absolute inset-0 bg-gradient-to-b from-white/10 via-transparent to-black/5 pointer-events-none" />
      <span className="relative">{children}</span>
    </button>
  );
}