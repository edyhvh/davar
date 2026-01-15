import React from 'react';

interface NeumorphButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  disabled?: boolean;
}

export function NeumorphButton({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
}: NeumorphButtonProps) {
  const baseClasses = 'relative overflow-hidden transition-all duration-300 rounded-2xl';
  
  const variantClasses = {
    primary: `
      bg-gradient-to-br from-[var(--accent-from)] to-[var(--accent-to)]
      text-white 
      shadow-[6px_6px_16px_var(--neomorph-shadow-dark),-6px_-6px_16px_var(--neomorph-shadow-light)]
      hover:shadow-[4px_4px_12px_var(--neomorph-shadow-dark),-4px_-4px_12px_var(--neomorph-shadow-light)] hover:scale-[1.02]
      active:shadow-[inset_4px_4px_8px_var(--neomorph-inset-shadow-dark),inset_-4px_-4px_8px_var(--neomorph-inset-shadow-light)] active:scale-[0.98]
      border border-[var(--neomorph-border)]
      disabled:opacity-50 disabled:cursor-not-allowed
    `,
    secondary: `
      bg-[var(--neomorph-bg)]
      text-[var(--foreground)]
      border border-[var(--neomorph-border)]
      shadow-[6px_6px_16px_var(--neomorph-shadow-dark),-6px_-6px_16px_var(--neomorph-shadow-light)]
      hover:shadow-[4px_4px_12px_var(--neomorph-shadow-dark),-4px_-4px_12px_var(--neomorph-shadow-light)] hover:scale-[1.02]
      active:shadow-[inset_4px_4px_8px_var(--neomorph-inset-shadow-dark),inset_-4px_-4px_8px_var(--neomorph-inset-shadow-light)] active:scale-[0.98]
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
      <span className="relative">{children}</span>
    </button>
  );
}
