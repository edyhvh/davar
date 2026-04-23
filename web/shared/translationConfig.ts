// Translation configuration utilities for footnote handling and display rules

export type AppLanguage = "en" | "es" | "he";
export type TranslationKey = "ts2009" | "tth" | "delitzsch";

// Mapping from canonical English book names to TTH_2 Hebrew file names
// TTH_2 covers 35 books (Torah, some Neviim, some Ketuvim, some Besorah)
export const TTH_BOOK_MAPPING: Record<string, string> = {
	// TORAH
	Genesis: "bereshit",
	Exodus: "shemot",
	Leviticus: "vaikra",
	Numbers: "bamidbar",
	Deuteronomy: "devarim",
	// NEVIIM (Former Prophets)
	Joshua: "iehoshua",
	Judges: "shoftim",
	Samuel1: "shemuel_alef",
	Samuel2: "shemuel_bet",
	Kings1: "melajim_alef",
	Kings2: "melajim_bet",
	// NEVIIM (Latter Prophets)
	Isaiah: "ieshaiahu",
	Jeremiah: "irmeiahu",
	Ezekiel: "iejezkel",
	// NEVIIM (The Twelve)
	Hosea: "hoshea",
	Joel: "ioel",
	Amos: "amos",
	Jonah: "ionah",
	Micah: "micah",
	Nahum: "najum",
	Habakkuk: "jabakuk",
	Zephaniah: "tzefaniah",
	Haggai: "jagai",
	Zechariah: "zejariah",
	Malachi: "malaji",
	// KETUVIM (partial in tth_2)
	Psalms: "tehilim",
	Proverbs: "mishlei",
	SongOfSolomon: "shir_hashirim",
	// BESORAH (tth_2 format)
	Matthew: "matityahu",
	Mark: "markos",
	Luke: "lukas",
	John: "iojanan",
	Acts: "maasei_hashlijim",
	Romans: "romanos",
	Revelation: "sodot",
};

export const getTranslationKey = (language: AppLanguage): TranslationKey => {
	switch (language) {
		case "en":
			return "ts2009";
		case "es":
			return "tth";
		case "he":
			return "delitzsch";
		default:
			return "ts2009"; // fallback
	}
};

export const shouldHideSuperscripts = (
	translationKey: TranslationKey,
): boolean => {
	// TTH (Spanish) and TS2009 (English) embed footnote markers that we hide in UI
	return translationKey === "tth" || translationKey === "ts2009";
};
