import { useTranslation } from "@/src/i18n/useTranslation";
import { LegalScreen } from "@/src/screens/LegalScreen";

const PRIVACY_URL =
  "https://raw.githubusercontent.com/edyhvh/davar/main/docs/privacy.md";

export default function PrivacyScreen() {
  const { t } = useTranslation();

  return (
    <LegalScreen title={t("home.about.items.privacy")} docUrl={PRIVACY_URL} />
  );
}
