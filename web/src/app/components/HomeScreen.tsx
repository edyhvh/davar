import React from "react";
import {
  Bug,
  FileText,
  Github,
  Info,
  MessageCircle,
  Scale,
  Shield,
} from "lucide-react";
import { useTranslation } from "../hooks/useTranslation";

interface HomeScreenProps {
  language: "en" | "es" | "he";
}

export function HomeScreen({ language }: HomeScreenProps) {
  const { t } = useTranslation(language);
  const sourceItems = [
    {
      label: t("home.sources.hebrewTextLabel"),
      value: t("home.sources.hebrewTextValue"),
    },
    {
      label: t("home.sources.dictionaryLabel"),
      value: t("home.sources.dictionaryValue"),
      note: t("home.sources.dictionaryNote"),
    },
    {
      label: t("home.sources.englishTranslationLabel"),
      value: t("home.sources.englishTranslationValue"),
    },
    {
      label: t("home.sources.spanishTranslationLabel"),
      value: t("home.sources.spanishTranslationValue"),
    },
    {
      label: t("home.sources.besorahLabel"),
      value: t("home.sources.besorahValue"),
    },
  ];
  const aboutItems = [
    { label: t("home.aboutItems.terms"), Icon: FileText, href: "/terms" },
    { label: t("home.aboutItems.privacy"), Icon: Shield, href: "/privacy" },
    { label: t("home.aboutItems.support"), Icon: MessageCircle, href: "#" },
    { label: t("home.aboutItems.bug"), Icon: Bug, href: "#" },
    { label: t("home.aboutItems.github"), Icon: Github, href: "#" },
    { label: t("home.aboutItems.feedback"), Icon: Info, href: "#" },
  ];

  return (
    <div className="space-y-4 pb-24">
      <div className="min-h-[40vh] flex items-center justify-center">
        <div className="text-center">
          <div className="text-sm tracking-[0.3em] uppercase text-[var(--copper-highlight)] mb-6">
            {t("home.sourcesTitle")}
          </div>
          <div className="space-y-3">
            {sourceItems.map((item) => (
              <div
                key={item.label}
                className="flex items-center justify-center gap-2 text-sm text-[var(--text-primary)]"
              >
                <span style={{ fontFamily: "'Inter', sans-serif" }}>
                  {item.label}{" "}
                  <span className="font-semibold">{item.value}</span>
                  {item.note ?? ""}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="min-h-[30vh] flex items-center justify-center">
        <div className="text-center">
          <div className="text-sm tracking-[0.3em] uppercase text-[var(--copper-highlight)] mb-6">
            {t("home.aboutTitle")}
          </div>
          <div className="space-y-3">
            {aboutItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="flex items-center justify-center gap-2 text-sm text-[var(--text-primary)] hover:text-[var(--text-secondary-muted)]"
              >
                <item.Icon className="w-4 h-4 text-[var(--copper-highlight)]" />
                <span style={{ fontFamily: "'Inter', sans-serif" }}>
                  {item.label}
                </span>
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-6 pt-2">
        <a
          href="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={t("common.downloadOnAppStore")}
        >
          <img
            src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
            alt={t("common.downloadOnAppStore")}
            className="h-12"
          />
        </a>
        <a
          href="https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png"
          target="_blank"
          rel="noopener noreferrer"
          aria-label={t("common.getOnGooglePlay")}
        >
          <img
            src="https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png"
            alt={t("common.getOnGooglePlay")}
            className="h-14"
          />
        </a>
      </div>
    </div>
  );
}
