import tailwind from "bun-plugin-tailwind";
import { join } from "path";
import { cpSync, existsSync, readFileSync, writeFileSync } from "fs";

const generation = Bun.spawnSync(
	["bun", "../scripts/generate-static-data/index.ts"],
	{
		cwd: import.meta.dir,
		stdout: "inherit",
		stderr: "inherit",
	},
);

if (generation.exitCode !== 0) {
	console.error("Static data generation failed.");
	process.exit(generation.exitCode ?? 1);
}

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
	for (const log of result.logs) {
		console.error(log);
	}
	process.exit(1);
}

// Copy public assets that aren't referenced in HTML/CSS (og-image, etc.)
const publicDir = join(import.meta.dir, "public");
const distDir = join(import.meta.dir, "dist");

if (existsSync(publicDir)) {
	cpSync(publicDir, distDir, { recursive: true, force: true });
}

// Ensure deep-route reloads request bundled assets from root (e.g. /chunk-*.js)
// instead of route-relative paths (e.g. /verse/.../chunk-*.js).
const distIndexPath = join(distDir, "index.html");
if (existsSync(distIndexPath)) {
	const html = readFileSync(distIndexPath, "utf-8");
	const normalizedHtml = html.replace(/(href|src)="\.\/([^\"]+)"/g, '$1="/$2"');

	if (normalizedHtml !== html) {
		writeFileSync(distIndexPath, normalizedHtml, "utf-8");
	}
}

console.log(`Build complete: ${result.outputs.length} files written to ./dist`);
