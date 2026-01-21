export interface WordInstance {
  verse: string;
  text: string;
}

export interface WordAnalysis {
  word: string;
  transliteration?: string;
  meanings: string[];
  root?: string;
  rootTransliteration?: string;
  rootMeaning?: string;
  instances: WordInstance[];
  strong?: string;
}

const mockLexicon: Record<string, WordAnalysis> = {
  'H7225': {
    word: 'בְּרֵאשִׁית',
    transliteration: 'bereshit',
    meanings: ['in beginning', 'at first', 'when beginning'],
    root: 'ראש',
    rootTransliteration: 'rosh',
    rootMeaning: 'head, beginning, chief',
    instances: [
      { verse: 'Gen 1:1', text: 'In the beginning God created...' },
      { verse: 'Gen 10:10', text: 'The beginning of his kingdom was...' },
    ],
    strong: 'H7225',
  },
  'H1254': {
    word: 'בָּרָא',
    transliteration: 'bara',
    meanings: ['created', 'brought into existence'],
    root: 'ברא',
    rootTransliteration: 'bara',
    rootMeaning: 'to create, shape, form',
    instances: [
      { verse: 'Gen 1:1', text: 'In the beginning God created...' },
      { verse: 'Gen 1:21', text: 'So God created the great creatures...' },
      { verse: 'Gen 1:27', text: 'So God created mankind...' },
    ],
    strong: 'H1254',
  },
  'H430': {
    word: 'אֱלֹהִים',
    transliteration: 'elohim',
    meanings: ['God', 'gods', 'divine beings'],
    root: 'אלה',
    rootTransliteration: 'elah',
    rootMeaning: 'deity, divine power',
    instances: [
      { verse: 'Gen 1:1', text: 'In the beginning God created...' },
      { verse: 'Gen 1:2', text: 'and the Spirit of God was hovering...' },
    ],
    strong: 'H430',
  },
};

const mockLexiconByWord: Record<string, WordAnalysis> = {
  'בְּרֵאשִׁית': mockLexicon.H7225,
  'בָּרָא': mockLexicon.H1254,
  'אֱלֹהִים': mockLexicon.H430,
};

export const getWordAnalysisByStrong = (strong?: string): WordAnalysis | null => {
  if (!strong) return null;
  return mockLexicon[strong] ?? null;
};

export const getWordAnalysisByText = (word: string): WordAnalysis | null => {
  return mockLexiconByWord[word] ?? null;
};
