const he = {
  languages: {
    en: "אנגלית",
    es: "ספרדית",
    he: "עברית",
  },
  home: {
    calendar: {
      todayIs: "היום הוא",
      dateLabel: "אביב 10",
      dayNames: ["א׳", "ב׳", "ג׳", "ד׳", "ה׳", "ו׳", "ש׳"],
    },
    download: {
      title: "הורדה לא מקוונת",
      downloading: "מוריד {item}...",
      idle: "הקש כדי לשמור מילון ותרגומים",
      dictionary: "מילון",
      english: "אנגלית",
      spanish: "ספרדית",
    },
    donate: {
      title: "תרומה",
      subtitle: "תמיכה בפיתוח דבר",
    },
    about: {
      title: "אודות",
      items: {
        legal: "משפטי",
        terms: "תנאים",
        privacy: "פרטיות",
        support: "תמיכה",
        bug: "באג",
        github: "GitHub",
        feedback: "משוב",
      },
    },
  },
  settings: {
    title: "הגדרות",
    sections: {
      general: "כללי",
      offline: "לא מקוון",
    },
    theme: {
      title: "ערכת נושא",
      subtitle: "מצב כהה",
    },
    language: {
      title: "שפה",
    },
    qumran: {
      title: "גרסאות קומראן",
      subtitle: "הצג טקסט מגילות מדבר יהודה",
    },
    fullChapter: {
      title: "פרק מלא",
      subtitle: "הצג טקסט מלא של הפרק",
    },
    hebrewOnly: {
      title: "עברית בלבד",
      subtitle: "הצג טקסט רק בעברית",
    },
    cantillation: {
      title: "טעמי מקרא",
      subtitle: "הצג טעמי מקרא",
    },
    nikud: {
      title: "ניקוד",
      subtitle: "הצג ניקוד",
    },
    clearStorage: {
      title: "נקה אחסון",
      subtitle: "אפס את כל ההגדרות והנתונים",
      alertTitle: "נקה אחסון",
      alertMessage: "פעולה זו תאפס את כל ההגדרות והנתונים. האפליקציה תיטען מחדש.",
      cancel: "ביטול",
      confirm: "נקה",
    },
  },
  offline: {
    dictionary: "מילון",
    englishTranslation: "תרגום אנגלי",
    spanishTranslation: "תרגום ספרדי",
    downloaded: "הורד",
    notDownloaded: "לא הורד",
  },
} as const;

export default he;