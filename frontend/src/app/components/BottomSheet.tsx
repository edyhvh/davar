import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export function BottomSheet({ isOpen, onClose, children }: BottomSheetProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xl z-40 transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Bottom Sheet - Smaller with rounded top */}
      <div
        className="fixed inset-x-0 bottom-0 z-50 max-h-[70vh] animate-slide-up"
        style={{
          animation: isOpen ? 'slideUp 0.3s ease-out' : 'slideDown 0.3s ease-in',
        }}
      >
        <div className="relative bg-[var(--background)] rounded-t-[32px] shadow-[0_-16px_64px_0_rgba(0,0,0,0.2)]">
          
          {/* Handle bar */}
          <div className="relative flex justify-center pt-4 pb-2">
            <div className="w-12 h-1 rounded-full bg-[var(--border)] opacity-40" />
          </div>

          {/* Close button - rounded pill */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full border border-[var(--border)] hover:bg-[var(--muted)] transition-all"
            aria-label="Close"
          >
            <X className="w-4 h-4 text-[var(--text-secondary)]" />
          </button>

          {/* Content */}
          <div className="relative overflow-y-auto max-h-[65vh] px-6 pb-6">
            {children}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from {
            transform: translateY(100%);
          }
          to {
            transform: translateY(0);
          }
        }
        @keyframes slideDown {
          from {
            transform: translateY(0);
          }
          to {
            transform: translateY(100%);
          }
        }
      `}</style>
    </>
  );
}