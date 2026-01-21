export interface WordResponse {
  position: number;
  text: string;
  text_no_nikud: string;
  strong?: string;
  morph?: string;
  prefixes: string[];
  has_dss_variant: boolean;
}

export interface DssVariant {
  word_position: number;
  dss_text: string;
  manuscript: string;
  commentary?: string;
}

export interface VerseResponse {
  chapter: number;
  verse: number;
  hebrew: string;
  hebrew_no_nikud: string;
  words: WordResponse[];
  translation?: string;
  translation_language?: string;
  dss?: DssVariant[];
}

const createWordResponses = (
  hebrew: string,
  strongMap: Record<number, string> = {},
  dssPositions: number[] = []
): WordResponse[] => {
  return hebrew.split(' ').map((word, index) => {
    const position = index + 1;
    return {
      position,
      text: word,
      text_no_nikud: word,
      strong: strongMap[position],
      prefixes: [],
      has_dss_variant: dssPositions.includes(position),
    };
  });
};

const makeVerse = (
  chapter: number,
  verse: number,
  hebrew: string,
  translation: string,
  strongMap: Record<number, string> = {},
  dss?: DssVariant[]
): VerseResponse => ({
  chapter,
  verse,
  hebrew,
  hebrew_no_nikud: hebrew,
  words: createWordResponses(hebrew, strongMap, dss?.map((item) => item.word_position) ?? []),
  translation,
  translation_language: 'en',
  dss,
});

const mockVerses: Record<string, Record<number, VerseResponse[]>> = {
  Genesis: {
    1: [
      makeVerse(
        1,
        1,
        'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
        'In the beginning, God created the heavens and the earth.',
        {
          1: 'H7225',
          2: 'H1254',
          3: 'H430',
        },
        [
          {
            word_position: 1,
            dss_text: 'בראשית',
            manuscript: '1QGen',
            commentary: 'Orthographic variant without niqqud.',
          },
        ]
      ),
      makeVerse(
        1,
        2,
        'וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם',
        'Now the earth was formless and empty, and darkness was over the surface of the deep.',
        {
          2: 'H1961',
          3: 'H8414',
          4: 'H922',
        }
      ),
      makeVerse(
        1,
        3,
        'וַיֹּאמֶר אֱלֹהִים יְהִי אוֹר וַיְהִי־אוֹר',
        'And God said, “Let there be light,” and there was light.',
        {
          1: 'H559',
          2: 'H430',
          3: 'H1961',
          4: 'H216',
        }
      ),
    ],
  },
};

const defaultBooks = Object.keys(mockVerses);

export const getBooks = (): string[] => defaultBooks;

export const getChapterCount = (book: string): number => {
  const chapters = mockVerses[book];
  if (!chapters) return 1;
  return Object.keys(chapters).length;
};

export const getVerseCount = (book: string, chapter: number): number => {
  const verses = mockVerses[book]?.[chapter];
  return verses?.length ?? 0;
};

export const getChapterVerses = (book: string, chapter: number): VerseResponse[] => {
  return mockVerses[book]?.[chapter] ?? [];
};

export const getVerse = (book: string, chapter: number, verse: number): VerseResponse | null => {
  const verses = mockVerses[book]?.[chapter];
  if (!verses) return null;
  return verses[verse - 1] ?? null;
};
