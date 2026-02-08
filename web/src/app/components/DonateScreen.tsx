import React from 'react';
import { useTranslation, type AppLanguage } from '../hooks/useTranslation';

const DONATION_CONFIG = {
  githubSponsor: 'https://github.com/sponsors/edyhvh',
} as const;

const GithubSponsorsIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path
      fillRule="evenodd"
      d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.5-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
    />
  </svg>
);

const CreditCardIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 16 16" fill="currentColor">
    <path d="M0 4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V4zm2-1a1 1 0 0 0-1 1v1h14V4a1 1 0 0 0-1-1H2zm13 4H1v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V7z" />
  </svg>
);

const TelegramIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="currentColor"
    aria-hidden="true"
  >
    <path d="M9.993 15.43 9.66 20.06c.506 0 .726-.217.99-.478l2.37-2.28 4.91 3.595c.902.498 1.54.235 1.76-.832l3.2-15.02c.293-1.326-.48-1.845-1.33-1.53L2.1 9.18c-1.29.49-1.27 1.19-.22 1.51l4.86 1.52 11.28-7.12c.53-.35 1.01-.16.61.19L9.993 15.43z" />
  </svg>
);

interface DonateScreenProps {
  language: AppLanguage;
}

export function DonateScreen({ language }: DonateScreenProps) {
  const { t } = useTranslation(language);
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <div className="space-y-6 text-[var(--text-secondary)]" style={{ fontFamily: "'Inter', sans-serif" }}>
          <div className="flex items-center justify-center gap-3 text-base">
            <div className="flex items-center gap-1">
              <GithubSponsorsIcon className="w-6 h-6" />
              <CreditCardIcon className="w-5 h-5" />
            </div>
            <span className="font-medium">{t('donate.githubSponsor')}</span>
            <a
              href={DONATION_CONFIG.githubSponsor}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline underline-offset-2 transition-colors"
            >
              @edyhvh
            </a>
          </div>

          <p className="text-sm text-[var(--text-secondary)]">
            {t('donate.contactPrefix')}{' '}
            <span className="inline-flex items-center gap-2">
              <span className="inline-flex items-center gap-1 font-medium text-[var(--text-primary)]">
                <TelegramIcon className="w-4 h-4" />
                {t('donate.telegramLabel')}
              </span>
              <a
                href="https://t.me/edyhvh"
                target="_blank"
                rel="noopener noreferrer"
                className="underline underline-offset-2 hover:text-[var(--text-primary)] transition-colors"
              >
                @edyhvh
              </a>
            </span>
          </p>

          <div className="flex flex-wrap items-center justify-center gap-6 pt-6">
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
      </div>
    </div>
  );
}
