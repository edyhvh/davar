# Google Play Console Answers (Ready to Paste)

Last updated: 2026-04-01
Use this for the current release only (new app, no in-app accounts, no ads, no IAP).

## 1) App Content: Target Audience

Recommended selection:
- Older teens and adults (13+)
- Not directed primarily to children

Do not select child-directed/families options for this release unless product intent changes.

## 2) App Content: Account Creation / Login

Answer:
- No, users cannot create an account in this app.
- No login is required to use core features.

## 3) App Content: Ads

Answer:
- This app does not show ads.

## 4) App Content: In-App Purchases / Subscriptions

Answer:
- No in-app purchases.
- No subscriptions.
- No Google Play Billing usage.

## 5) Data Safety: Top-Level

Recommended path for current behavior:
- Does your app collect or share required user data types? -> No
- Is all user data encrypted in transit? -> Yes (for any network communication that occurs)
- Does your app provide a way for users to request deletion of data? -> Yes (contact mechanism) or Not applicable for account data

Notes:
- Keep these answers strictly aligned with runtime behavior and SDK behavior.
- If you later enable analytics, cloud sync, accounts, or ads, these answers must be updated before release.

## 6) Data Deletion Questions

Current app model:
- No in-app account creation.
- No account deletion flow required for this release.
- Provide data deletion request contact path:
  - hi@davar.bible

If the form asks for a URL/web resource for deletion requests, use:
- https://davar.bible/privacy

## 7) Privacy Policy Field

Play Console privacy policy URL:
- https://davar.bible/privacy

Support contact:
- hi@davar.bible

## 8) Content Rating Questionnaire (IARC)

Declare accurately based on current app features:
- No user-generated content
- No real-money gambling
- No dating/matchmaking
- No controlled substances sales
- No violent/sexual interactive gameplay content
- No ads

This should generally result in a low-age rating for scripture reading/study content, but always submit truthful responses for each prompt.

## 9) Store Listing Copy Guardrails

Use wording that matches current app behavior:
- Scripture reading and study app
- No account required
- No ads
- No in-app purchases

Avoid claiming features not yet shipped (for example: account sync, social features, UGC moderation, advanced analytics).

## 10) Submission Gate (Final Check)

Before clicking Submit:
- Target SDK in final artifact is compliant for new app submission.
- Data safety answers match actual code and SDK behavior.
- Privacy policy URL works publicly.
- Content rating completed (not Unrated).
- Audience declaration aligns with legal text (13+).

## 11) Store Listing Descriptions (Ready to Paste)

Use these as a safe baseline for the first submission. You can refine tone later without changing policy claims.

### Short Description (English)

Read Tanakh with the Hebrew translation of the Besorah and Qumran references.

### Short Description (Spanish)

Estudia el Tanaj con la traducción hebrea de la Besorah y referencias de Qumran.

### Short Description (Hebrew)

קראו ולמדו את התנ"ך עם התרגום העברי של הבשורה והפניות מקומראן.

### Long Description (English)

Davar is a minimalist Bible study app designed for focused reading of the Hebrew Scriptures (Tanakh), the Besorah, and related study sources.

Read the text in a calm, distraction-free interface built for deep study, reflection, and daily use. Davar prioritizes clarity, typography, and navigation so you can stay immersed in the text.

Texts and translation support in this release include:
- Tanakh in Hebrew
- Besorah with Delitzsch Hebrew text
- English translation support (including TS2009 where available)
- Spanish translation support (including TTH and SPABES where available)
- Qumran references and comparative study material where available

Current release highlights:
- Hebrew Scripture reading and study experience
- Translation support for comparative reading
- Fast navigation by book, chapter, and verse
- No account required
- No in-app purchases

Davar is built as an open-source, non-commercial project with a strong focus on respectful design, textual study, and transparency.

### Long Description (Spanish)

Davar es una app minimalista de estudio bíblico diseñada para una lectura enfocada de las Escrituras Hebreas (Tanaj), la Besorah y fuentes de estudio relacionadas.

Lee el texto en una interfaz tranquila y sin distracciones, creada para el estudio profundo, la reflexión y el uso diario. Davar prioriza la claridad, la tipografía y la navegación para ayudarte a mantenerte centrado en el texto.

Textos y traducciones incluidas en esta versión:
- Tanaj en hebreo
- Besorah con texto hebreo de Delitzsch
- Soporte de traducción al inglés (incluyendo TS2009 cuando está disponible)
- Soporte de traducción al español (incluyendo TTH y SPABES cuando está disponible)
- Referencias de Qumrán y material comparativo cuando está disponible

Aspectos principales de esta versión:
- Lectura y estudio de las Escrituras en hebreo
- Soporte de traducciones para lectura comparativa
- Navegación rápida por libro, capítulo y versículo
- No requiere cuenta
- Sin compras dentro de la app

Davar es un proyecto abierto y no comercial, enfocado en un diseño respetuoso, el estudio textual y la transparencia.

### Long Description (Hebrew)

אפליקציה מינימליסטית ללימוד כתבי הקודש, שנבנתה לקריאה ממוקדת של כתבי הקודש העבריים (תנ"ך), הבשורה ומקורות לימוד נוספים

האפליקציה מציעה ממשק שקט וללא הסחות דעת, המתאים ללימוד מעמיק, להתבוננות ולשימוש יומיומי. מושם בה דגש על בהירות, טיפוגרפיה טובה וניווט נוח כדי לשמור על ריכוז בטקסט

הטקסטים והתמיכות בתרגום בגרסה זו כוללים:

בגרסה זו כלולים טקסט התנ"ך בעברית, הבשורה עם הטקסט העברי של דליטש, תמיכה בתרגום לאנגלית (כולל TS2009 כאשר זמין), תמיכה בתרגום לספרדית (כולל TTH ו-SPABES כאשר זמין), וכן הפניות מקומראן וחומר השוואתי כאשר זמין

עיקרי הגרסה הנוכחית:

הגרסה הנוכחית כוללת קריאה ולימוד של כתבי הקודש בעברית, תמיכה בתרגומים לקריאה השוואתית, ניווט מהיר לפי ספר, פרק ופסוק, ללא צורך בחשבון משתמש וללא רכישות בתוך האפליקציה

זהו פרויקט קוד פתוח ולא מסחרי, עם דגש על עיצוב מכבד, לימוד טקסטואלי ושקיפות (Davar)
