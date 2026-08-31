# Dictionary Instance Handling Rules

Status: design specification for issue #94
Version: 1.0

This document defines deterministic handling for dictionary entries with many
attested instances. It is a contract for a later implementation; it does not
change generated data or runtime behavior by itself.

## 1. Volume tiers

The tier is based on the number of valid, deduplicated instances attached to an
entry after normalization.

| Tier | Count | First-pass surface set | Full-set policy |
| --- | ---: | ---: | --- |
| low | 0-99 | all instances | retain all |
| medium | 100-999 | all instances, grouped by book | retain all |
| high | 1,000+ | deterministic top 500 | retain all for background/export use |

The limits are product and implementation constants. A later implementation
must expose them in one configuration object and include the configuration
version in generated reports.

## 2. Normalization and deduplication

Before ranking, each instance is normalized without changing its source value:

1. Require a stable reference key (`book`, `chapter`, `verse`, and token/index
   when available).
2. Trim surrounding whitespace from display fields and normalize Unicode to
   NFC for comparison.
3. Preserve the original source payload for display and audit.
4. Collapse duplicate reference keys by retaining the record with the highest
   confidence; ties use the deterministic source key (lexicographic order).
5. Reject records with missing book/chapter/verse or invalid numeric ranges and
   report them as validation findings rather than silently dropping them.

## 3. Ranking and ordering

Ranking is stable and deterministic. Sort descending by the following tuple:

1. confidence score (missing confidence is `0`),
2. linguistic signal score,
3. canonical-source priority,
4. earliest canonical reference (`book_order`, chapter, verse, token/index),
5. stable instance identifier.

No filesystem order, insertion order, random value, or wall-clock value may
participate in ranking. Medium-tier presentation groups instances by canonical
book order, then applies the same ordering within each group. High-tier
presentation uses the first 500 ranked records and reports the omitted count.

## 4. Conflict resolution

When multiple rules produce different assignments for one instance:

1. Select the result with the highest confidence.
2. If tied, select the result with the strongest linguistic signal.
3. If still tied, prefer the result supported by more independent sources.
4. If still tied, choose the lexicographically smallest normalized candidate
   and mark the instance `needs_review`.

Every conflict must be retained in a machine-readable audit report with all
candidates and the reason the winner was selected.

## 5. Validation and quality gates

The validator must report, at minimum:

- duplicate reference keys before deduplication,
- missing or malformed location fields,
- invalid confidence values (outside 0-1),
- missing stable identifiers,
- conflicting assignments,
- repeated identical payloads at different references,
- high-tier entries whose surface set is not exactly 500 or the full count when
  fewer than 500 valid records exist.

A build fails on malformed locations, invalid confidence values, or unstable
ordering. Duplicates and conflicts are warnings only when they are fully
represented in the audit report; unresolved conflicts remain `needs_review`.

## 6. Performance safeguards

- Load high-tier entries in bounded batches rather than constructing repeated
  full-size intermediate lists.
- Keep the full set available to background/export consumers, while returning
  only the surface set to interactive clients.
- Do not change the public entry shape without a versioned migration. Add
  `instance_policy_version`, `instance_total`, and `instance_surface_count` to
  generated metadata.
- Add a regression benchmark for parsing, ranking, and serialization at 100,
  1,000, and 10,000 instances.

## 7. Canonical examples

- 42 instances: `low`; all 42 are shown in deterministic rank order.
- 400 instances across three books: `medium`; all are retained and grouped by
  canonical book order.
- 4,200 instances: `high`; all 4,200 remain available to export/background
  processing, while the interactive surface contains the top 500 and reports
  `instance_total=4200`, `instance_surface_count=500`.
- Two candidates with equal confidence and signal: choose the stable
  lexicographic fallback and mark the record for review.

## 8. Follow-up implementation plan

Implementation must be delivered in a separate issue/PR sequence:

1. Add the shared policy constants, normalization, ranking, and conflict model.
2. Add validator findings and deterministic JSON fixtures for each tier.
3. Integrate the policy into dictionary generation and static export.
4. Add client surface-set handling and verify memory/performance benchmarks.
5. Run web/mobile regression QA and compare generated output before publishing.

Each phase must preserve the full instance set and include a report diff before
any generated data is committed.
