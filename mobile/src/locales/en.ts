const en = {
  languages: {
    en: "English",
    es: "Español",
    he: "עברית",
  },
  home: {
    calendar: {
      todayIs: "Today is",
      dateLabel: "Aviv 10",
      dayNames: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    },
    download: {
      title: "Download Offline",
      downloading: "Downloading {item}...",
      idle: "Tap to store dictionary and translations",
      dictionary: "Dictionary",
      english: "English",
      spanish: "Spanish",
    },
    donate: {
      title: "Donate",
      subtitle: "Support Davar development",
    },
    about: {
      title: "About",
      items: {
        legal: "Legal",
        terms: "Terms",
        privacy: "Privacy",
        support: "Support",
        bug: "Bug",
        github: "GitHub",
        feedback: "Feedback",
      },
    },
  },
  settings: {
    title: "Settings",
    sections: {
      general: "General",
      offline: "Offline",
    },
    theme: {
      title: "Theme",
      subtitle: "Dark Mode",
    },
    language: {
      title: "Language",
    },
    qumran: {
      title: "Qumran Variants",
      subtitle: "Show Dead Sea Scrolls text",
    },
    fullChapter: {
      title: "Full Chapter",
      subtitle: "Show full chapter text",
    },
    seferStyle: {
      title: "Book Style",
      subtitle: "Continuous Hebrew scroll layout",
      warningTitle: "Book requires Hebrew Only",
      warningMessage: "Enable Hebrew Only to use Book style.",
    },
    hebrewOnly: {
      title: "Hebrew Only",
      subtitle: "Show text in Hebrew only",
    },
    cantillation: {
      title: "Cantillation",
      subtitle: "Show cantillation marks",
    },
    nikud: {
      title: "Nikud",
      subtitle: "Show vowel pointing",
    },
    clearStorage: {
      title: "Clear Storage",
      subtitle: "Reset all settings and data",
      alertTitle: "Clear Storage",
      alertMessage:
        "This will reset all settings and data. The app will reload.",
      cancel: "Cancel",
      confirm: "Clear",
    },
  },
  offline: {
    dictionary: "Dictionary",
    englishTranslation: "English Translation",
    spanishTranslation: "Spanish Translation",
    downloaded: "Downloaded",
    notDownloaded: "Not downloaded",
  },
} as const;

export default en;
