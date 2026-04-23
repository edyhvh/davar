/**
 * Formats a book name to display the number prefix correctly.
 * Converts "John1" to "1 John", "Corinthians2" to "2 Corinthians", etc.
 *
 * @param bookName - The book name from the backend (e.g., "John1", "Genesis")
 * @returns The formatted display name (e.g., "1 John", "Genesis")
 */
export function formatBookDisplayName(bookName: string): string {
  if (!bookName) return bookName;

  const trimmedName = bookName.trim();

  // Known fused variants that cannot be inferred by casing rules.
  const fusedMap: Record<string, string> = {
    songofsolomon: "Song of Solomon",
    sonofsolomon: "Song of Solomon",
  };
  const fusedKey = trimmedName.toLowerCase().replace(/[^a-z0-9]/g, "");
  const mappedFusedName = fusedMap[fusedKey];
  if (mappedFusedName) {
    return mappedFusedName;
  }

  // Match a number at the end of the string (e.g., "John1", "Corinthians2")
  const match = trimmedName.match(/^(.+?)(\d+)$/);

  let normalized = trimmedName;

  if (match) {
    const name = match[1]; // e.g., "John", "Corinthians"
    const number = match[2]; // e.g., "1", "2"
    normalized = `${number} ${name}`;
  }

  // Add spacing for camel/pascal case names (e.g., "SongOfSolomon").
  return normalized
    .replace(/[_-]+/g, " ")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1 $2")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/\s+/g, " ")
    .trim();
}
