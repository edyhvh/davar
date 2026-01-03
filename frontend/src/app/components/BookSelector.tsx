import React from 'react';
import { GlassCard } from './GlassCard';
import { X } from 'lucide-react';

interface BookSelectorProps {
  currentBook: string;
  onBookSelect: (book: string) => void;
  onClose: () => void;
  language: 'en' | 'es';
}

const booksData = [
  { en: 'Genesis', es: 'Génesis', he: 'בראשית' },
  { en: 'Exodus', es: 'Éxodo', he: 'שמות' },
  { en: 'Leviticus', es: 'Levítico', he: 'ויקרא' },
  { en: 'Numbers', es: 'Números', he: 'במדבר' },
  { en: 'Deuteronomy', es: 'Deuteronomio', he: 'דברים' },
  { en: 'Joshua', es: 'Josué', he: 'יהושע' },
  { en: 'Judges', es: 'Jueces', he: 'שופטים' },
  { en: 'Ruth', es: 'Rut', he: 'רות' },
  { en: 'Samuel', es: 'Samuel', he: 'שמואל' },
  { en: 'Kings', es: 'Reyes', he: 'מלכים' },
  { en: 'Isaiah', es: 'Isaías', he: 'ישעיהו' },
  { en: 'Jeremiah', es: 'Jeremías', he: 'ירמיהו' },
  { en: 'Ezekiel', es: 'Ezequiel', he: 'יחזקאל' },
  { en: 'Hosea', es: 'Oseas', he: 'הושע' },
  { en: 'Joel', es: 'Joel', he: 'יואל' },
  { en: 'Psalms', es: 'Salmos', he: 'תהלים' },
  { en: 'Proverbs', es: 'Proverbios', he: 'משלי' },
  { en: 'Job', es: 'Job', he: 'איוב' },
  { en: 'Song of Songs', es: 'Cantar de los Cantares', he: 'שיר השירים' },
  { en: 'Ecclesiastes', es: 'Eclesiastés', he: 'קהלת' },
];

export function BookSelector({ currentBook, onBookSelect, onClose, language }: BookSelectorProps) {
  return (
    <div className="fixed inset-0 z-50 bg-[var(--background)]">
      {/* Header with HEAVY NEUTRAL glass */}
      <div className="sticky top-0 z-10 bg-[var(--glass-surface-elevated)] backdrop-blur-[40px] border-b-2 border-[var(--glass-border)] shadow-[0_8px_32px_0_var(--glass-shadow)]">
        <div className="relative max-w-md mx-auto px-6 py-5 flex items-center justify-between">
          {/* Inner glass highlight - NEUTRAL */}
          <div className="absolute inset-0 bg-gradient-to-b from-[var(--glass-highlight)] via-transparent to-transparent pointer-events-none" />
          
          <h2 
            className="relative text-lg font-medium"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Select Book
          </h2>
          <button
            onClick={onClose}
            className="relative p-3 rounded-2xl bg-[var(--glass-surface)] backdrop-blur-[40px] border border-[var(--glass-border)] hover:bg-[var(--glass-surface-elevated)] transition-all hover:scale-110 active:scale-95 shadow-[0_4px_16px_0_var(--glass-shadow)]"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-[var(--text-secondary)]" />
          </button>
        </div>
      </div>

      {/* Book Grid */}
      <div className="max-w-md mx-auto px-6 py-6">
        <div className="space-y-3 pb-24">
          {booksData.map((book) => {
            const isSelected = book.en === currentBook;
            return (
              <button
                key={book.en}
                onClick={() => {
                  onBookSelect(book.en);
                  onClose();
                }}
                className={`
                  w-full p-6 rounded-2xl transition-all text-left
                  ${isSelected 
                    ? 'bg-[var(--accent)] text-white shadow-lg scale-[1.02]' 
                    : 'bg-[var(--glass-surface)] backdrop-blur-[40px] border border-[var(--glass-border)] hover:bg-[var(--glass-surface-elevated)] hover:scale-[1.01] active:scale-[0.99]'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div 
                      className={`text-lg font-medium mb-1 ${isSelected ? 'text-white' : 'text-[var(--foreground)]'}`}
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {book.en.toUpperCase()}
                    </div>
                    <div 
                      className={`text-sm ${isSelected ? 'text-white/80' : 'text-[var(--text-secondary)]'}`}
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {language === 'es' ? book.es : book.en}
                    </div>
                  </div>
                  <div 
                    className={`text-2xl ${isSelected ? 'text-white' : 'text-[var(--text-hebrew)]'}`}
                    style={{ fontFamily: "'Arimo', sans-serif" }}
                  >
                    {book.he}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}