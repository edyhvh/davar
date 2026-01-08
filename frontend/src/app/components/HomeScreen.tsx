import React from 'react';
import { Download, Heart, ExternalLink, Github, Scale, FileText, Shield, MessageCircle, Bug, Info } from 'lucide-react';

interface HomeScreenProps {
  language: 'en' | 'es' | 'he';
}

// Biblical Hebrew months (not rabbinic)
const biblicalMonths = [
  'Aviv', 'Ziv', 'Sivan', 'Tammuz', 'Av', 'Elul',
  'Ethanim', 'Bul', 'Kislev', 'Tevet', 'Shevat', 'Adar'
];

const translations = {
  en: {
    todayIs: 'Today is',
    downloadOffline: 'Download Offline',
    downloadDescription: 'Access Scripture without internet',
    donate: 'Donate',
    donateDescription: 'Support Davar development',
    about: 'About',
    legal: 'Legal',
    terms: 'Terms',
    privacy: 'Privacy',
    support: 'Support',
    reportBug: 'Bug',
    feedback: 'Feedback',
    github: 'GitHub',
  },
  es: {
    todayIs: 'Hoy es',
    downloadOffline: 'Descargar Sin Conexión',
    downloadDescription: 'Accede a las Escrituras sin internet',
    donate: 'Donar',
    donateDescription: 'Apoya el desarrollo de Davar',
    about: 'Acerca de',
    legal: 'Legal',
    terms: 'Términos',
    privacy: 'Privacidad',
    support: 'Soporte',
    reportBug: 'Bug',
    feedback: 'Comentarios',
    github: 'GitHub',
  },
  he: {
    todayIs: 'היום הוא',
    downloadOffline: 'הורדה לא מקוונת',
    downloadDescription: 'גישה לכתובים ללא אינטרנט',
    donate: 'תרומה',
    donateDescription: 'תמיכה בפיתוח דבר',
    about: 'אודות',
    legal: 'משפטי',
    terms: 'תנאים',
    privacy: 'פרטיות',
    support: 'תמיכה',
    reportBug: 'באג',
    feedback: 'משוב',
    github: 'GitHub',
  },
};

// Get Biblical Hebrew date (simplified version for demo)
function getBiblicalHebrewDate(): string {
  // Hardcoded to Aviv 10th for demo
  return `Aviv 10th`;
}

function getDaySuffix(day: number): string {
  if (day >= 11 && day <= 13) {
    return 'th';
  }
  switch (day % 10) {
    case 1: return 'st';
    case 2: return 'nd';
    case 3: return 'rd';
    default: return 'th';
  }
}

