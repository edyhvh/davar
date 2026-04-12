declare const process: {
	env: Record<string, string | undefined>;
};

interface ImportMetaEnv {
	readonly PUBLIC_NODE_ENV?: string;
	[key: string]: string | undefined;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}

declare module "*.css";
declare module "*.png";
