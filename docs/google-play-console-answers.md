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
