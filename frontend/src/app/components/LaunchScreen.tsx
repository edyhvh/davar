import React, { useEffect, useState } from 'react';

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
        background: 'linear-gradient(180deg, #1C2254 0%, #2E347A 25%, #5C6199 50%, #8B7BA8 75%, #C9A896 100%)',
        opacity,
      }}
    >
      <div className="max-w-md mx-auto w-full px-8 text-center">
        {/* Davar in Hebrew */}
        <h1
          className="text-white mb-4"
          style={{
            fontFamily: "'Cardo', serif",
            fontSize: '72px',
            letterSpacing: '0.02em',
          }}
        >
          דבר
        </h1>
        
        {/* Subtitle */}
        <p
          className="text-white/90"
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: '18px',
            letterSpacing: '0.01em',
          }}
        >
          focus on what's really important
        </p>
      </div>
    </div>
  );
}