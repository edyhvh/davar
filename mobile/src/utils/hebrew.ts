/**
 * Hebrew text processing utilities for React Native
 */

// Load prefix forms lookup (this would be loaded from the API in a real app)
const PREFIX_FORMS: Record<string, string[]> = {
  בְּ: ["Hb"],
  לְ: ["Hl"],
  וְ: ["Hv"],
  כְּ: ["Hk"],
  מִ: ["Hm"],
  הַ: ["Hd"],
  בַּ: ["Hb"],
  לַ: ["Hl"],
  וַ: ["Hv"],
  כַּ: ["Hk"],
  מַ: ["Hm"],
  הָ: ["Hd"],
  // Add more forms as needed
};

const HEBREW_MARKS_REGEX = /[\u0591-\u05C7]/g;
const HEBREW_MARKS_SINGLE = /[\u0591-\u05C7]/;
const HEBREW_BIDI_CONTROLS = /[\u200C\u200D\u200E\u200F\u202A-\u202E\u2066-\u2069]/g;

const stripHebrewMarks = (text: string) => text.replace(HEBREW_MARKS_REGEX, "");

const buildPrefixFormsById = () => {
  const map: Record<string, string[]> = {};
  Object.entries(PREFIX_FORMS).forEach(([form, ids]) => {
    ids.forEach((id) => {
      map[id] = map[id] ? [...map[id], form] : [form];
    });
  });
  return map;
};

const PREFIX_FORMS_BY_ID = buildPrefixFormsById();

const sliceByStrippedLength = (
  text: string,
  startIndex: number,
  strippedLength: number,
) => {
  let count = 0;
  let endIndex = startIndex;
  for (; endIndex < text.length; endIndex += 1) {
    const char = text[endIndex];
    if (char === "/") {
      continue;
    }
    if (!HEBREW_MARKS_SINGLE.test(char)) {
      count += 1;
    }
    if (count >= strippedLength) {
      endIndex += 1;
      break;
    }
  }
  return text.slice(startIndex, endIndex);
};

export const getPrefixSegments = (
  word: string,
  prefixIds: string[],
): { prefixes: string[]; root: string } => {
  if (!word || !prefixIds.length) {
    return { prefixes: [], root: word };
  }

  if (word.includes("/")) {
    const parts = word.split("/").filter(Boolean);
    if (parts.length > 1) {
      return {
        prefixes: parts.slice(0, -1).map((part) => part.replace(/\//g, "")),
        root: parts.slice(-1).join(""),
      };
    }
  }

  const strippedWord = stripHebrewMarks(word);
  const prefixes: string[] = [];
  let rawIndex = 0;
  let strippedIndex = 0;

  for (const prefixId of prefixIds) {
    const forms = PREFIX_FORMS_BY_ID[prefixId] ?? [];
    const sortedForms = forms
      .map((form) => ({ form, stripped: stripHebrewMarks(form) }))
      .sort((a, b) => b.stripped.length - a.stripped.length);

    const match = sortedForms.find((form) =>
      strippedWord.startsWith(form.stripped, strippedIndex),
    );

    if (!match) {
      break;
    }

    const segment = sliceByStrippedLength(
      word,
      rawIndex,
      match.stripped.length,
    );
    prefixes.push(segment.replace(/\//g, ""));
    rawIndex += segment.length;
    strippedIndex += match.stripped.length;
  }

  if (!prefixes.length) {
    return { prefixes: [], root: word };
  }

  return {
    prefixes,
    root: word.slice(rawIndex),
  };
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
  if (word.includes("/")) {
    const parts = word.split("/");
    if (parts.length >= 2) {
      const prefixText = parts.slice(0, -1).join("");
      const rootText = parts.slice(-1).join("");

      const cleanedPrefixText = stripHebrewMarks(prefixText.replace(/\//g, ""));

      // Find the prefix particle from our lookup
      const prefixForms = Object.keys(PREFIX_FORMS).sort(
        (a, b) => b.length - a.length,
      );
      for (const prefixForm of prefixForms) {
        if (cleanedPrefixText.includes(stripHebrewMarks(prefixForm))) {
          return {
            full: word,
            prefix: {
              text: prefixText.replace(/\//g, ""),
              particle: PREFIX_FORMS[prefixForm][0],
              meanings: {}, // Would be loaded from API
            },
            root: rootText.replace(/\//g, ""),
          };
        }
      }

      // If no specific prefix form found, still treat first part as prefix
      return {
        full: word,
        prefix: {
          text: prefixText.replace(/\//g, ""),
          particle: "unknown",
          meanings: {},
        },
        root: rootText.replace(/\//g, ""),
      };
    }
  }

  const withoutMarks = stripHebrewMarks(word);

  // Try to find prefix (longest match first)
  const prefixForms = Object.keys(PREFIX_FORMS).sort(
    (a, b) => b.length - a.length,
  );

  for (const prefixForm of prefixForms) {
    const strippedPrefixForm = stripHebrewMarks(prefixForm);
    if (withoutMarks.startsWith(strippedPrefixForm)) {
      const prefixText = sliceByStrippedLength(word, 0, strippedPrefixForm.length);
      const root = word.slice(prefixText.length);
      if (root.length > 0) {
        // Ensure there's a root left
        return {
          full: word,
          prefix: {
            text: prefixText,
            particle: PREFIX_FORMS[prefixForm][0],
            meanings: {}, // Would be loaded from API
          },
          root: root,
        };
      }
    }
  }

  // No prefix found
  return {
    full: word,
    root: word,
  };
}

/**
 * Strip nikud from Hebrew text
 */
export function stripNikud(text: string): string {
  return text.replace(/[\u05B0-\u05C7]/g, "");
}

/**
 * Strip cantillation marks from Hebrew text
 */
export function stripCantillation(text: string): string {
  return text.replace(/[\u0591-\u05AF]/g, "");
}

/**
 * Strip meteg (U+05BD) from Hebrew text
 */
export function stripMeteg(text: string): string {
  return text.replace(/\u05BD/g, "");
}

/**
 * Normalize Hebrew display text and remove bidi control characters
 */
export function normalizeHebrewDisplay(text: string): string {
  return text.normalize("NFC").replace(HEBREW_BIDI_CONTROLS, "");
}

/**
 * Normalize Hebrew text (strip both nikud and cantillation)
 */
export function normalizeHebrew(text: string): string {
  return stripCantillation(stripNikud(text));
}
