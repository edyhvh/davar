import React from 'react';
import { X } from 'lucide-react';
import { NeumorphCard } from './NeumorphCard';

interface BookSelectorProps {
  currentBook: string;
  onBookSelect: (book: string) => void;
  onClose: () => void;
  language: 'en' | 'es' | 'he';
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
      {/* Header with neumorphic styling */}
      <div className="sticky top-0 z-10 bg-[var(--neomorph-bg)] border-b border-[var(--neomorph-border)] shadow-[6px_6px_16px_var(--neomorph-shadow-dark),-6px_-6px_16px_var(--neomorph-shadow-light)]">
        <div className="relative max-w-md mx-auto px-6 py-5 flex items-center justify-between">
          <h2 
            className="relative text-lg font-medium text-[var(--text-primary)]"
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            Select Book
          </h2>
          <button
            onClick={onClose}
            className="relative p-3 rounded-2xl transition-all hover:scale-110 active:scale-95"
            style={{
              backgroundColor: 'var(--neomorph-bg)',
              border: '1px solid var(--neomorph-border)',
              boxShadow: '6px 6px 12px var(--neomorph-shadow-dark), -6px -6px 12px var(--neomorph-shadow-light)',
            }}
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
              <NeumorphCard
                key={book.en}
                hoverable
                className={`w-full p-6 rounded-2xl transition-all text-left ${
                  isSelected ? 'border-2 border-[var(--accent)]' : ''
                }`}
                onClick={() => {
                  onBookSelect(book.en);
                  onClose();
                }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div 
                      className="text-lg font-medium mb-1 text-[var(--foreground)]"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {book.en.toUpperCase()}
                    </div>
                    <div 
                      className="text-sm text-[var(--text-secondary)]"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {language === 'es' ? book.es : book.en}
                    </div>
                  </div>
                  <div 
                    className="text-2xl text-[var(--text-hebrew)]"
                    style={{ fontFamily: "'Arimo', sans-serif" }}
                  >
                    {book.he}
                  </div>
                </div>
              </NeumorphCard>
            );
          })}
        </div>
      </div>
    </div>
  );
}