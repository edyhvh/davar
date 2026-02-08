// Centralized legal content for web and mobile.
// Keep this in sync with docs/terms.md and docs/privacy.md.

export type LegalKind = "terms" | "privacy";

export type LegalDoc = {
  title: string;
  lastUpdated: string | null;
  body: string;
};

type LegalContent = Record<LegalKind, string>;

type LegalContentByLocale = {
  en: LegalContent;
};

const LEGAL_TITLES: Record<LegalKind, string> = {
  terms: "Terms of Service of Davar",
  privacy: "Privacy Policy of Davar",
};

const EN_TERMS = `# Terms of Service for Davar

**Effective Date:** February 8, 2026  
**Last Updated:** February 8, 2026

Welcome to Davar, an open-source project providing access to the Hebrew Bible (Tanakh) in its original language and hebrew translations of the Besorah, along with select translations and study resources. The Davar mobile application (the "App") is available on the Apple App Store and Google Play Store, and the associated website is located at https://davar.bible (collectively, the "Services").

These Terms of Service ("Terms") govern your access to and use of the Services. By downloading, installing, accessing, or using the App or Website, you agree to be bound by these Terms. If you do not agree, do not use the Services.

These Terms are provided in English. If you prefer another language, you may use your browser or device translation tools; the English version is authoritative.

## 1. Nature of the Services

Davar is a non-commercial, open-source project created to facilitate reading, studying, and meditating on the Hebrew Scriptures. The Services are provided "as is" without any warranty of accuracy, completeness, or fitness for any particular purpose beyond personal, non-commercial use.

## 2. User Eligibility

You must be at least 12 years old (or the minimum age required in your country to consent without parental approval). The Services are not directed to children under 12.

## 3. License to Use the Services

Subject to these Terms, we grant you a limited, non-exclusive, non-transferable, revocable license to access and use the Services for your **personal, non-commercial purposes** only.

You may not:

- Use the Services for any commercial purpose without our written permission.
- Modify, distribute, sell, rent, lease, or sublicense any part of the Services or restricted content (e.g., copyrighted translations) beyond the limits in our third-party licensing agreements.
- Extract or share portions of copyrighted translations (e.g., TS2009, TTH) beyond permitted limits (e.g., API up to 100 verses, daily emails/RSS up to 250 verses, SMS up to 10 verses).
- Reverse engineer, decompile, or attempt to extract source code from the App (except as permitted under open-source licenses applicable to specific components).
- Use the Services in any way that violates applicable laws or infringes third-party rights.
- Introduce viruses, malware, or other harmful code.
- Use the Services to create competing products or services.

All use must include required copyright notices for third-party content (see Section 6). You agree not to infringe any licensor's rights.

## 4. User-Generated Content (Future Feature)

Currently, the App does not allow saving or submitting content. If features like personal notes, highlights, or annotations are added:

- Any content you create remains your personal property.
- If you enable optional cloud synchronization, you grant us a limited license to store, process, and transmit that content solely to provide synchronization and backup.
- You are solely responsible for your content; it must not be unlawful, harmful, or infringe third-party rights.
- We may remove or disable access to any user content that violates these Terms or law.
- User content must not violate third-party licenses (e.g., no commercial sharing of annotated restricted translations).
- We may implement moderation tools; content may not be recoverable upon service changes or termination.

## 5. Open-Source Nature

Davar is an open-source project. The source code is publicly available on GitHub[](https://github.com/edyhvh/davar). Use of the source code is governed by the specific open-source license in the repository (e.g., MIT, GPL, etc.). These Terms apply only to the official App and Website distributed by us.

While the Davar code is open-source, certain biblical texts and data (e.g., TS2009, TTH) are included under separate restricted licenses and may not be freely redistributed. Forks must respect these by excluding or obtaining separate permissions for restricted content.

## 6. Intellectual Property

The Hebrew Bible text, morphological data, lexicons, and other resources are sourced from public domain or permissively licensed materials. We claim no ownership over the biblical texts themselves.

For copyrighted translations (TS2009, TTH), we operate under specific agreements requiring notices and restricting uses. The App interface, design elements, and original code not covered by third-party licenses are © Davar Project (Jhonny / @edyhvh), all rights reserved, except as expressly licensed.

**Key Sources and Licenses:**

| Component                    | Source                                                                       | License/Status                                              | Attribution/Requirements                                                                                                            | Restrictions/Notes                                                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Hebrew Morphology (morphhb)  | https://github.com/openscriptures/morphhb                                    | CC BY 4.0 (lemma/morphology); WLC text public domain        | Credit "Open Scriptures Hebrew Bible Project" in redistribution/use                                                                 | Attribution required for CC BY parts; no commercial restrictions beyond that                                        |
| Hebrew Lexicon               | https://github.com/openscriptures/HebrewLexicon                              | CC BY 4.0; BDB/Strong's text public domain                  | Credit "Open Scriptures Hebrew Bible Project"                                                                                       | Attribution required; public domain core                                                                            |
| Hebrew Text                  | https://github.com/hebrew-bible/hebrew-bible.github.io                       | GPL-3.0                                                     | Standard GPL (include license in forks)                                                                                             | Derivatives must be GPL; no additional commercial ban                                                               |
| English Translation (TS2009) | Licensed from Institute for Scripture Research (agreement July 15, 2025)     | Custom non-exclusive, non-commercial                        | Display: "Scripture taken from The Scriptures, Copyright by Institute for Scripture Research. Used by permission." in every display | Non-commercial only; API ≤100 verses, emails/RSS ≤250, SMS ≤10; no broad redistribution; error corrections required |
| Spanish Translation (TTH)    | Licensed from Natanael Doldan (agreement ~January 2026)                      | Custom non-exclusive, non-commercial                        | Display: "Texto tomado de la Traducción Textual del Hebreo, Copyright por Natanael Doldan. Usado con permiso." in every display     | Non-commercial only; similar limits to TS2009; error corrections; donations to licensor voluntary                   |
| Spanish Translation (SPABES) | https://ebible.org/spabes/                                                   | CC BY 4.0                                                   | Credit "AudioBiblia.org / Irma Flores (info@audiobiblia.org)"; note changes if modified                                             | Redistribution ok with attribution; indicate if modified                                                            |
| Delitzsch Strong's           | https://www.ph4.org/b4_1.php?l=iw                                            | Unclear (site ©2005-2026 Ph4)                               | None specified; recommend crediting source                                                                                          | License unclear—use cautiously or consider alternatives                                                             |
| Qumran Differences/Data      | https://codeberg.org/dandeto/deadseainsights + document from Natanael Doldan | No license specified (treat as restricted)                  | Credit repository/author or Natanael Doldan if applicable                                                                           | Unclear permissions—contact for explicit license; treat as non-redistributable                                      |
| Fonts (SBL Hebrew)           | https://www.sbl-site.org/educational/BiblicalFonts_SBLHebrew.aspx            | SIL Open Font License 1.1                                   | Font credit not required but recommended                                                                                            | Free for personal and commercial use; modifications allowed                                                         |
| Fonts (Dead Sea Scrolls)     | Custom font files                                                            | Licensed                                                    | None required                                                                                                                       | Used under license agreement                                                                                        |
| Fonts (Proto-Sinaitic)       | Custom generated fonts                                                       | Public domain / Custom                                      | None required                                                                                                                       | Generated for project use                                                                                           |
| Fonts (Google Fonts)         | https://fonts.google.com                                                     | SIL Open Font License (Cardo, Arimo, Inter, Jost, Suez One) | Font credit not required per license                                                                                                | Free for personal and commercial use; web loads from Google CDN                                                     |

Future translations will follow similar non-commercial, attributed models. Users must comply with third-party licenses when using/sharing content. Biblical data is not necessarily redistributable under the code's open-source license.

## 7. Disclaimers and Limitation of Liability

THE SERVICES ARE PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.

We are not responsible for:

- Errors, omissions, or inaccuracies in biblical text or data (including Qumran differences).
- Interruptions, delays, or data loss (including future notes).
- Any spiritual, emotional, or personal outcomes.

To the maximum extent permitted by law, our liability is limited to $0 (zero), as the Services are free.

## 8. Indemnification

You agree to indemnify and hold us harmless from claims, losses, or damages arising from your use of the Services in violation of these Terms or law.

## 9. Changes to the Services or Terms

We may modify, suspend, or discontinue any part of the Services without notice. We may update these Terms; continued use constitutes acceptance.

## 10. Privacy

Your use is also governed by our Privacy Policy (available at https://davar.bible/privacy or similar), which details minimal data collection (no accounts required currently; additional if cloud sync added).

## 11. Donations and Contributions

Davar accepts voluntary donations for development, maintenance, and expansion. Donations are non-refundable, with no expectation of goods, services, tax benefits, equity, or influence (Davar is not a registered nonprofit).

Methods (via Website):

- GitHub Sponsors (processed by GitHub; we receive after fees).
- Cryptocurrency to listed wallets (volatile; we are not responsible for fluctuations/fees/risks).

Donations used exclusively for project purposes. Periodic transparency reports posted (aggregate totals, categories). A portion may be voluntarily shared with licensors (e.g., TTH maintenance). Donors confirm legitimate sources; we may reject/return violating donations. No tax receipts issued.

## 12. Governing Law

These Terms are governed by the laws of the Republic of Argentina, without regard to conflict of laws principles. Disputes resolved in competent courts of the City of Buenos Aires, Argentina (subject to overriding terms in third-party licenses).

## 13. Third-Party Content

Davar incorporates third-party content under Section 6 licenses. We are not responsible for accuracy or availability. Changes (e.g., error corrections) may occur per licensor requests.

## 14. Entire Agreement

These Terms constitute the entire agreement regarding the Services and supersede prior understandings.

## Contact Us

For questions: hi@davar.bible

May the use of Davar bring you closer to understanding and walking in YHVH’s eternal Word.
`;

