import { useTranslation } from "@/src/i18n/useTranslation";
import { LegalScreen } from "@/src/screens/LegalScreen";

const TERMS_URL =
  "https://raw.githubusercontent.com/edyhvh/davar/main/docs/terms.md";

export default function TermsScreen() {
  const { t } = useTranslation();

  return (
    <LegalScreen title={t("home.about.items.terms")} docUrl={TERMS_URL} />
  );
}
