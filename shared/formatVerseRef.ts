type Language = "en" | "es" | "he";

const DISPLAY_ABBREV: Record<string, { en: string; es: string }> = {
  gen: { en: "Gen", es: "Gén" },
  exod: { en: "Exod", es: "Éx" },
  ex: { en: "Exod", es: "Éx" },
  lev: { en: "Lev", es: "Lev" },
  num: { en: "Num", es: "Núm" },
  deut: { en: "Deut", es: "Dt" },
  josh: { en: "Josh", es: "Jos" },
  judg: { en: "Judg", es: "Jue" },
  ruth: { en: "Ruth", es: "Rut" },
  "1sam": { en: "1 Sam", es: "1 Sam" },
  "2sam": { en: "2 Sam", es: "2 Sam" },
  "1kgs": { en: "1 Kgs", es: "1 Re" },
  "2kgs": { en: "2 Kgs", es: "2 Re" },
  "1chr": { en: "1 Chr", es: "1 Cró" },
  "2chr": { en: "2 Chr", es: "2 Cró" },
  ezra: { en: "Ezra", es: "Esd" },
  neh: { en: "Neh", es: "Neh" },
  esth: { en: "Esth", es: "Est" },
  job: { en: "Job", es: "Job" },
  ps: { en: "Ps", es: "Sal" },
  prov: { en: "Prov", es: "Prov" },
  eccl: { en: "Eccl", es: "Ecl" },
  song: { en: "Song", es: "Cnt" },
  isa: { en: "Isa", es: "Is" },
  jer: { en: "Jer", es: "Jer" },
  lam: { en: "Lam", es: "Lam" },
  ezek: { en: "Ezek", es: "Ez" },
  dan: { en: "Dan", es: "Dn" },
  hos: { en: "Hos", es: "Os" },
  joel: { en: "Joel", es: "Jl" },
  amos: { en: "Amos", es: "Am" },
  obad: { en: "Obad", es: "Abd" },
  jonah: { en: "Jonah", es: "Jon" },
  mic: { en: "Mic", es: "Miq" },
  nah: { en: "Nah", es: "Nah" },
  hab: { en: "Hab", es: "Hab" },
  zeph: { en: "Zeph", es: "Sof" },
  hag: { en: "Hag", es: "Ag" },
  zech: { en: "Zech", es: "Zac" },
  mal: { en: "Mal", es: "Mal" },
  matt: { en: "Matt", es: "Mt" },
  mark: { en: "Mark", es: "Mc" },
  luke: { en: "Luke", es: "Lc" },
  john: { en: "John", es: "Jn" },
  acts: { en: "Acts", es: "Hch" },
  rom: { en: "Rom", es: "Rom" },
  "1cor": { en: "1 Cor", es: "1 Cor" },
  "2cor": { en: "2 Cor", es: "2 Cor" },
  gal: { en: "Gal", es: "Gál" },
  eph: { en: "Eph", es: "Ef" },
  phil: { en: "Phil", es: "Flp" },
  col: { en: "Col", es: "Col" },
  "1thess": { en: "1 Thess", es: "1 Tes" },
  "2thess": { en: "2 Thess", es: "2 Tes" },
  "1tim": { en: "1 Tim", es: "1 Tim" },
  "2tim": { en: "2 Tim", es: "2 Tim" },
  titus: { en: "Titus", es: "Tit" },
  phlm: { en: "Phlm", es: "Flm" },
  heb: { en: "Heb", es: "Heb" },
  jas: { en: "Jas", es: "Stg" },
  "1pet": { en: "1 Pet", es: "1 Pe" },
  "2pet": { en: "2 Pet", es: "2 Pe" },
  "1john": { en: "1 John", es: "1 Jn" },
  "2john": { en: "2 John", es: "2 Jn" },
  "3john": { en: "3 John", es: "3 Jn" },
  jude: { en: "Jude", es: "Jud" },
  rev: { en: "Rev", es: "Ap" },
};

/**
 * Format a raw lexicon verse reference for display.
 * Input:  "gen.1.1" or "1chr.9.27"
 * Output: "Gen 1:1" or "1 Chr 9:27" (language-aware)
 */
export const formatVerseRef = (raw: string, lang?: Language): string => {
  const parts = raw.split(".");
  if (parts.length < 3) return raw;
  const [book, chapter, verse] = parts;
  const key = book.toLowerCase();
  const displayLang = lang === "es" ? "es" : "en";
  const entry = DISPLAY_ABBREV[key];
  const displayBook = entry
    ? entry[displayLang]
    : book.charAt(0).toUpperCase() + book.slice(1);
  return `${displayBook} ${chapter}:${verse}`;
};
