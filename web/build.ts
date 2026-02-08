import tailwind from "bun-plugin-tailwind";
import { join } from "path";
import { cpSync, existsSync } from "fs";

const result = await Bun.build({
  entrypoints: ["./index.html"],
  outdir: "./dist",
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

console.log(`Build complete: ${result.outputs.length} files written to ./dist`);
