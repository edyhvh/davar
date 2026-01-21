/**
 * Hebrew text processing utilities for prefix parsing and text normalization
 */

// Load prefix forms lookup (this would be loaded from the API in a real app)
const PREFIX_FORMS: Record<string, string[]> = {
  "בְּ": ["Hb"],
  "לְ": ["Hl"],
  "וְ": ["Hv"],
  "כְּ": ["Hk"],
  "מִ": ["Hm"],
  "הַ": ["Hd"],
  "בַּ": ["Hb"],
  "לַ": ["Hl"],
  "וַ": ["Hv"],
  "כַּ": ["Hk"],
  "מַ": ["Hm"],
  "הָ": ["Hd"],
  // Add more forms as needed
};

export interface ParsedWord {
  full: string;
  prefix?: {
    text: string;
    particle: string;
    meanings: Record<string, string[]>;
  };
  root: string;
}

/**
 * Parse a Hebrew word into prefix and root components
 */
export function parseHebrewWord(word: string): ParsedWord {
  // Check if word contains "/" separator (data format with explicit prefix separation)
  if (word.includes('/')) {
    const parts = word.split('/');
    if (parts.length >= 2) {
      const prefixText = parts[0];
      const rootText = parts.slice(1).join('/'); // Rejoin in case there are multiple slashes

      // Clean prefix and root text: remove cantillation, nikud and any remaining slashes
      const clean = (s: string) => s.replace(/[\u0591-\u05AF]/g, '').replace(/[\u05B0-\u05C7]/g, '').replace(/\//g, '');
      const cleanedPrefixText = clean(prefixText);
      const cleanedRootText = clean(rootText);

      // Find the prefix particle from our lookup
      const prefixForms = Object.keys(PREFIX_FORMS).sort((a, b) => b.length - a.length);
      for (const prefixForm of prefixForms) {
        if (cleanedPrefixText.includes(prefixForm)) {
          return {
            full: word,
            prefix: {
              text: cleanedPrefixText,
              particle: PREFIX_FORMS[prefixForm][0],
              meanings: {} // Would be loaded from API
            },
            root: cleanedRootText
          };
        }
      }

      // If no specific prefix form found, still treat first part as prefix
      return {
        full: word,
        prefix: {
          text: cleanedPrefixText,
          particle: 'unknown',
          meanings: {}
        },
        root: cleanedRootText
      };
    }
  }

  // Remove cantillation marks (U+0591-U+05AF)
  const withoutCantillation = word.replace(/[\u0591-\u05AF]/g, '');

  // Remove nikud (U+05B0-U+05C7)
  const withoutNikud = withoutCantillation.replace(/[\u05B0-\u05C7]/g, '');

  // Try to find prefix (longest match first)
  const prefixForms = Object.keys(PREFIX_FORMS).sort((a, b) => b.length - a.length);

  for (const prefixForm of prefixForms) {
    if (withoutNikud.startsWith(prefixForm)) {
      const root = withoutNikud.slice(prefixForm.length);
      if (root.length > 0) { // Ensure there's a root left
        return {
          full: word,
          prefix: {
            text: prefixForm,
            particle: PREFIX_FORMS[prefixForm][0],
            meanings: {} // Would be loaded from API
          },
          root: root
        };
      }
    }
  }

  // No prefix found
  return {
    full: word,
    root: withoutNikud
  };
}

/**
 * Strip nikud from Hebrew text
 */
export function stripNikud(text: string): string {
  return text.replace(/[\u05B0-\u05C7]/g, '');
}

/**
 * Strip cantillation marks from Hebrew text
 */
export function stripCantillation(text: string): string {
  return text.replace(/[\u0591-\u05AF]/g, '');
}

/**
 * Normalize Hebrew text (strip both nikud and cantillation)
 */
export function normalizeHebrew(text: string): string {
  return stripCantillation(stripNikud(text));
}