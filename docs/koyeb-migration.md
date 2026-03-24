# Koyeb Migration Runbook

## Goal
Migrate backend hosting from Render to Koyeb with minimal downtime and a reversible cutover.

## Hosting Ownership
- Frontend production deployments: Cloudflare Pages Git integration.
- Backend production deployments: Koyeb Git auto-deploy.

## Prerequisites
1. Koyeb account and GitHub integration installed.
2. Existing backend secrets available from current production host.
3. Cloudflare Pages project already serving frontend.

## Service Setup (Koyeb)
1. Create a Koyeb Web Service from this repository.
2. Select builder: `Buildpack`.
3. Set work directory: `backend`.
4. Set run command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Set tracked branch to `koyeb` for validation.
6. Configure HTTP health check path: `/health`.
7. Add required environment variables:
   - `DAVAR_API_KEY`
   - `DAVAR_ALLOWED_ORIGINS`
   - `DAVAR_RATE_LIMIT`
   - `DAVAR_ENV=production`
   - `DAVAR_DATA_PATH=../data`
   - `DAVAR_SUPABASE_URL`
   - `DAVAR_SUPABASE_SERVICE_KEY`
   - `DAVAR_TS2009_SYNC_ON_STARTUP=true`

## Cutover Sequence
1. Deploy and validate backend on Koyeb tracked branch `koyeb`.
2. Set Cloudflare Pages variable:

```bash
BACKEND_API_ORIGIN=https://api.davar.bible
```

3. Redeploy Pages.
4. Verify production traffic is healthy through `/api/*` proxy.
5. Switch Koyeb tracked branch from `koyeb` to `main`.
6. Keep old provider alive during observation window.

## Verification
1. `GET /health` returns `status: healthy`.
2. Authenticated `GET /api/v1/books` succeeds.
3. Representative verses (Tanaj + Besorah + TS2009-backed responses) succeed.
4. Koyeb logs show normal startup and TS2009 background sync.

## Rollback
1. Revert Cloudflare `BACKEND_API_ORIGIN` to previous backend host.
2. Redeploy Pages.
3. Investigate Koyeb deployment logs and health checks before reattempting cutover.
