/**
 * Regression check for #107: shared settings order must match
 * shared/settingsOrder.ts on both platforms.
 */
import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = join(import.meta.dir, "..", "..", "..", "..");

const SHARED_ORDER = [
	"theme",
	"language",
	"besorahTextVersion",
	"fullChapter",
	"seferStyle",
	"hebrewOnly",
	"qumran",
];

// Extract settings.* i18n keys in render order from a source file.
function extractOrder(path: string): string[] {
	const src = readFileSync(join(ROOT, path), "utf8");
	const ids: string[] = [];
	for (const m of src.matchAll(
		/t\("settings\.(theme|language|besorahTextVersion|fullChapter|seferStyle|hebrewOnly|qumran)\.title"\)/g,
	)) {
		if (ids[ids.length - 1] !== m[1]) ids.push(m[1]);
	}
	return ids;
}

test("mobile settings order matches canonical shared order", () => {
	expect(extractOrder("mobile/app/(tabs)/settings.tsx")).toEqual(SHARED_ORDER);
});

test("web settings order matches canonical shared order", () => {
	expect(extractOrder("web/src/app/components/SettingsScreen.tsx")).toEqual(
		SHARED_ORDER,
	);
});

test("shared/settingsOrder.ts manifest matches the enforced order", () => {
	const src = readFileSync(join(ROOT, "shared", "settingsOrder.ts"), "utf8");
	const inManifest = [
		...src.matchAll(/"([a-zA-Z]+)"/g),
	]
		.map((m) => m[1])
		.filter((v) => SHARED_ORDER.includes(v as never));
	expect([...new Set(inManifest)]).toEqual(SHARED_ORDER);
});
