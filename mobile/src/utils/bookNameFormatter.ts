/**
 * Formats a book name to display the number prefix correctly.
 * Converts "John1" to "1 John", "Corinthians2" to "2 Corinthians", etc.
 *
 * @param bookName - The book name from the backend (e.g., "John1", "Genesis")
 * @returns The formatted display name (e.g., "1 John", "Genesis")
 */
export function formatBookDisplayName(bookName: string): string {
  if (!bookName) return bookName;

  // Match a number at the end of the string (e.g., "John1", "Corinthians2")
  const match = bookName.match(/^(.+?)(\d+)$/);

  if (match) {
    const name = match[1]; // e.g., "John", "Corinthians"
    const number = match[2]; // e.g., "1", "2"
    return `${number} ${name}`;
  }

  // No number suffix, return as-is
  return bookName;
}
