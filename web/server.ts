import { join } from "path";
import app from "./dist/index.html";

const port = Number(process.env.PORT ?? 3002);
const distDir = join(import.meta.dir, "dist");

Bun.serve({
  port,
  async fetch(req) {
    const url = new URL(req.url);
    const pathname = decodeURIComponent(url.pathname);

    if (pathname !== "/" && pathname.includes(".")) {
      const assetPath = pathname.startsWith("/") ? pathname.slice(1) : pathname;
      const file = Bun.file(join(distDir, assetPath));
      if (await file.exists()) {
        return new Response(file);
      }
      return new Response("Not Found", { status: 404 });
    }

    return app;
  },
});

console.log(`[davar-web] server listening on http://localhost:${port}`);
