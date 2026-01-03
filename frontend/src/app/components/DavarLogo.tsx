import React from 'react';
import logoImage from 'figma:asset/5861301c21db3eba2e849dff80c99762eaaf3833.png';

interface DavarLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'light';
  className?: string;
  theme?: 'light' | 'dark';
}

export function DavarLogo({ size = 'md', variant = 'default', className = '', theme }: DavarLogoProps) {
  const sizes = {
    sm: { height: 24 },
    md: { height: 32 },
    lg: { height: 48 },
    xl: { height: 120 },
  };

  const currentSize = sizes[size];

  // Determine if we're in dark mode
  // Check if theme prop is provided, otherwise check CSS variable or variant
  const isDark = theme === 'dark' || variant === 'light';

  return (
    <div className={`flex items-center justify-center ${className}`}>
      {/* Logo image with background removed and theme-based color */}
      <img
        src={logoImage}
        alt="Davar Logo"
        style={{
          height: `${currentSize.height}px`,
          width: 'auto',
          // Remove blue background and colorize the white logo shape
          filter: isDark 
            ? 'brightness(0) saturate(100%) invert(87%) sepia(14%) saturate(524%) hue-rotate(357deg) brightness(95%) contrast(89%)' // #ebdbb2 warm cream
            : 'brightness(0) saturate(100%) invert(13%) sepia(95%) saturate(4736%) hue-rotate(219deg) brightness(94%) contrast(108%)', // #0038B8 tekhelet blue
          objectFit: 'contain',
          mixBlendMode: 'normal',
        }}
      />
    </div>
  );
}