import { existsSync } from "node:fs";
import { join } from "node:path";

const webRoot = join(import.meta.dir, "..");
const publicDataDir = join(webRoot, "public", "data");
const metadataPath = join(publicDataDir, "metadata.json");

const requiredTs2009Files = [
	join(publicDataDir, "ts2009", "matthew", "1.json"),
	join(publicDataDir, "ts2009", "galatians", "1.json"),
	join(publicDataDir, "ts2009", "john1", "1.json"),
	join(publicDataDir, "ts2009", "jude", "1.json"),
	join(publicDataDir, "ts2009", "revelation", "1.json"),
];
const requiredHutterFiles = [
	join(publicDataDir, "hutter", "matthew", "1.json"),
	join(publicDataDir, "hutter", "revelation", "22.json"),
];

const hasRequiredTs2009Coverage = (): boolean =>
	requiredTs2009Files.every((path) => existsSync(path));
const hasRequiredHutterCoverage = (): boolean =>
	requiredHutterFiles.every((path) => existsSync(path));

if (
	existsSync(metadataPath) &&
	hasRequiredTs2009Coverage() &&
	hasRequiredHutterCoverage()
) {
	console.log("[davar-web] static-data=present skip-generation");
	process.exit(0);
}

if (!existsSync(metadataPath)) {
	console.log("[davar-web] static-data=missing generating");
} else {
	console.log("[davar-web] static-data=incomplete regenerating");
}

const generation = Bun.spawnSync(
	["bun", "../scripts/generate-static-data/index.ts"],
	{
		cwd: webRoot,
		stdout: "inherit",
		stderr: "inherit",
	},
);

if (generation.exitCode !== 0) {
	console.error("[davar-web] static-data=generate failed");
	process.exit(generation.exitCode ?? 1);
}

console.log("[davar-web] static-data=ready");
