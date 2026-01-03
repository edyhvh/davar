import React, { useEffect, useState } from 'react';
import { DavarLogo } from './DavarLogo';

interface LaunchScreenProps {
  onComplete: () => void;
}

export function LaunchScreen({ onComplete }: LaunchScreenProps) {
  const [opacity, setOpacity] = useState(0);

  useEffect(() => {
    // Fade in animation
    const fadeIn = setTimeout(() => setOpacity(1), 100);
    
    // Auto transition after 2.5 seconds
    const autoTransition = setTimeout(() => {
      setOpacity(0);
      setTimeout(onComplete, 500);
    }, 2500);

    return () => {
      clearTimeout(fadeIn);
      clearTimeout(autoTransition);
    };
  }, [onComplete]);

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center transition-opacity duration-500"
      style={{
        background: 'linear-gradient(135deg, #0038B8 0%, #002B80 50%, #001F59 100%)',
        opacity,
      }}
    >
      <div className="max-w-md mx-auto w-full px-8">
        {/* Logo */}
        <div className="flex flex-col items-center space-y-8">
          <DavarLogo size="xl" variant="light" />
          
          {/* Title */}
          <div className="text-center space-y-2">
            <h1
              className="text-white"
              style={{
                fontFamily: "'Suez One', serif",
                fontSize: '28px',
                letterSpacing: '0.02em',
              }}
            >
              Phoenician Dalet
            </h1>
            <p
              className="text-white/80 text-sm"
              style={{
                fontFamily: "'Inter', sans-serif",
              }}
            >
              (first 3 uses)
            </p>
          </div>
        </div>

        {/* Bottom hint */}
        <div className="fixed bottom-12 left-0 right-0 text-center">
          <p
            className="text-white/60 text-sm"
            style={{
              fontFamily: "'Inter', sans-serif",
            }}
          >
            Swipe up/down
          </p>
        </div>
      </div>
    </div>
  );
}