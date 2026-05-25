
# Web App for Davar

This is the web application package for Davar.

## Running the code

Run `bun install` to install dependencies.

Run `bun run dev` for Bun HTML hot-reload mode without running `build.ts`.
It keeps the app on `http://localhost:3002`, checks static data, runs Bun HTML mode on an internal port, and serves `/data/*.json` through a local gateway.
The gateway listens on `0.0.0.0` by default so mobile devices on the same LAN can use `http://<your-machine-ip>:3002`.

Run `bun run dev:static` for production-parity local serving (builds `dist/` once, then serves it).

### Startup Logs

When using `bun run dev`, startup logs now show high-level milestone phases:

- `[davar-web] phase=data-generation start|done`
- `[davar-web] phase=bundle start|done`
- `[davar-web] phase=assets done`
- `[davar-web] phase=build done`

`[davar-static-data]` logs mark static-data generation start/end with total duration.

## Environment Setup

Web TS2009 translation loading is now served through the same-origin
`/api/ts2009/*` Pages Function backed by the private Cloudflare R2 bucket
`ts2009`.

Production builds also keep a bundled `/data/ts2009/*` fallback so English
verses can still render if the Pages Function binding is unavailable.

The web client no longer needs public Supabase credentials for TS2009.

### TS2009 Storage And Upload

Production flow:

1. Keep the source files in `data/ts2009/`.
2. Upload them to the private R2 bucket with `bun run upload:ts2009:r2` from `web/`.
	The uploader is resumable and skips files that were already uploaded.
3. Deploy the web app through the existing GitHub -> Cloudflare Pages flow.

At runtime:

- The browser requests `/api/ts2009/<book>.json` first.
- The Pages Function reads that object from the private `TS2009_BUCKET` binding.
- If that request fails, the client falls back to bundled `/data/ts2009/<book>.json` when present.
- In Cloudflare Pages, configure `TS2009_BUCKET` in both Preview and Production under Settings > Bindings, then redeploy after any binding change.

For local Bun development:

- `bun run dev` and `bun run serve` expose the same `/api/ts2009/*` path.
- Those local routes read directly from `data/ts2009/`.

## Formatting

- This workspace uses Biome as the formatter/linter source of truth for JS/TS files.
- Use `bun run format` in this `web/` directory to format files.
- Prettier is intentionally not configured at project level in this workspace.
  