const EN_PRIVACY = `# Privacy Policy for Davar

**Effective Date:** February 8, 2026  
**Last Updated:** February 8, 2026

Davar (the "App" and "Website") is an open-source project providing access to the Hebrew Bible (Tanakh) in its original language. The App is available on the Apple App Store and Google Play Store, and the Website is hosted at https://davar.bible. This Privacy Policy explains our practices regarding any information when you use the App or visit the Website.

We are committed to your privacy, minimal data practices, and transparency as an open-source initiative. We do not collect personally identifiable information (PII) at this time. Our practices comply with Argentina's Personal Data Protection Law (Ley 25.326) and equivalent international standards (e.g., GDPR for EU users where applicable).

This Privacy Policy is provided in English. If you prefer another language, you may use your browser or device translation tools; the English version is authoritative.

## 1. Information We Collect – Current Practices

We do not collect any personally identifiable information (such as names, email addresses, phone numbers, precise location, device IDs linked to you, or other identifiers).

- **App Preferences and Local Data**: You can adjust display settings (font size, theme, text alignment, reading mode). These are stored locally on your device only and never transmitted to us or any third party.
- **Verse Notes and Annotations (Future Feature)**: Currently, the App does not support saving notes, highlights, or annotations on verses. If and when we implement this feature:
  - Notes will first be stored locally on your device (no transmission required for basic use).
  - In a future update, we may offer optional cloud synchronization to back up or access notes across devices. This would require your explicit consent and would involve transmitting minimal data (e.g., notes text, verse references, timestamps) to secure servers solely for sync and backup.
  - Any such cloud feature would be optional, encrypted in transit and at rest, and used exclusively for app functionality. We would not use notes for advertising, profiling, or sharing with third parties without additional consent.
- **Analytics or Tracking**: Currently, no analytics, cookies, tracking pixels, or third-party SDKs collect usage data. If we introduce anonymous analytics in the future (e.g., aggregated crash reports or usage stats like feature counts, without IPs or identifiers), we will update this Policy, declare it in app stores, and provide opt-out options.
- **Website Third-Party Services**:
  - **Google Fonts**: The Website loads fonts from Google Fonts CDN (fonts.googleapis.com). When you visit the Website, Google receives your IP address and User-Agent as part of the font delivery process. This is necessary for proper text display. We do not control Google's data practices; see [Google's Privacy Policy](https://policies.google.com/privacy).
  - **App Store Badge Images**: The Website displays download badges loaded from Apple and Google servers (developer.apple.com and play.google.com). Visiting pages with these images may transmit your IP address to Apple and Google.
  - **Website Hosting**: The Website is hosted by a third-party hosting provider that may process standard web server logs (IP addresses, request timestamps, URLs accessed) as part of content delivery. These logs are automatically generated and used solely for infrastructure operation and security.
- **API Rate Limiting**: Our API server temporarily processes IP addresses in memory for rate limiting and abuse prevention to ensure fair access for all users. These are not stored persistently.
- **Website Contact**: The Website lists a contact email for feedback or questions. If you email us, we receive your email address and message content voluntarily. We use this only to respond and delete it after support resolution (typically within 30 days).

## 2. How We Use Information

Any limited information (e.g., voluntary emails) is used solely to provide support. No personal data is used for marketing, advertising, or profiling. Future features like cloud-synced notes would be used exclusively to enable saving and retrieving your personal annotations on Scripture.

## 3. Information Sharing and Disclosure

We do not share, sell, or disclose any user information because we do not collect personal data automatically. As an open-source project on GitHub[](https://github.com/edyhvh/davar), any contributions or issues you submit follow GitHub's privacy practices.

If cloud features are added, notes would be processed by service providers (e.g., cloud storage like AWS or Google Cloud) under strict data processing agreements ensuring they act only on our instructions, with equivalent protection, and no further use.

No data is transferred internationally at this time. For future cloud features, transfers (if any) would ensure adequate safeguards under Ley 25.326.

## 4. Data Storage and Security

- **Local Data** (preferences, future local notes) stays on your device.
- Any future cloud storage would use industry-standard encryption (in transit via HTTPS and at rest where applicable) and security measures.
- We do not maintain servers holding personal user data currently.

## 5. Children's Privacy

The App and Website are not directed to children under 13. We do not knowingly collect data from children. If we learn of such collection, we will delete it promptly.

## 6. Your Rights

Under Ley 25.326 and similar laws, you have rights to access, rectify, update, or delete any personal data we hold (though currently none). For voluntary emails or future notes:

- Contact us to exercise rights (e.g., delete synced notes).
- We respond within 10 days (or as required by law).
- No fees for rights requests unless excessive.

## 7. Changes to This Privacy Policy

We may update this Policy to reflect new features (e.g., verse notes with optional cloud sync), legal requirements, or improvements. We will post the revised version at https://davar.bible/privacy with the new effective date. For significant changes involving new data collection, we will notify you in-app (e.g., pop-up or settings notice) and obtain consent where required by law before enabling the feature.

Continued use after changes means acceptance of the updated Policy.

## 8. Contact Us

For questions about this Policy or privacy, contact us at: hi@davar.bible

**Open-Source Note**: Davar is open source. The code is available on GitHub[](https://github.com/edyhvh/davar). This does not involve personal data collection through the repository.

May Davar be a tool to draw you closer to YHVH’s Word in its pure form.
`;

