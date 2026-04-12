import { cpSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import tailwind from "bun-plugin-tailwind";

const formatSeconds = (startedAtMs: number): string => {
	return `${((Date.now() - startedAtMs) / 1000).toFixed(1)}s`;
};

const buildStartedAt = Date.now();
console.log("[davar-web] phase=data-generation start");
const dataGenerationStartedAt = Date.now();

const generation = Bun.spawnSync(
	["bun", "../scripts/generate-static-data/index.ts"],
	{
		cwd: import.meta.dir,
		stdout: "inherit",
		stderr: "inherit",
	},
);

if (generation.exitCode === 0) {
	console.log(
		`[davar-web] phase=data-generation done duration=${formatSeconds(dataGenerationStartedAt)}`,
	);
}

if (generation.exitCode !== 0) {
	console.error(
		`[davar-web] phase=data-generation failed duration=${formatSeconds(dataGenerationStartedAt)}`,
	);
	process.exit(generation.exitCode ?? 1);
}

console.log("[davar-web] phase=bundle start");
const bundleStartedAt = Date.now();

const result = await Bun.build({
	entrypoints: ["./index.html"],
	outdir: "./dist",
	publicPath: "/",
	minify: true,
	env: "PUBLIC_*",
	// Belt-and-suspenders: force literal substitution of PUBLIC_* env vars so
	// that import.meta.env.PUBLIC_X is guaranteed to be inlined even in Bun
	// versions that only replace direct AST-node patterns.
	define: {
		"import.meta.env.PUBLIC_SUPABASE_URL": JSON.stringify(
			process.env.PUBLIC_SUPABASE_URL ?? "",
		),
		"import.meta.env.PUBLIC_SUPABASE_ANON_KEY": JSON.stringify(
			process.env.PUBLIC_SUPABASE_ANON_KEY ?? "",
		),
		"import.meta.env.PUBLIC_NODE_ENV": JSON.stringify(
			process.env.PUBLIC_NODE_ENV ?? "production",
		),
		"import.meta.env.PUBLIC_STATIC_URL": JSON.stringify(
			process.env.PUBLIC_STATIC_URL ?? "",
		),
	},
	plugins: [tailwind],
});

if (!result.success) {
	console.error(
		`[davar-web] phase=bundle failed duration=${formatSeconds(bundleStartedAt)}`,
	);
	for (const log of result.logs) {
		console.error(log);
	}
	process.exit(1);
}

console.log(
	`[davar-web] phase=bundle done duration=${formatSeconds(bundleStartedAt)} outputs=${result.outputs.length}`,
);

// Copy public assets that aren't referenced in HTML/CSS (og-image, etc.)
const publicDir = join(import.meta.dir, "public");
const distDir = join(import.meta.dir, "dist");

if (existsSync(publicDir)) {
	cpSync(publicDir, distDir, { recursive: true, force: true });
}

console.log("[davar-web] phase=assets done");

// Ensure deep-route reloads request bundled assets from root (e.g. /chunk-*.js)
// instead of route-relative paths (e.g. /verse/.../chunk-*.js).
const distIndexPath = join(distDir, "index.html");
if (existsSync(distIndexPath)) {
	const html = readFileSync(distIndexPath, "utf-8");
	const normalizedHtml = html.replace(/(href|src)="\.\/([^"]+)"/g, '$1="/$2"');

	if (normalizedHtml !== html) {
		writeFileSync(distIndexPath, normalizedHtml, "utf-8");
	}
}

console.log(
	`[davar-web] phase=build done duration=${formatSeconds(buildStartedAt)} files=${result.outputs.length}`,
);
