import tailwind from "bun-plugin-tailwind";
import { join } from "path";
import { cpSync, existsSync, readFileSync, writeFileSync } from "fs";

const result = await Bun.build({
  entrypoints: ["./index.html"],
  outdir: "./dist",
  publicPath: "/",
  minify: true,
  env: "PUBLIC_*",
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