const LEGAL_CONTENT: LegalContentByLocale = {
  en: {
    terms: EN_TERMS,
    privacy: EN_PRIVACY,
  },
};

export const getLegalContent = (
  kind: LegalKind,
  locale: keyof LegalContentByLocale = "en",
): string => LEGAL_CONTENT[locale][kind];

const LAST_UPDATED_REGEX = /^\*\*Last Updated:\*\*\s*(.+)$/i;
const EFFECTIVE_DATE_REGEX = /^\*\*Effective Date:\*\*\s*(.+)$/i;
const HEADING_REGEX = /^#\s+/;

const extractLastUpdated = (markdown: string): string | null => {
  const match = markdown
    .split("\n")
    .map((line) => line.trim())
    .find((line) => LAST_UPDATED_REGEX.test(line));

  if (!match) return null;
  const result = LAST_UPDATED_REGEX.exec(match);
  return result?.[1]?.trim() ?? null;
};

const stripHeaderLines = (markdown: string): string => {
  const lines = markdown.split("\n");
  const filtered = lines.filter((line) => {
    const trimmed = line.trim();
    if (!trimmed) return true;
    if (HEADING_REGEX.test(trimmed)) return false;
    if (EFFECTIVE_DATE_REGEX.test(trimmed)) return false;
    if (LAST_UPDATED_REGEX.test(trimmed)) return false;
    return true;
  });
  return filtered.join("\n").trim();
};

export const getLegalDoc = (
  kind: LegalKind,
  locale: keyof LegalContentByLocale = "en",
): LegalDoc => {
  const markdown = getLegalContent(kind, locale);
  return {
    title: LEGAL_TITLES[kind],
    lastUpdated: extractLastUpdated(markdown),
    body: stripHeaderLines(markdown),
  };
};

const legalContentApi = {
  getLegalContent,
  getLegalDoc,
};

export default legalContentApi;
