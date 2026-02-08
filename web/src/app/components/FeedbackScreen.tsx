import React from "react";
import { useTranslation, getSupportTelegramUrl } from "../hooks/useTranslation";

interface FeedbackScreenProps {
  language: "en" | "es" | "he";
  onBack: () => void;
}

export function FeedbackScreen({ language, onBack }: FeedbackScreenProps) {
  const { t } = useTranslation(language);

  return (
    <div className="legal-page">
      <div className="legal-hero">
        <div className="legal-hero-inner">
          <button className="legal-back" onClick={onBack} type="button">
            {t("navigation.backToApp")}
          </button>
          <h1 className="legal-title">{t("home.aboutItems.feedback")}</h1>
        </div>
      </div>

      <div className="legal-content feedback-content">
        <div className="legal-prose">
          <p>{t("feedback.emailInstruction", { email: "hi@davar.bible" })}</p>
          <p>{t("feedback.telegramReminder")}</p>
          <p>
            <a
              href={getSupportTelegramUrl(language)}
              target="_blank"
              rel="noopener noreferrer"
            >
              {t("feedback.telegramLink")}
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
