export type MockWord = {
  position: number;
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
  qumranVariants?: { position: number; dssWord: string }[];
};

export type MockBook = {
  id: string;
  name: string;
  hebrewName: string;
};

export const mockBooks: MockBook[] = [
  { id: "genesis", name: "Genesis", hebrewName: "בראשית" },
  { id: "exodus", name: "Exodus", hebrewName: "שמות" },
  { id: "leviticus", name: "Leviticus", hebrewName: "ויקרא" },
  { id: "numbers", name: "Numbers", hebrewName: "במדבר" },
  { id: "deuteronomy", name: "Deuteronomy", hebrewName: "דברים" },
  { id: "joshua", name: "Joshua", hebrewName: "יהושע" },
  { id: "judges", name: "Judges", hebrewName: "שופטים" },
  { id: "samuel1", name: "Samuel1", hebrewName: "שמואל א" },
  { id: "samuel2", name: "Samuel2", hebrewName: "שמואל ב" },
  { id: "kings1", name: "Kings1", hebrewName: "מלכים א" },
  { id: "kings2", name: "Kings2", hebrewName: "מלכים ב" },
  { id: "isaiah", name: "Isaiah", hebrewName: "ישעיהו" },
  { id: "jeremiah", name: "Jeremiah", hebrewName: "ירמיהו" },
  { id: "ezekiel", name: "Ezekiel", hebrewName: "יחזקאל" },
  { id: "hosea", name: "Hosea", hebrewName: "הושע" },
  { id: "joel", name: "Joel", hebrewName: "יואל" },
  { id: "amos", name: "Amos", hebrewName: "עמוס" },
  { id: "obadiah", name: "Obadiah", hebrewName: "עובדיה" },
  { id: "jonah", name: "Jonah", hebrewName: "יונה" },
  { id: "micah", name: "Micah", hebrewName: "מיכה" },
  { id: "nahum", name: "Nahum", hebrewName: "נחום" },
  { id: "habakkuk", name: "Habakkuk", hebrewName: "חבקוק" },
  { id: "zephaniah", name: "Zephaniah", hebrewName: "צפניה" },
  { id: "haggai", name: "Haggai", hebrewName: "חגי" },
  { id: "zechariah", name: "Zechariah", hebrewName: "זכריה" },
  { id: "malachi", name: "Malachi", hebrewName: "מלאכי" },
  { id: "psalms", name: "Psalms", hebrewName: "תהלים" },
  { id: "proverbs", name: "Proverbs", hebrewName: "משלי" },
  { id: "job", name: "Job", hebrewName: "איוב" },
  { id: "songofsolomon", name: "SongOfSolomon", hebrewName: "שיר השירים" },
  { id: "ruth", name: "Ruth", hebrewName: "רות" },
  { id: "lamentations", name: "Lamentations", hebrewName: "איכה" },
  { id: "ecclesiastes", name: "Ecclesiastes", hebrewName: "קהלת" },
  { id: "esther", name: "Esther", hebrewName: "אסתר" },
  { id: "daniel", name: "Daniel", hebrewName: "דניאל" },
  { id: "ezra", name: "Ezra", hebrewName: "עזרא" },
  { id: "nehemiah", name: "Nehemiah", hebrewName: "נחמיה" },
  { id: "chronicles1", name: "Chronicles1", hebrewName: "דברי הימים א" },
  { id: "chronicles2", name: "Chronicles2", hebrewName: "דברי הימים ב" },
  { id: "matthew", name: "Matthew", hebrewName: "מתתיהו" },
  { id: "mark", name: "Mark", hebrewName: "מרקוס" },
  { id: "luke", name: "Luke", hebrewName: "לוקאס" },
  { id: "john", name: "John", hebrewName: "יוחנן" },
  { id: "acts", name: "Acts", hebrewName: "מעשי השליחים" },
  { id: "romans", name: "Romans", hebrewName: "רומים" },
  { id: "corinthians1", name: "Corinthians1", hebrewName: "קורינתים א" },
  { id: "corinthians2", name: "Corinthians2", hebrewName: "קורינתים ב" },
  { id: "galatians", name: "Galatians", hebrewName: "גלטים" },
  { id: "ephesians", name: "Ephesians", hebrewName: "אפסים" },
  { id: "philippians", name: "Philippians", hebrewName: "פיליפים" },
  { id: "colossians", name: "Colossians", hebrewName: "קלוסים" },
  { id: "thessalonians1", name: "Thessalonians1", hebrewName: "תסלוניקים א" },
  { id: "thessalonians2", name: "Thessalonians2", hebrewName: "תסלוניקים ב" },
  { id: "timothy1", name: "Timothy1", hebrewName: "טימותי א" },
  { id: "timothy2", name: "Timothy2", hebrewName: "טימותי ב" },
  { id: "titus", name: "Titus", hebrewName: "טיטוס" },
  { id: "philemon", name: "Philemon", hebrewName: "פילימון" },
  { id: "hebrews", name: "Hebrews", hebrewName: "עברים" },
  { id: "james", name: "James", hebrewName: "יעקב" },
  { id: "peter1", name: "Peter1", hebrewName: "כפא א" },
  { id: "peter2", name: "Peter2", hebrewName: "כפא ב" },
  { id: "john1", name: "John1", hebrewName: "יוחנן א" },
  { id: "john2", name: "John2", hebrewName: "יוחנן ב" },
  { id: "john3", name: "John3", hebrewName: "יוחנן ג" },
  { id: "jude", name: "Jude", hebrewName: "יהודה" },
  { id: "revelation", name: "Revelation", hebrewName: "התגלות יוחנן" },
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
    qumranVariants: [{ position: 0, dssWord: "בְּרֹאשִׁית" }],
    words: [
      {
        position: 0,
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
        position: 1,
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
        position: 2,
        text: "אֱלֹהִים",
        strong: "H430",
        transliteration: "Elohim",
        gloss: "God",
      },
      {
        position: 3,
        text: "אֵת",
        strong: "H853",
        transliteration: "et",
        gloss: "object marker",
      },
      {
        position: 4,
        text: "הַשָּׁמַיִם",
        strong: "H8064",
        transliteration: "hashamayim",
        gloss: "the heavens",
      },
      {
        position: 5,
        text: "וְאֵת",
        strong: "H853",
        prefixes: ["ו"],
        transliteration: "ve-et",
        gloss: "and",
      },
      {
        position: 6,
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
        position: 0,
        text: "וְהָאָרֶץ",
        strong: "H776",
        prefixes: ["ו"],
        transliteration: "vehaaretz",
        gloss: "and the earth",
        hasQumranVariant: true,
      },
      {
        position: 1,
        text: "הָיְתָה",
        strong: "H1961",
        transliteration: "hayetah",
        gloss: "was",
      },
      {
        position: 2,
        text: "תֹהוּ",
        strong: "H8414",
        transliteration: "tohu",
        gloss: "formless",
      },
      {
        position: 3,
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
        position: 0,
        text: "וַיֹּאמֶר",
        strong: "H559",
        prefixes: ["ו"],
        transliteration: "vayomer",
        gloss: "and he said",
        hasQumranVariant: false,
      },
      {
        position: 1,
        text: "אֱלֹהִים",
        strong: "H430",
        transliteration: "Elohim",
        gloss: "God",
      },
      {
        position: 2,
        text: "יְהִי",
        strong: "H1961",
        transliteration: "yehi",
        gloss: "let there be",
      },
      {
        position: 3,
        text: "אוֹר",
        strong: "H216",
        transliteration: "or",
        gloss: "light",
      },
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
        position: 0,
        text: "סֵפֶר",
        strong: "H5612",
        transliteration: "sefer",
        gloss: "book",
        meanings: ["book", "scroll"],
      },
      {
        position: 1,
        text: "תּוֹלְדֹת",
        strong: "H8435",
        transliteration: "toledot",
        gloss: "genealogies",
      },
      {
        position: 2,
        text: "יֵשׁוּעַ",
        strong: "H3442",
        transliteration: "Yeshua",
        gloss: "Jesus",
      },
      {
        position: 3,
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
