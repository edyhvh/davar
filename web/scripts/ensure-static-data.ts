import { existsSync } from "node:fs";
import { join } from "node:path";

const webRoot = join(import.meta.dir, "..");
const publicDataDir = join(webRoot, "public", "data");
const metadataPath = join(publicDataDir, "metadata.json");

if (existsSync(metadataPath)) {
	console.log("[davar-web] static-data=present skip-generation");
	process.exit(0);
}

console.log("[davar-web] static-data=missing generating");

const generation = Bun.spawnSync(["bun", "../scripts/generate-static-data/index.ts"], {
	cwd: webRoot,
	stdout: "inherit",
	stderr: "inherit",
});

if (generation.exitCode !== 0) {
	console.error("[davar-web] static-data=generate failed");
	process.exit(generation.exitCode ?? 1);
}

console.log("[davar-web] static-data=ready");
