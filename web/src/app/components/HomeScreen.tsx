import React from 'react';
import { Download, Heart, ExternalLink, Github, Scale, FileText, Shield, MessageCircle, Bug, Info } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';

interface HomeScreenProps {
  language: 'en' | 'es' | 'he';
}

// Biblical Hebrew months (not rabbinic)
const biblicalMonths = [
  'Aviv', 'Ziv', 'Sivan', 'Tammuz', 'Av', 'Elul',
  'Ethanim', 'Bul', 'Kislev', 'Tevet', 'Shevat', 'Adar'
];

export function HomeScreen({ language }: HomeScreenProps) {
  const { t, get } = useTranslation(language);
  const hebrewDate = t('home.calendar.dateLabel');
  const dayNames = get<string[]>('home.calendar.dayNames', [
    'Sun',
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat',
  ]);

  // Check if text is Hebrew (contains Hebrew characters)
  const isHebrewText = (text: string) => /[\u0590-\u05FF]/.test(text);

  // Generate upcoming days starting from 10th (hardcoded for demo)
  const upcomingDays = [];
  const startDay = 10; // Aviv 10th
  
  for (let i = 0; i < 14; i++) {
    const day = startDay + i;
    // Simplified day names for demo
    const dayName = dayNames[i % dayNames.length] ?? dayNames[0];
    
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
      <div className="flex flex-col gap-4 lg:flex-row">
        <div className="flex-1 min-w-0">
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
                  className="text-sm font-medium text-[var(--text-primary)]"
                  style={{ 
                    fontFamily: "'Inter', sans-serif",
                  }}
                >
                  {t('home.todayIs')}
                </span>
              </div>
            </div>
            <div 
              className="text-7xl font-bold leading-none tracking-tight mb-8 text-[var(--text-primary)]"
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
                    className="text-3xl font-bold text-center text-[var(--text-primary)]"
                    style={{ 
                      fontFamily: "'Inter', sans-serif",
                    }}
                  >
                    {item.day}
                  </div>
                  
                  {/* Day name */}
                  <div 
                    className={`text-xs text-center mt-1 ${
                      item.isToday ? 'text-[var(--text-primary)] opacity-80' : 'text-[var(--text-primary)]'
                    }`}
                    style={{ fontFamily: "'Inter', sans-serif" }}
                  >
                    {item.dayName}
                  </div>
                  
                  {/* Pesach label */}
                  {item.isPesach && (
                    <div className="mt-2 text-center">
                      <div 
                        className="text-xs font-medium text-[var(--text-primary)]" 
                        style={{ 
                          fontFamily: "'Inter', sans-serif",
                        }}
                      >
                        {t('home.calendar.pesachLabel')}
                      </div>
                      <div 
                        className="text-[10px] text-[var(--text-primary)]" 
                        style={{ 
                          fontFamily: "'Cardo', serif",
                        }}
                      >
                        {t('home.calendar.pesachHebrew')}
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
        </div>

        <div className="flex-1 min-w-0">
          {/* Info Section - Neumorphic Column */}
          <div
            className="p-6 rounded-[32px] h-full"
            style={{
              backgroundColor: 'var(--about-surface)',
              boxShadow: '0 28px 50px rgba(13, 39, 80, 0.16)',
            }}
          >
            <div className="space-y-3 text-[var(--about-text)]" style={{ fontFamily: "'Inter', sans-serif" }}>
              <div
                className="text-2xl font-bold mb-2 text-[var(--about-text)]"
                style={{ fontFamily: "'Inter', sans-serif" }}
              >
                {t('home.sourcesTitle')}
              </div>
              <div className="text-base text-[var(--about-text)] opacity-80">
                {t('home.sources.hebrewTextLabel')} <span className="font-semibold text-[var(--about-text)] opacity-100">{t('home.sources.hebrewTextValue')}</span>
              </div>
              <div className="text-base text-[var(--about-text)] opacity-80">
                {t('home.sources.dictionaryLabel')} <span className="font-semibold text-[var(--about-text)] opacity-100">{t('home.sources.dictionaryValue')}</span>{t('home.sources.dictionaryNote')}
              </div>
              <div className="text-base text-[var(--about-text)] opacity-80">
                {t('home.sources.englishTranslationLabel')} <span className="font-semibold text-[var(--about-text)] opacity-100">{t('home.sources.englishTranslationValue')}</span>
              </div>
              <div className="text-base text-[var(--about-text)] opacity-80">
                {t('home.sources.spanishTranslationLabel')} <span className="font-semibold text-[var(--about-text)] opacity-100">{t('home.sources.spanishTranslationValue')}</span>
              </div>
              <div className="text-base text-[var(--about-text)] opacity-80">
                {t('home.sources.besorahLabel')} <span className="font-semibold text-[var(--about-text)] opacity-100">{t('home.sources.besorahValue')}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* About Section - Bubble/Pill Style with Icons */}
      <div 
        className="p-6 rounded-[32px]"
        style={{
          backgroundColor: 'var(--about-surface)',
        }}
      >
        <div 
          className="text-2xl font-bold mb-5 text-[var(--about-text)]"
          style={{ 
            fontFamily: "'Inter', sans-serif",
          }}
        >
          {t('home.aboutTitle')}
        </div>
        
        {/* Bubble Pills Grid - Organic Layout */}
        <div className="flex flex-wrap gap-2">
          {/* Legal */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Scale className="w-5 h-5 text-[var(--about-text)]" strokeWidth={2} />
            <span className="text-[var(--about-text)] font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t('home.aboutItems.legal')}
            </span>
          </a>

          {/* Terms */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <FileText className="w-5 h-5 text-[var(--about-text)]" strokeWidth={2} />
            <span className="text-[var(--about-text)] font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t('home.aboutItems.terms')}
            </span>
          </a>

          {/* Privacy */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Shield className="w-5 h-5 text-[var(--about-text)]" strokeWidth={2} />
            <span className="text-[var(--about-text)] font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t('home.aboutItems.privacy')}
            </span>
          </a>

          {/* Support */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <MessageCircle className="w-5 h-5 text-[var(--about-text)]" strokeWidth={2} />
            <span className="text-[var(--about-text)] font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t('home.aboutItems.support')}
            </span>
          </a>

          {/* Bug */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Bug className="w-5 h-5 text-[var(--about-text)]" strokeWidth={2} />
            <span className="text-[var(--about-text)] font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t('home.aboutItems.bug')}
            </span>
          </a>

          {/* GitHub */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Github className="w-5 h-5 text-[var(--about-text)]" strokeWidth={2} />
            <span className="text-[var(--about-text)] font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t('home.aboutItems.github')}
            </span>
          </a>

          {/* Feedback */}
          <a 
            href="#" 
            className="inline-flex items-center gap-2.5 px-5 py-3 rounded-full bg-white/20 hover:bg-white/30 backdrop-blur-sm transition-all border border-white/30"
          >
            <Info className="w-5 h-5 text-[var(--about-text)]" strokeWidth={2} />
            <span className="text-[var(--about-text)] font-medium text-base" style={{ fontFamily: "'Inter', sans-serif" }}>
              {t('home.aboutItems.feedback')}
            </span>
          </a>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-6 pt-2">
        <a
          href="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={t('common.downloadOnAppStore')}
        >
          <img
            src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
            alt={t('common.downloadOnAppStore')}
            className="h-12"
          />
        </a>
        <a
          href="https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={t('common.getOnGooglePlay')}
        >
          <img
            src="https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png"
            alt={t('common.getOnGooglePlay')}
            className="h-14"
          />
        </a>
      </div>

    </div>
  );
}