export function HomeScreen({ language }: HomeScreenProps) {
  const t = translations[language];
  const hebrewDate = getBiblicalHebrewDate();

  // Check if text is Hebrew (contains Hebrew characters)
  const isHebrewText = (text: string) => /[\u0590-\u05FF]/.test(text);

  // Generate upcoming days starting from 10th (hardcoded for demo)
  const upcomingDays = [];
  const startDay = 10; // Aviv 10th
  
  for (let i = 0; i < 7; i++) {
    const day = startDay + i;
    // Simplified day names for demo
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const dayName = dayNames[i % 7];
    
    // Check if this is Pesach (14th)
    const isPesach = day === 14;
    
    // Check if this is Shabbat (Saturday)
    const isShabbat = dayName === 'Sat';
    
    upcomingDays.push({
      day,
      dayName,
      isPesach,
      isShabbat,
      isToday: i === 0
    });
  }

  return (
    <div className="space-y-4 pb-24">
      {/* Hebrew Date Card - Retro Style */}
      <div 
        className="p-8 rounded-[32px] border-2 border-[var(--accent)]"
        style={{
          backgroundColor: 'var(--background)',
        }}
      >
        <div className="flex items-center justify-between mb-6">
          <div 
            className="px-5 py-2 rounded-full border-2 border-[var(--accent)] inline-block"
            style={{
              backgroundColor: 'var(--background)',
            }}
          >
            <span 
              className="text-sm font-medium text-[var(--text-secondary)]"
              style={{ 
                fontFamily: "'Inter', sans-serif",
              }}
            >
              {t.todayIs}
            </span>
          </div>
        </div>
        <div 
          className="text-7xl font-bold leading-none tracking-tight mb-8 text-[var(--text-secondary)]"
          style={{ 
            fontFamily: "'Inter', sans-serif",
          }}
        >
          {hebrewDate}
        </div>

        {/* Upcoming Days Calendar */}
        <div className="flex gap-3 overflow-x-auto pb-2 -mx-2 px-2">
          {upcomingDays.map((item, index) => (
            <div
              key={index}
              className={`flex-shrink-0 rounded-[24px] p-4 relative ${
                item.isToday ? 'bg-[var(--accent)]' : 'bg-[var(--muted)]'
              }`}
              style={{
                minWidth: '80px',
              }}
            >
              {/* Small dots at top for decoration */}
              {!item.isToday && (
                <div className="flex gap-1 justify-center mb-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--text-secondary)] opacity-30" />
                  <div className="w-1.5 h-1.5 rounded-full bg-[var(--text-secondary)] opacity-30" />
                </div>
              )}
              
              {/* Day number */}
              <div 
                className={`text-3xl font-bold text-center ${
                  item.isToday ? 'text-white' : 'dark:text-[var(--muted-foreground)]'
                }`}
                style={{ 
                  fontFamily: "'Inter', sans-serif",
                  color: item.isToday ? undefined : 'var(--foreground)',
                }}
              >
                {item.day}
              </div>
              
              {/* Day name */}
              <div 
                className={`text-xs text-center mt-1 ${
                  item.isToday ? 'text-white/80' : 'text-[var(--text-secondary)]'
                }`}
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {item.dayName}
              </div>
              
              {/* Pesach label */}
              {item.isPesach && (
                <div className="mt-2 text-center">
                  <div 
                    className="text-xs font-medium text-[var(--text-secondary)]" 
                    style={{ 
                      fontFamily: "'Inter', sans-serif",
                    }}
                  >
                    Pesaj
                  </div>
                  <div 
                    className="text-[10px] dark:text-[var(--foreground)]" 
                    style={{ 
                      fontFamily: "'Cardo', serif",
                      color: 'var(--text-secondary)',
                    }}
                  >
                    פֶּסַח
                  </div>
                </div>
              )}
              
              {/* Today indicator underline */}
              {item.isToday && (
                <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-8 h-1 bg-white rounded-full" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Download Card - Full Width */}
      <div 
        className="p-5 rounded-[32px] relative overflow-hidden flex items-center justify-between"
        style={{
          backgroundColor: 'var(--copper-highlight)',
        }}
      >
        <div>
          <div 
            className={`text-2xl font-bold text-white mb-1 ${isHebrewText(t.downloadOffline) ? 'dark:text-white' : 'dark:text-white'}`}
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {t.downloadOffline}
          </div>
          <div 
            className={`text-sm text-white/80 ${isHebrewText(t.downloadDescription) ? 'dark:text-white/80' : 'dark:text-white/80'}`}
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {t.downloadDescription}
          </div>
        </div>
        <div className="flex-shrink-0">
          <Download className="w-10 h-10 text-white" strokeWidth={2} />
        </div>
      </div>

      {/* Donate Card - Full Width */}
      <div 
        className="p-5 rounded-[32px] relative overflow-hidden flex items-center justify-between"
        style={{
          backgroundColor: 'var(--accent-light)',
        }}
      >
        <div>
          <div 
            className={`text-2xl font-bold text-white mb-1 ${isHebrewText(t.donate) ? 'dark:text-white' : 'dark:text-white'}`}
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {t.donate}
          </div>
          <div 
            className={`text-sm text-white/80 ${isHebrewText(t.donateDescription) ? 'dark:text-white/80' : 'dark:text-white/80'}`}
            style={{ fontFamily: "'Inter', sans-serif" }}
          >
            {t.donateDescription}
          </div>
        </div>
        <div className="flex-shrink-0">
          <Heart className="w-10 h-10 text-white" strokeWidth={2} />
        </div>
      </div>

      {/* About Section - Bubble/Pill Style with Icons */}
      <div 
        className="p-6 rounded-[32px]"
        style={{
          backgroundColor: 'var(--text-secondary)',
        }}
      >
        <div 
          className="text-2xl font-bold mb-5 text-white"
          style={{ 
            fontFamily: "'Inter', sans-serif",
          }}
        >
          {t.about}
        </div>
        
        {/* Bubble Pills Grid - Organic Layout */}
        <div className="flex flex-wrap gap-2">
          {/* Legal */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Scale className="w-5 h-5 text-white" strokeWidth={2} />
            <span className="text-white font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t.legal}
            </span>
          </a>

          {/* Terms */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <FileText className="w-5 h-5 text-white" strokeWidth={2} />
            <span className="text-white font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t.terms}
            </span>
          </a>

          {/* Privacy */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Shield className="w-5 h-5 text-white" strokeWidth={2} />
            <span className="text-white font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t.privacy}
            </span>
          </a>

          {/* Support */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <MessageCircle className="w-5 h-5 text-white" strokeWidth={2} />
            <span className="text-white font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t.support}
            </span>
          </a>

          {/* Bug */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Bug className="w-5 h-5 text-white" strokeWidth={2} />
            <span className="text-white font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t.reportBug}
            </span>
          </a>

          {/* GitHub */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Github className="w-5 h-5 text-white" strokeWidth={2} />
            <span className="text-white font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t.github}
            </span>
          </a>

          {/* Feedback */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Info className="w-5 h-5 text-white" strokeWidth={2} />
            <span className="text-white font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t.feedback}
            </span>
          </a>
        </div>
      </div>
    </div>
  );
}