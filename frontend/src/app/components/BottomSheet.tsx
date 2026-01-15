import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
}

export function BottomSheet({ isOpen, onClose, children, title }: BottomSheetProps) {
  // Prevent scroll on body when bottom sheet is open
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

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/40 z-[200]"
            onClick={onClose}
          />

          {/* Bottom Sheet */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed bottom-0 left-0 right-0 z-[201] bg-[var(--neomorph-bg)] rounded-t-[32px] shadow-[0_-8px_32px_var(--neomorph-shadow-dark)] max-h-[80vh] flex flex-col"
          >
            {/* Handle bar */}
            <div className="flex justify-center pt-3 pb-2">
              <div 
                className="w-12 h-1.5 rounded-full bg-[var(--neomorph-border)]"
                style={{
                  boxShadow: 'inset 2px 2px 4px var(--neomorph-inset-shadow-dark), inset -2px -2px 4px var(--neomorph-inset-shadow-light)'
                }}
              />
            </div>

            {/* Title */}
            {title && (
              <div 
                className="px-6 py-3 text-center text-[var(--text-primary)]"
                style={{ fontFamily: "'Inter', sans-serif", fontSize: '18px', fontWeight: 600 }}
              >
                {title}
              </div>
            )}

            {/* Scrollable Content */}
            <div className="overflow-y-auto px-6 pb-8 pt-2">
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
