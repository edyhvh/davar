
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

Web TS2009 translation loading uses these public env vars:

- `PUBLIC_SUPABASE_URL`
- `PUBLIC_SUPABASE_ANON_KEY`

Recommended workflow:

1. Keep `.env.example` committed as the template.
2. Set real local values in `.env` for local development.
3. Set real production values in Cloudflare Pages environment variables.

If Supabase values are missing, invalid, or placeholders, the app skips TS2009
loading and falls back to other translation sources.

### Build-time TS2009 Static Export (Cloudflare Pages)

The build pipeline can export TS2009 from Supabase Storage into static CDN files
at `public/data/ts2009/<book>/<chapter>.json`.

Required build-time secrets:

- `SUPABASE_URL` (or fallback to `PUBLIC_SUPABASE_URL`)
- `SUPABASE_SERVICE_ROLE_KEY`

Behavior:

1. During `bun run build`, `build.ts` executes `scripts/generate-static-data/index.ts`.
2. If both TS2009 build secrets are present, TS2009 chapter files are generated.
3. If secrets are missing, TS2009 static export is skipped and runtime fallback remains available.

Important:

- Never expose `SUPABASE_SERVICE_ROLE_KEY` as a `PUBLIC_*` variable.
- Keep service-role credentials only in Cloudflare Pages build secrets.

## Formatting

- This workspace uses Biome as the formatter/linter source of truth for JS/TS files.
- Use `bun run format` in this `web/` directory to format files.
- Prettier is intentionally not configured at project level in this workspace.
  
