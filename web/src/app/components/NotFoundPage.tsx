import React from "react";
import { AlertCircle, Home } from "lucide-react";
import { useTranslation, type AppLanguage } from "../hooks/useTranslation";

interface NotFoundPageProps {
  language: AppLanguage;
}

export function NotFoundPage({ language }: NotFoundPageProps) {
  const { t } = useTranslation(language);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center px-6">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          <AlertCircle className="w-12 h-12 text-[var(--copper-highlight)]" />
        </div>

        {/* Title */}
        <h1
          className="text-xl mb-4 text-[var(--text-primary)]"
          style={{ fontFamily: "'Jost', sans-serif" }}
        >
          {t("errors.notFound.title")}
        </h1>

        {/* Message */}
        <p
          className="text-sm text-[var(--text-secondary)] mb-6"
          style={{ fontFamily: "'Arimo', sans-serif" }}
        >
          {t("errors.notFound.message")}
        </p>

        {/* Go Home Button */}
        <a
          href="/home"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-dark)] transition-colors"
          style={{ fontFamily: "'Jost', sans-serif" }}
        >
          <Home className="w-4 h-4" />
          {t("errors.notFound.goHome")}
        </a>
      </div>
    </div>
  );
}
