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
      {/* Backdrop with HEAVY blur - NEUTRAL */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xl z-40 transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Bottom Sheet - HEAVY Liquid Glass NEUTRAL */}
      <div
        className="fixed inset-x-0 bottom-0 z-50 max-h-[85vh] animate-slide-up"
        style={{
          animation: isOpen ? 'slideUp 0.3s ease-out' : 'slideDown 0.3s ease-in',
        }}
      >
        <div className="relative bg-[var(--glass-surface-elevated)] backdrop-blur-[40px] border-t-2 border-[var(--glass-border)] rounded-t-[32px] shadow-[0_-16px_64px_0_var(--glass-shadow)]">
          {/* Inner glass highlight - NEUTRAL ONLY */}
          <div className="absolute inset-0 bg-gradient-to-b from-[var(--glass-highlight)] via-transparent to-transparent rounded-t-[32px] pointer-events-none" />
          
          {/* Handle bar - Tekhelet accent */}
          <div className="relative flex justify-center pt-5 pb-3">
            <div className="w-16 h-2 bg-[var(--accent)]/20 rounded-full shadow-inner" />
          </div>

          {/* Close button - NEUTRAL glass */}
          <button
            onClick={onClose}
            className="absolute top-6 right-6 p-3 rounded-2xl bg-[var(--glass-surface)] backdrop-blur-[40px] border border-[var(--glass-border)] hover:bg-[var(--glass-surface-elevated)] transition-all hover:scale-110 active:scale-95 shadow-[0_4px_16px_0_var(--glass-shadow)]"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-[var(--text-secondary)]" />
          </button>

          {/* Content */}
          <div className="relative overflow-y-auto max-h-[80vh] px-6 pb-8">
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