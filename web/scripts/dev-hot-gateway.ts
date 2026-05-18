import { join } from "node:path";

const gatewayPort = Number(process.env.PORT ?? 3002);
const gatewayHost = process.env.HOST ?? "0.0.0.0";
const htmlPort = Number(process.env.HOT_HTML_PORT ?? 3003);
const htmlHost = process.env.HOT_HTML_HOST ?? "localhost";
const dataRoot = join(import.meta.dir, "..", "public", "data");

Bun.serve({
	hostname: gatewayHost,
	port: gatewayPort,
	async fetch(req: Request) {
		const url = new URL(req.url);
		const pathname = decodeURIComponent(url.pathname);

		if (pathname.startsWith("/data/")) {
			const relativePath = pathname.slice("/data/".length);
			if (!relativePath || relativePath.includes("..")) {
				return new Response("Not Found", { status: 404 });
			}

			const file = Bun.file(join(dataRoot, relativePath));
			if (!(await file.exists())) {
				return new Response("Not Found", { status: 404 });
			}

			return new Response(file);
		}

		const upstream = new URL(
			url.pathname + url.search,
			`http://${htmlHost}:${htmlPort}`,
		);
		const proxiedRequest = new Request(upstream, req);
		return fetch(proxiedRequest);
	},
});

console.log(
	`[davar-web] dev-hot-gateway listening on http://${gatewayHost}:${gatewayPort} (html upstream http://${htmlHost}:${htmlPort})`,
);
