import React, { useEffect, useState } from 'react';
import { DavarLogo } from './DavarLogo';

interface LaunchScreenProps {
  onComplete: () => void;
  language: 'en' | 'es' | 'he';
}

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
        background: 'linear-gradient(135deg, #FDFDF9 0%, #F8F7F3 50%, #A8C8F0 100%)',
        opacity,
      }}
    >
      <div className="max-w-md mx-auto w-full px-8 text-center">
        {/* Logo with breathing animation */}
        <div className="animate-breathe">
          <DavarLogo size="xl" variant="light" />
        </div>
      </div>

      <style>{`
        @keyframes breathe {
          0%, 100% {
            transform: scale(1);
            opacity: 0.9;
          }
          50% {
            transform: scale(1.05);
            opacity: 1;
          }
        }

        .animate-breathe {
          animation: breathe 2.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
