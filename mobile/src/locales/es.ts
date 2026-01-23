const es = {
  languages: {
    en: "Inglés",
    es: "Español",
    he: "Hebreo",
  },
  home: {
    calendar: {
      todayIs: "Hoy es",
      dateLabel: "Aviv 10",
      dayNames: ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"],
    },
    download: {
      title: "Descargar sin conexión",
      downloading: "Descargando {item}...",
      idle: "Toca para guardar diccionario y traducciones",
      dictionary: "Diccionario",
      english: "Inglés",
      spanish: "Español",
    },
    donate: {
      title: "Donar",
      subtitle: "Apoya el desarrollo de Davar",
    },
    about: {
      title: "Acerca de",
      items: {
        legal: "Legal",
        terms: "Términos",
        privacy: "Privacidad",
        support: "Soporte",
        bug: "Bug",
        github: "GitHub",
        feedback: "Comentarios",
      },
    },
  },
  settings: {
    title: "Ajustes",
    sections: {
      general: "General",
      offline: "Sin conexión",
    },
    theme: {
      title: "Tema",
      subtitle: "Modo oscuro",
    },
    language: {
      title: "Idioma",
    },
    qumran: {
      title: "Variantes de Qumrán",
      subtitle: "Mostrar texto de los Rollos del Mar Muerto",
    },
    fullChapter: {
      title: "Capítulo completo",
      subtitle: "Mostrar texto completo del capítulo",
    },
    hebrewOnly: {
      title: "Solo hebreo",
      subtitle: "Mostrar texto solo en hebreo",
    },
    cantillation: {
      title: "Cantilación",
      subtitle: "Mostrar marcas de cantilación",
    },
    nikud: {
      title: "Nikud",
      subtitle: "Mostrar signos vocálicos",
    },
    clearStorage: {
      title: "Borrar almacenamiento",
      subtitle: "Restablecer ajustes y datos",
      alertTitle: "Borrar almacenamiento",
      alertMessage: "Esto restablecerá todos los ajustes y datos. La app se recargará.",
      cancel: "Cancelar",
      confirm: "Borrar",
    },
  },
  offline: {
    dictionary: "Diccionario",
    englishTranslation: "Traducción al inglés",
    spanishTranslation: "Traducción al español",
    downloaded: "Descargado",
    notDownloaded: "No descargado",
  },
} as const;

export default es;