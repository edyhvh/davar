/**
 * Regression checks for #103: multi-word DSS variants must render as
 * span-aware replacements (replacing N Masoretic tokens) instead of
 * being hidden.
 */
import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = join(import.meta.dir, "..", "..", "..", "..");
const verseDisplaySrc = readFileSync(
	join(ROOT, "web/src/app/components/VerseDisplay.tsx"),
	"utf8",
);
const verseCardSrc = readFileSync(
	join(ROOT, "mobile/src/components/VerseCard.tsx"),
	"utf8",
);
const scriptureSrc = readFileSync(
	join(ROOT, "mobile/src/services/scripture.ts"),
	"utf8",
);

describe("DSS span-aware replacement (#103)", () => {
	test("web render path keeps skip-until span skipping", () => {
		expect(verseDisplaySrc).toContain("skipUntilIndex");
		expect(verseDisplaySrc).toContain("countMasoreticVariantSpan");
	});

	test("single-token guard removed from web and mobile render paths", () => {
		for (const [name, src] of [
			["VerseDisplay.tsx", verseDisplaySrc],
			["VerseCard.tsx", verseCardSrc],
			["scripture.ts", scriptureSrc],
		] as const) {
			expect(src.includes("tokenCount === 1"), name).toBe(false);
			expect(src.includes("countDssWordTokens(trimmed) === 1"), name).toBe(
				false,
			);
		}
	});

	test("mobile carries qumranSpan through DisplayWord", () => {
		expect(scriptureSrc).toContain("qumranSpan");
		expect(verseCardSrc).toContain("word.qumranSpan ?? 1");
	});
});
