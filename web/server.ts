const port = Number(process.env.PORT ?? 3002);
const hostname = process.env.HOST ?? "0.0.0.0";
const distDir = new URL("./dist/", import.meta.url);

Bun.serve({
	hostname,
	port,
	async fetch(req: Request) {
		const url = new URL(req.url);
		const pathname = decodeURIComponent(url.pathname);

		if (pathname.startsWith("/data/")) {
			const assetPath = pathname.startsWith("/") ? pathname.slice(1) : pathname;
			const file = Bun.file(new URL(assetPath, distDir));
			if (await file.exists()) {
				return new Response(file);
			}
			return new Response("Not Found", { status: 404 });
		}

		if (pathname !== "/" && pathname.includes(".")) {
			const assetPath = pathname.startsWith("/") ? pathname.slice(1) : pathname;
			const file = Bun.file(new URL(assetPath, distDir));
			if (await file.exists()) {
				return new Response(file);
			}
			return new Response("Not Found", { status: 404 });
		}

		const htmlFile = Bun.file(new URL("index.html", distDir));
		return new Response(htmlFile, {
			headers: { "Content-Type": "text/html; charset=utf-8" },
		});
	},
});

console.log(`[davar-web] server listening on http://${hostname}:${port}`);
