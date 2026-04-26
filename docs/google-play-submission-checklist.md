# Google Play Submission Checklist (Davar)

Last updated: 2026-04-26
Scope: New app submission, no in-app account creation, Android mobile release.

## 1. Hard Blockers (must be true before upload)

- [ ] Target API for submitted artifact is compliant for new apps.
  - Policy baseline (as of current review): new apps must target Android 15 (API 35) or higher.
  - Verify on generated artifact/manifests in release build outputs before upload.
- [ ] If release minification/obfuscation is enabled (R8/ProGuard), upload deobfuscation file for that exact bundle version.
  - File: `mapping.txt`
  - Typical local path: `mobile/android/app/build/outputs/mapping/release/mapping.txt`
  - Upload location: Play Console -> App Bundle Explorer -> selected version -> Deobfuscation files.
- [ ] Privacy policy URL is public, active, non-PDF, and added in Play Console.
  - URL: https://davar.bible/privacy
- [ ] Data safety form is completed and submitted.
- [ ] Data deletion questions are completed in Data safety.
- [ ] Content rating questionnaire is completed (app must not be Unrated).

## 2. App Content and Declarations

- [ ] App type/audience decision is explicit in Play Console.
  - Recommended for current release: 13+ only (not child-directed).
- [ ] No account creation declaration is accurate.
  - Current app behavior: no user registration/login flow.
- [ ] Ads declaration is accurate.
  - Current app behavior: no ad SDKs or ad delivery.
- [ ] In-app purchases/subscriptions declaration is accurate.
  - Current app behavior: no Play Billing integration.

## 3. Metadata Quality (Store Listing)

- [ ] Title, short description, and full description accurately describe current features only.
- [ ] Listing does not imply features not present (for example, cloud sync or user accounts).
- [ ] Screenshots and icon match current app UI and functionality.
- [ ] Contact email is configured and monitored.
  - Email: hi@davar.bible

## 4. Data Safety Answers (current recommended direction)

Use this only if release behavior remains unchanged:

- [ ] Collection/sharing claims match real app behavior and included SDK behavior.
- [ ] If declaring no collection/sharing, confirm no analytics/ad/auth SDK behavior contradicts that.
- [ ] Encryption in transit answer is accurate for any network data flows.
- [ ] Data deletion mechanism answer is accurate for current no-account model.

## 5. Permission Hygiene

- [ ] Confirm no unnecessary sensitive permissions in final manifest.
- [ ] If a permission is declared, ensure it supports a user-visible core feature.
- [ ] Confirm permission prompts, if any, are contextual and not coercive.

## 6. Functional Review (Policy UX Gate)

- [ ] Core reading flow works with no crashes/freezes.
- [ ] Legal screens load correctly in-app.
- [ ] Privacy and Terms links are reachable.
- [ ] No dead-end startup states or placeholder screens in release build.

## 7. Release Evidence Pack (recommended)

Keep these for fast response if review asks questions:

- [ ] Screenshot of Data safety final answers.
- [ ] Screenshot of Content rating completion.
- [ ] Screenshot of App content declarations.
- [ ] Final merged manifest used in release review.
- [ ] Notes on why no account deletion flow applies (no in-app account creation).

## 8. Final Go/No-Go

Go only if all are true:

- [ ] Hard blockers complete.
- [ ] Declarations are truthful and consistent with app behavior.
- [ ] Store metadata and legal text are internally consistent.
- [ ] Functional smoke test passed on release candidate build.
- [ ] Deobfuscation file uploaded for the same `versionCode` before publishing when minification is enabled.
