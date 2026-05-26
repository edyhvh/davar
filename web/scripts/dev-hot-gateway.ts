import { join } from "node:path";

const gatewayPort = Number(process.env.PORT ?? 3002);
const gatewayHost = process.env.HOST ?? "0.0.0.0";
const htmlPort = Number(process.env.HOT_HTML_PORT ?? 3003);
const htmlHost = process.env.HOT_HTML_HOST ?? "localhost";
const dataRoot = join(import.meta.dir, "..", "public", "data");
const ts2009DataRoot = join(import.meta.dir, "..", "..", "data", "ts2009");

const getTs2009LocalFilePath = (pathname: string): string | null => {
	const relativePath = pathname.slice("/api/ts2009/".length);
	if (!relativePath || relativePath.includes("\0")) {
		return null;
	}

	const segments = relativePath.split("/").filter(Boolean);
	if (segments.length === 0 || segments.some((segment) => segment === "." || segment === "..")) {
		return null;
	}

	return join(ts2009DataRoot, ...segments);
};

Bun.serve({
	hostname: gatewayHost,
	port: gatewayPort,
	async fetch(req: Request) {
		const url = new URL(req.url);
		const pathname = decodeURIComponent(url.pathname);

		if (pathname.startsWith("/api/ts2009/")) {
			const localFilePath = getTs2009LocalFilePath(pathname);
			if (!localFilePath) {
				return new Response("Not Found", { status: 404 });
			}

			const file = Bun.file(localFilePath);
			if (!(await file.exists())) {
				return new Response("Not Found", { status: 404 });
			}

			return new Response(file, {
				headers: { "Content-Type": "application/json; charset=utf-8" },
			});
		}

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
