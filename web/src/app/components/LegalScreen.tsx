import React, { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useTranslation } from "../hooks/useTranslation";

const LEGAL_DOCS = {
  terms: "https://raw.githubusercontent.com/edyhvh/davar/main/docs/terms.md",
  privacy: "https://raw.githubusercontent.com/edyhvh/davar/main/docs/privacy.md",
} as const;

type LegalKind = keyof typeof LEGAL_DOCS;

interface LegalScreenProps {
  kind: LegalKind;
  language: "en" | "es" | "he";
  onBack: () => void;
}

export function LegalScreen({ kind, language, onBack }: LegalScreenProps) {
  const { t } = useTranslation(language);
  const [markdown, setMarkdown] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const title = useMemo(
    () =>
      kind === "terms"
        ? t("home.aboutItems.terms")
        : t("home.aboutItems.privacy"),
    [kind, t],
  );

  useEffect(() => {
    const controller = new AbortController();

    const loadDoc = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await fetch(LEGAL_DOCS[kind], {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error("Failed to load legal content.");
        }
        const text = await response.text();
        setMarkdown(text);
      } catch (err) {
        if ((err as { name?: string }).name === "AbortError") {
          return;
        }
        setError(t("errors.uiFallbackMessage"));
      } finally {
        setIsLoading(false);
      }
    };

    void loadDoc();

    return () => controller.abort();
  }, [kind, t]);

  return (
    <div className="legal-page">
      <div className="legal-hero">
        <div className="legal-hero-inner">
          <button className="legal-back" onClick={onBack} type="button">
            {t("navigation.backToApp")}
          </button>
          <div className="legal-kicker">Davar Legal</div>
          <h1 className="legal-title">{title}</h1>
          <p className="legal-subtitle">
            Quiet clarity for important agreements and commitments.
          </p>
        </div>
      </div>

      <div className="legal-content">
        {isLoading && (
          <div className="legal-status">{t("common.loading")}</div>
        )}
        {!isLoading && error && <div className="legal-status">{error}</div>}
        {!isLoading && !error && (
          <div className="legal-prose">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                a: ({ href, children, ...props }) => (
                  <a
                    {...props}
                    href={href}
                    target="_blank"
                    rel="noreferrer"
                  >
                    {children}
                  </a>
                ),
              }}
            >
              {markdown}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
