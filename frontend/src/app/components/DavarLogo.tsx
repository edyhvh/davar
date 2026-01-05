import React from 'react';
import logoImage from 'figma:asset/86a59e5984baacebd9e81429a4678e2e378e368b.png';

interface DavarLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'light';
  className?: string;
  theme?: 'light' | 'dark';
}

export function DavarLogo({ size = 'md', variant = 'default', className = '', theme }: DavarLogoProps) {
  const sizes = {
    sm: 48,
    md: 64,
    lg: 96,
    xl: 192,
  };

  const currentSize = sizes[size];

  // Determine if we're in dark mode
  const isDark = theme === 'dark' || variant === 'light';

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <img
        src={logoImage}
        alt="Davar Logo"
        style={{
          height: `${currentSize}px`,
          width: `${currentSize}px`,
          objectFit: 'contain',
          filter: isDark 
            ? 'brightness(0) saturate(100%) invert(87%) sepia(14%) saturate(524%) hue-rotate(357deg) brightness(95%) contrast(89%)' 
            : 'brightness(0) saturate(100%) invert(18%) sepia(43%) saturate(2093%) hue-rotate(226deg) brightness(91%) contrast(94%)',
        }}
      />
    </div>
  );
}