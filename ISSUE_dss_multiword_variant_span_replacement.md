# Title
Implement correct multi-word DSS span replacement (remove temporary hide-only behavior)

## Summary
Multi-word DSS variants are currently not rendered because they can produce duplicated text when applied as a single-word replacement. We need a proper span-aware replacement algorithm so DSS variants with two or more tokens replace the corresponding Masoretic token range safely and consistently across web and mobile.

## Scope / What to do
- Define a span-aware DSS rendering model that maps one DSS variant to N Masoretic tokens.
- Replace index-only substitution with start-position + span logic in all render paths.
- Ensure click/selection behavior still resolves to the correct source word and analysis payload.
- Preserve existing behavior for single-word DSS variants.
- Remove the temporary guard that hides DSS variants when token_count > 1 once span replacement is verified.
- Add regression checks for known multi-word examples from DSS data.

## Current Problem / Root Cause (if applicable)
- DSS variants are attached to a single position, but some entries represent phrases (2+ tokens).
- Current rendering inserts the DSS phrase at one position while remaining Masoretic words may still render, causing visible duplication/misalignment.
- Temporary mitigation now hides multi-word DSS variants to prevent incorrect UI output; data is still present.
- Root cause: no unified span computation from dss_word and masoretic_word token structure at render time.

## Examples
Wrong (historical behavior before temporary hide):
```text
Masoretic tokens: [A][B][C][D]
DSS variant at position B: "X Y"
Rendered: [A][X Y][C][D]   (C may be duplicate residual if B+C should be replaced)
```

Current temporary behavior (safe but incomplete):
```text
DSS variant token_count > 1
Rendered: Masoretic only (DSS hidden)
```

Expected behavior:
```text
Masoretic tokens: [A][B][C][D]
DSS variant at position B, span=2: "X Y"
Rendered: [A][X Y][D]
```

Concrete dataset examples to validate:
```hebrew
web/data/dss/1samuel.json 1:22 pos 15
DSS: יָקִים יְהוָה אֵת אֲשֶׁר־יָצָא מִפִּיךְ
```

```hebrew
web/data/dss/isaiah.json 4:5 pos 12
DSS: ועשן ונגה אש להבה לילה כי על כל כבוד חפה
```

```hebrew
web/data/dss/isaiah.json 60:20 pos 1
DSS: לוא יבוא שמשך וירחך לוא יאסף כיא יהוה יהיה לך לאור עולם
```

## Impact
- Affected: users who enable DSS/Qumran view on verses containing phrase-level variants.
- Current severity: medium-high UX/data fidelity issue.
- Without fix: DSS coverage is reduced because multi-word variants are hidden.
- With incorrect fix: learning accuracy and textual trust can degrade due to duplicated/incorrect mixed text.

## Proposed Solution / Recommended Fix
- Preferred approach (automated, unified):
1. Introduce a shared span calculator that derives replacement span from variant metadata (prefer masoretic_word tokenization, fallback to dss metadata heuristics).
2. Apply this span model in all renderers (verse view, full chapter, mobile mapping) to skip replaced Masoretic tokens deterministically.
3. Keep source token identity for interactions (selection, Strong lookup, word cards) by anchoring on the original start position.
4. Add snapshot/regression tests using known multi-word cases.
5. Remove temporary multi-word hide guard after verification.
- Alternative approach:
1. Precompute spans during static data generation and store explicit span in DSS payload.
2. Renderers consume precomputed span directly.
- Manual review-only approach is not recommended due to dataset scale and cross-platform behavior drift risk.

## Files / Locations Involved
- web/src/app/components/VerseDisplay.tsx
- web/src/app/components/FullChapterView.tsx
- web/src/app/App.tsx
- mobile/src/services/scripture.ts
- web/src/app/services/staticData.ts
- shared/translationConfig.ts (only if shared normalization logic is centralized)
- web/data/dss/*.json (validation fixtures, no destructive edits required)
- debug/output/dss_changed_words_multiword_only_v2.txt (verification sample set)

## Acceptance Criteria / How to know it's fixed
- Multi-word DSS variants render correctly as span replacements (no duplicated residual Masoretic tokens).
- Single-word DSS variants remain unchanged.
- Behavior is consistent in:
  - web verse view
  - web full chapter view
  - mobile verse rendering
- Word selection and analysis still work for replaced spans without incorrect Strong mappings.
- Temporary "hide if token_count > 1" guard is removed.
- Regression checks pass for representative multi-word examples (including long phrase cases).

## Related Issues / Context
- Discovered while fixing DSS visibility/commentary wiring and investigating duplicated phrase rendering.
- Temporary mitigation was introduced: hide multi-word DSS variants instead of rendering potentially incorrect output.
- Validation artifacts already generated in debug/output for recovered and multi-word entries.

## Status (only if relevant)
New
