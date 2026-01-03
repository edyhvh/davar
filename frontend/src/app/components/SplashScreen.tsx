import React, { useEffect } from 'react';

interface SplashScreenProps {
  onComplete?: () => void;
  duration?: number;
}

export function SplashScreen({ onComplete, duration = 2500 }: SplashScreenProps) {
  useEffect(() => {
    if (onComplete) {
      const timer = setTimeout(onComplete, duration);
      return () => clearTimeout(timer);
    }
  }, [onComplete, duration]);

  return (
    <div className="fixed inset-0 bg-[var(--background)] flex items-center justify-center z-50">
      {/* Phoenician Dalet Logo with Tekhelet Gradient */}
      <div className="animate-breathe">
        <svg
          width="120"
          height="120"
          viewBox="0 0 120 120"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Tekhelet Blue Gradient: #0038B8 → #002B80 → #001F59 */}
            <linearGradient id="tekheletGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0038B8" />
              <stop offset="50%" stopColor="#002B80" />
              <stop offset="100%" stopColor="#001F59" />
            </linearGradient>
            
            {/* Subtle glow filter */}
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          {/* Phoenician Dalet (ד) - Minimalist form */}
          <path
            d="M 30 30 L 90 30 L 90 40 L 80 40 L 80 90 L 65 90 L 65 40 L 30 40 Z"
            fill="url(#tekheletGradient)"
            filter="url(#glow)"
          />
        </svg>
      </div>

      {/* App Name - Reverent Typography */}
      <div 
        className="absolute bottom-32 text-3xl tracking-wide opacity-60"
        style={{ fontFamily: "'Suez One', serif" }}
      >
        דבר
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
