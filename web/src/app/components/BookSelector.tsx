import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { NeumorphCard } from './NeumorphCard';
import { getBooks } from '../services/verseService';

interface BookSelectorProps {
  currentBook: string;
  onBookSelect: (book: string) => void;
  onClose: () => void;
  language: 'en' | 'es' | 'he';
}

interface BookResponse {
  id: string;
  name: string;
  section: string;
  chapters: number;
  order: number;
  hebrew_name: string;
  hebrew_transliteration: string;
  spanish_name: string;
}

export function BookSelector({ currentBook, onBookSelect, onClose, language }: BookSelectorProps) {
  const [books, setBooks] = useState<BookResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const booksData = await getBooks();
        setBooks(booksData);
      } catch (error) {
        console.error('Failed to fetch books:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, []);

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 bg-[var(--background)] flex items-center justify-center">
        <div className="text-[var(--text-primary)]">Loading books...</div>
      </div>
    );
  }
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
          {books.map((book) => {
            const isSelected = book.name === currentBook;
            const displayName = language === 'es' ? book.spanish_name : book.name;
            const hebrewDisplay = language === 'he' ? book.hebrew_name : book.hebrew_transliteration;
            return (
              <NeumorphCard
                key={book.id}
                hoverable
                className={`w-full p-6 rounded-2xl transition-all text-left ${
                  isSelected ? 'border-2 border-[var(--accent)]' : ''
                }`}
                onClick={() => {
                  onBookSelect(book.name);
                  onClose();
                }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div 
                      className="text-lg font-medium mb-1 text-[var(--foreground)]"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {book.name.toUpperCase()}
                    </div>
                    <div 
                      className="text-sm text-[var(--text-secondary)]"
                      style={{ fontFamily: "'Inter', sans-serif" }}
                    >
                      {displayName}
                    </div>
                  </div>
                  <div 
                    className="text-2xl text-[var(--text-hebrew)]"
                    style={{ fontFamily: "'Arimo', sans-serif" }}
                  >
                    {hebrewDisplay}
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