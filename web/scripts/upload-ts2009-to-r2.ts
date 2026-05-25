import {
	mkdir,
	readFile,
	readdir,
	stat,
	writeFile,
} from "node:fs/promises";
import { join } from "node:path";

type RuntimeProcess = {
	env: Record<string, string | undefined>;
	exit: (exitCode: number) => never;
};

const runtimeProcess = process as unknown as RuntimeProcess;
const runtimeExit = (code: number): never => runtimeProcess.exit(code);
const textDecoder = new TextDecoder();

const bucketName = "ts2009";
const webRoot = join(import.meta.dir, "..");
const repoRoot = join(webRoot, "..");
const ts2009Root = join(webRoot, "..", "data", "ts2009");
const uploadStatePath = join(webRoot, "tmp", "ts2009-r2-upload-state.json");

type UploadStateEntry = {
	size: number;
	mtimeMs: number;
	uploadedAt: string;
};

type UploadState = {
	uploaded: Record<string, UploadStateEntry>;
};

type WranglerCommandResult = {
	exitCode: number;
	stdout: string;
	stderr: string;
	combinedOutput: string;
};

const decodeOutput = (output: Uint8Array<ArrayBufferLike> | null | undefined) =>
	output ? textDecoder.decode(output).trim() : "";

const printCommandOutput = (result: WranglerCommandResult): void => {
	if (result.stdout) {
		console.log(result.stdout);
	}
	if (result.stderr) {
		console.error(result.stderr);
	}
};

const isAuthenticationMessage = (message: string): boolean => {
	const normalized = message.toLowerCase();
	return (
		normalized.includes("authentication error") ||
		normalized.includes("unauthorized") ||
		normalized.includes("code\":10000")
	);
};

const runWranglerCommand = (
	args: string[],
	options?: { retryLabel?: string; printOutput?: boolean },
): WranglerCommandResult => {
	for (let attempt = 1; attempt <= 2; attempt += 1) {
		const command = Bun.spawnSync(["bunx", "wrangler", ...args], {
			cwd: repoRoot,
			stdout: "pipe",
			stderr: "pipe",
		});
		const result: WranglerCommandResult = {
			exitCode: command.exitCode ?? 1,
			stdout: decodeOutput(command.stdout),
			stderr: decodeOutput(command.stderr),
			combinedOutput: [
				decodeOutput(command.stdout),
				decodeOutput(command.stderr),
			]
				.filter(Boolean)
				.join("\n"),
		};

		if (result.exitCode === 0) {
			if (options?.printOutput) {
				printCommandOutput(result);
			}
			return result;
		}

		if (
			attempt === 1 &&
			isAuthenticationMessage(result.combinedOutput)
		) {
			console.warn(
				`[ts2009-upload] Wrangler authentication expired while ${options?.retryLabel ?? "running command"}; retrying once.`,
			);
			continue;
		}

		if (options?.printOutput ?? true) {
			printCommandOutput(result);
		}
		return result;
	}

	return {
		exitCode: 1,
		stdout: "",
		stderr: "",
		combinedOutput: "",
	};
};

const readUploadState = async (): Promise<UploadState> => {
	try {
		const raw = await readFile(uploadStatePath, "utf-8");
		const parsed = JSON.parse(raw) as Partial<UploadState>;
		return {
			uploaded:
				typeof parsed.uploaded === "object" && parsed.uploaded !== null
					? parsed.uploaded
					: {},
		};
	} catch {
		return { uploaded: {} };
	}
};

const writeUploadState = async (state: UploadState): Promise<void> => {
	await mkdir(join(webRoot, "tmp"), { recursive: true });
	await writeFile(uploadStatePath, JSON.stringify(state, null, 2), "utf-8");
};

const isSameLocalFileVersion = (
	entry: UploadStateEntry | undefined,
	fileStats: { size: number; mtimeMs: number },
): boolean =>
	Boolean(
		entry &&
		entry.size === fileStats.size &&
		entry.mtimeMs === fileStats.mtimeMs,
	);

const isRemoteNotFoundMessage = (message: string): boolean => {
	const normalized = message.toLowerCase();
	return (
		normalized.includes("not found") ||
		normalized.includes("404") ||
		normalized.includes("does not exist") ||
		normalized.includes("nosuchkey") ||
		normalized.includes("specified key")
	);
};

const remoteObjectExists = (objectPath: string): boolean => {
	const check = runWranglerCommand(
		["r2", "object", "get", objectPath, "--pipe", "--remote"],
		{ retryLabel: `checking ${objectPath}`, printOutput: false },
	);

	if (check.exitCode === 0) {
		return true;
	}

	const message = check.combinedOutput;

	if (isRemoteNotFoundMessage(message)) {
		return false;
	}

	console.error(message || `[ts2009-upload] failed to inspect ${objectPath}`);
	runtimeExit(check.exitCode ?? 1);
	return false;
};

const files = (await readdir(ts2009Root, { withFileTypes: true }))
	.filter((entry) => entry.isFile() && entry.name.endsWith(".json"))
	.map((entry) => entry.name)
	.sort((a, b) => a.localeCompare(b, "en"));

if (files.length === 0) {
	throw new Error(`No TS2009 JSON files found in ${ts2009Root}`);
}

const uploadState = await readUploadState();
let uploadedCount = 0;
let skippedCount = 0;

for (const fileName of files) {
	const sourcePath = join(ts2009Root, fileName);
	const objectPath = `${bucketName}/${fileName}`;
	const fileStats = await stat(sourcePath);
	const currentFileVersion = {
		size: fileStats.size,
		mtimeMs: fileStats.mtimeMs,
	};
	const previousEntry = uploadState.uploaded[fileName];

	if (isSameLocalFileVersion(previousEntry, currentFileVersion)) {
		skippedCount += 1;
		console.log(`[ts2009-upload] skipping ${fileName} (already uploaded)`);
		continue;
	}

	if (!previousEntry && remoteObjectExists(objectPath)) {
		uploadState.uploaded[fileName] = {
			...currentFileVersion,
			uploadedAt: new Date().toISOString(),
		};
		await writeUploadState(uploadState);
		skippedCount += 1;
		console.log(
			`[ts2009-upload] skipping ${fileName} (already present in R2)`,
		);
		continue;
	}

	console.log(`[ts2009-upload] uploading ${fileName}`);
	const upload = runWranglerCommand(
		[
			"r2",
			"object",
			"put",
			objectPath,
			"--file",
			sourcePath,
			"--content-type",
			"application/json",
			"--remote",
		],
		{ retryLabel: `uploading ${fileName}`, printOutput: true },
	);

	if (upload.exitCode !== 0) {
		runtimeExit(upload.exitCode ?? 1);
	}

	uploadState.uploaded[fileName] = {
		...currentFileVersion,
		uploadedAt: new Date().toISOString(),
	};
	await writeUploadState(uploadState);
	uploadedCount += 1;
}

console.log(
	`[ts2009-upload] done uploaded=${uploadedCount} skipped=${skippedCount} bucket=${bucketName}`,
);