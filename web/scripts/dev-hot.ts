import { fileURLToPath } from "node:url";

const webRoot = fileURLToPath(new URL("../", import.meta.url));
const appPort = Number(process.env.PORT ?? 3002);
const appHost = process.env.HOST ?? "0.0.0.0";
const htmlPort = Number(process.env.HOT_HTML_PORT ?? 3003);
const useGateway = process.env.HOT_USE_GATEWAY === "1";
const staticUrl = `http://localhost:${appPort}`;

console.log(
	`[davar-web] dev:hot app-host=${appHost} app-port=${appPort} html-port=${htmlPort} static-base=http://localhost:${appPort} gateway=${useGateway ? "on" : "off"}`,
);

const ensure = Bun.spawnSync(["bun", "./scripts/ensure-static-data.ts"], {
	cwd: webRoot,
	stdout: "inherit",
	stderr: "inherit",
});

if (ensure.exitCode !== 0) {
	process.exit(ensure.exitCode ?? 1);
}

const htmlServer = Bun.spawn(
	["bun", "--env-file=.env", "./index.html"],
	{
		cwd: webRoot,
		env: {
			...process.env,
			PORT: String(useGateway ? htmlPort : appPort),
			HOST: appHost,
			PUBLIC_STATIC_URL: staticUrl,
		},
		stdout: "inherit",
		stderr: "inherit",
	},
);

const gatewayServer = useGateway
	? Bun.spawn(["bun", "./scripts/dev-hot-gateway.ts"], {
			cwd: webRoot,
			env: {
				...process.env,
				PORT: String(appPort),
				HOST: appHost,
				HOT_HTML_PORT: String(htmlPort),
				HOT_HTML_HOST: "localhost",
			},
			stdout: "inherit",
			stderr: "inherit",
		})
	: null;

const shutdown = () => {
	if (!htmlServer.killed) {
		htmlServer.kill();
	}
	if (gatewayServer && !gatewayServer.killed) {
		gatewayServer.kill();
	}
};

process.on("SIGINT", () => {
	shutdown();
	process.exit(0);
});

process.on("SIGTERM", () => {
	shutdown();
	process.exit(0);
});

const htmlExitCode = await htmlServer.exited;
shutdown();
process.exit(htmlExitCode);
