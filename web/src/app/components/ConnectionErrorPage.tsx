import React from "react";
import { RefreshCw, WifiOff } from "lucide-react";
import { useTranslation, type AppLanguage } from "../hooks/useTranslation";

interface ConnectionErrorPageProps {
  language: AppLanguage;
  onRetry?: () => void;
}

export function ConnectionErrorPage({
  language,
  onRetry,
}: ConnectionErrorPageProps) {
  const { t } = useTranslation(language);

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center px-6">
        {/* Icon */}
        <div className="mb-6 flex justify-center">
          <WifiOff className="w-12 h-12 text-[var(--copper-highlight)]" />
        </div>

        {/* Title */}
        <h1
          className="text-xl mb-4 text-[var(--text-primary)]"
          style={{ fontFamily: "'Jost', sans-serif" }}
        >
          {t("errors.connection.title")}
        </h1>

        {/* Message */}
        <p
          className="text-sm text-[var(--text-secondary)] mb-6"
          style={{ fontFamily: "'Arimo', sans-serif" }}
        >
          {t("errors.connection.message")}
        </p>

        {/* Action Buttons */}
        <div className="flex items-center justify-center gap-3">
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-dark)] transition-colors"
              style={{ fontFamily: "'Jost', sans-serif" }}
            >
              <RefreshCw className="w-4 h-4" />
              {t("errors.connection.retry")}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
