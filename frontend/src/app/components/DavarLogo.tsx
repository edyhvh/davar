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

  // Use the border color (CSS variable) for the logo on main screens
  // For light mode: #D4D0C8 (warm gray), for dark mode: #3A3A3A (dark gray)
  // This filter converts the image to match the border color
  const filterStyle = 'brightness(0) saturate(100%) invert(85%) sepia(6%) saturate(289%) hue-rotate(357deg) brightness(92%) contrast(88%)';

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <img
        src={logoImage}
        alt="Davar Logo"
        style={{
          height: `${currentSize}px`,
          width: `${currentSize}px`,
          objectFit: 'contain',
          filter: filterStyle,
        }}
      />
    </div>
  );
}