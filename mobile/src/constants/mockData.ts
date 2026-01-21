export type MockWord = {
  text: string;
  strong: string;
  prefixes?: string[];
  transliteration?: string;
  gloss?: string;
  meanings?: string[];
  root?: string;
  rootTransliteration?: string;
  rootMeaning?: string;
  instances?: { verse: string; text: string }[];
  hasQumranVariant?: boolean;
};

export type MockVerse = {
  id: string;
  book: string;
  bookId: string;
  chapter: number;
  verse: number;
  hebrew: string;
  translation: string;
  words: MockWord[];
  qumranVariants?: { wordIndex: number; variant: string }[];
};

export type MockBook = {
  id: string;
  name: string;
  hebrewName: string;
};

export const mockBooks: MockBook[] = [
  { id: "genesis", name: "Genesis", hebrewName: "בְּרֵאשִׁית" },
  { id: "exodus", name: "Exodus", hebrewName: "שְׁמוֹת" },
  { id: "psalms", name: "Psalms", hebrewName: "תְּהִלִּים" },
  { id: "isaiah", name: "Isaiah", hebrewName: "יְשַׁעְיָהוּ" },
  { id: "matthew", name: "Matthew", hebrewName: "מַתִּתְיָהוּ" },
];

export const mockVerses: MockVerse[] = [
  {
    id: "genesis-1-1",
    book: "Genesis",
    bookId: "genesis",
    chapter: 1,
    verse: 1,
    hebrew: "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ׃",
    translation: "In the beginning God created the heavens and the earth.",
    qumranVariants: [{ wordIndex: 0, variant: "בְּרֹאשִׁית" }],
    words: [
      {
        text: "בְּרֵאשִׁית",
        strong: "H7225",
        transliteration: "Bereshit",
        gloss: "in the beginning",
        meanings: ["in beginning", "at first", "when beginning"],
        root: "ראש",
        rootTransliteration: "rosh",
        rootMeaning: "head, beginning, chief",
        instances: [
          { verse: "Gen 1:1", text: "In the beginning God created…" },
          { verse: "Jer 26:1", text: "In the beginning of the reign…" },
        ],
        hasQumranVariant: true,
      },
      {
        text: "בָּרָא",
        strong: "H1254",
        transliteration: "bara",
        gloss: "created",
        meanings: ["created", "fashioned"],
        root: "ברא",
        rootTransliteration: "bara",
        rootMeaning: "create, shape",
      },
      {
        text: "אֱלֹהִים",
        strong: "H430",
        transliteration: "Elohim",
        gloss: "God",
      },
      {
        text: "אֵת",
        strong: "H853",
        transliteration: "et",
        gloss: "object marker",
      },
      {
        text: "הַשָּׁמַיִם",
        strong: "H8064",
        transliteration: "hashamayim",
        gloss: "the heavens",
      },
      {
        text: "וְאֵת",
        strong: "H853",
        prefixes: ["ו"],
        transliteration: "ve-et",
        gloss: "and",
      },
      {
        text: "הָאָרֶץ",
        strong: "H776",
        transliteration: "haaretz",
        gloss: "the earth",
      },
    ],
  },
  {
    id: "genesis-1-2",
    book: "Genesis",
    bookId: "genesis",
    chapter: 1,
    verse: 2,
    hebrew:
      "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם וְרוּחַ אֱלֹהִים מְרַחֶפֶת עַל־פְּנֵי הַמָּיִם׃",
    translation:
      "Now the earth was formless and empty, darkness was over the surface of the deep, and the Spirit of God was hovering over the waters.",
    words: [
      {
        text: "וְהָאָרֶץ",
        strong: "H776",
        prefixes: ["ו"],
        transliteration: "vehaaretz",
        gloss: "and the earth",
        hasQumranVariant: true,
      },
      {
        text: "הָיְתָה",
        strong: "H1961",
        transliteration: "hayetah",
        gloss: "was",
      },
      {
        text: "תֹהוּ",
        strong: "H8414",
        transliteration: "tohu",
        gloss: "formless",
      },
      {
        text: "וָבֹהוּ",
        strong: "H922",
        prefixes: ["ו"],
        transliteration: "vavohu",
        gloss: "empty",
      },
    ],
  },
  {
    id: "genesis-1-3",
    book: "Genesis",
    bookId: "genesis",
    chapter: 1,
    verse: 3,
    hebrew: "וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי אוֹר׃",
    translation: "And God said, “Let there be light,” and there was light.",
    words: [
      {
        text: "וַיֹּאמֶר",
        strong: "H559",
        prefixes: ["ו"],
        transliteration: "vayomer",
        gloss: "and he said",
        hasQumranVariant: false,
      },
      {
        text: "אֱלֹהִים",
        strong: "H430",
        transliteration: "Elohim",
        gloss: "God",
      },
      {
        text: "יְהִי",
        strong: "H1961",
        transliteration: "yehi",
        gloss: "let there be",
      },
      { text: "אוֹר", strong: "H216", transliteration: "or", gloss: "light" },
    ],
  },
  {
    id: "matthew-1-1",
    book: "Matthew",
    bookId: "matthew",
    chapter: 1,
    verse: 1,
    hebrew: "סֵפֶר תּוֹלְדֹת יֵשׁוּעַ הַמָּשִׁיחַ בֶּן־דָּוִד בֶּן־אַבְרָהָם׃",
    translation:
      "The record of the genealogy of Yeshua the Messiah, the son of David, the son of Abraham.",
    words: [
      {
        text: "סֵפֶר",
        strong: "H5612",
        transliteration: "sefer",
        gloss: "book",
        meanings: ["book", "scroll"],
      },
      {
        text: "תּוֹלְדֹת",
        strong: "H8435",
        transliteration: "toledot",
        gloss: "genealogies",
      },
      {
        text: "יֵשׁוּעַ",
        strong: "H3442",
        transliteration: "Yeshua",
        gloss: "Jesus",
      },
      {
        text: "הַמָּשִׁיחַ",
        strong: "H4899",
        prefixes: ["ה"],
        transliteration: "hamashiach",
        gloss: "the Messiah",
      },
    ],
  },
];

export const getMockVerseById = (id: string) =>
  mockVerses.find((verse) => verse.id === id);

export const getMockVerseIndex = (id: string) =>
  mockVerses.findIndex((verse) => verse.id === id);
