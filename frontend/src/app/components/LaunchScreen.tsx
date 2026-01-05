import React, { useEffect, useState } from 'react';
import { DavarLogo } from './DavarLogo';

interface LaunchScreenProps {
  onComplete: () => void;
  language: 'en' | 'es' | 'he';
}

const subtitles = {
  en: 'searching his word',
  es: 'escudriñando su palabra',
  he: 'חוקר את דברו',
};

export function LaunchScreen({ onComplete, language }: LaunchScreenProps) {
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
        background: 'linear-gradient(180deg, #1C2254 0%, #252B6B 33%, #2E347A 66%, #5C6199 100%)',
        opacity,
      }}
    >
      <div className="max-w-md mx-auto w-full px-8 text-center">
        {/* Logo */}
        <div className="mb-6">
          <DavarLogo size="xl" variant="light" />
        </div>
        
        {/* Subtitle */}
        <p
          className="text-white/90"
          style={{
            fontFamily: language === 'he' ? "'Cardo', serif" : "'Inter', sans-serif",
            fontSize: '18px',
            letterSpacing: '0.01em',
            direction: language === 'he' ? 'rtl' : 'ltr',
          }}
        >
          {subtitles[language]}
        </p>
      </div>
    </div>
  );
}