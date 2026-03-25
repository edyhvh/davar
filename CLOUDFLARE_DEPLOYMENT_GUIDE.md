# Cloudflare Pages Deployment Guide

This guide explains how to deploy the Davar web frontend to Cloudflare Pages on the free tier.

## ✅ Updated Architecture (Post-Migration)

**Status:** Backend eliminated. Now a pure static site with:
- Static JSON data served from Cloudflare Pages
- TS2009 licensed content from Supabase Storage
- No backend server required

### New Flow:
1. Browser loads frontend from Cloudflare Pages
2. Frontend fetches static JSON data from same origin (`/data/`)
3. TS2009 requests go to Supabase Storage
4. Everything served via Cloudflare's global CDN

### Benefits:
- **Zero cold starts** - no server to wake up
- **Global CDN** - instant worldwide loading
- **Free tier** - unlimited bandwidth for static content
- **No API proxy** - direct static file serving

---

## 1. Cloudflare Navigation

Cloudflare has two relevant areas:

- **Workers & Pages**: deployment, build config, environment variables, custom domain for Pages project
- **Zone Dashboard**: domain-level DNS and security controls

---

## 2. Create the Pages Project

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Open **Workers & Pages**
3. Click **Create application**
4. Choose **Pages** and **Connect to Git**
5. Select this repository
6. Configure build:
   - Project name: `davar-web`
   - Production branch: `main`
   - Root directory: `web`
   - Build command: `bun run build`
   - Build output directory: `dist`
7. Save and deploy

---

## 3. Configure Pages Environment Variables

In your Pages project settings, add production environment variables:

```bash
PUBLIC_SUPABASE_URL=https://your-project.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
PUBLIC_NODE_ENV=production
```

Notes:
- Supabase credentials are required for TS2009 access
- These values are applied at build time
- No backend API configuration needed

---

## 4. Add Custom Domain

1. In Pages project, open **Custom domains**
2. Add your domain (example: `davar.bible`)
3. Complete DNS prompts until status is active

---

## 5. Data Serving

Static data is automatically served from `/data/` paths on your domain. No additional configuration needed.

**Example URLs:**
- `https://davar.bible/data/metadata.json`
- `https://davar.bible/data/oe/genesis/1.json`
- `https://davar.bible/data/tth/genesis.json`

- Proxies `/api/*` requests to `BACKEND_API_ORIGIN`
- Caches selected GET/HEAD endpoints at the edge
- Adds `X-Davar-Edge-Cache: HIT|MISS` for observability

---

## 7. Update Backend CORS in Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Open backend service `davar`
3. Go to **Environment**
4. Update `DAVAR_ALLOWED_ORIGINS`
5. Use exact origins only

Example:

```bash
DAVAR_ALLOWED_ORIGINS=["http://localhost:3002","http://localhost:3003","http://localhost:8082","https://app.yourdomain.com"]
```

Then redeploy backend.

Because frontend is now same-origin to Pages, Render only needs to allow the Pages/Custom-domain origin and local dev origins.

---

## 8. Security Settings (Free Tier)

In Zone dashboard:

1. **SSL/TLS** -> **Overview** -> set mode to `Full (strict)`
2. **Security** -> **Bots** -> enable **Bot Fight Mode**
3. **Security** -> **WAF** -> optionally add managed/custom rules
4. **Security** -> **Settings** (or **Rate Limiting**) -> create one API rule

Suggested API limit baseline:

- Path: `/api/*`
- Threshold: `10 requests / 10 seconds` per client

Tune this after observing real traffic.

---

## 9. Build and Verification

### Local build check

```bash
cd web
bun --env-file=.env.production run build
```

### Optional local Pages preview

```bash
cd web
bunx wrangler pages dev dist
```

### Deployment verification checklist

1. Pages deployment is healthy in **Workers & Pages**
2. Custom domain is active and serving frontend
3. Browser API calls go to `/api/...` on your Pages domain
4. API responses are `200`
5. No CORS errors in browser console
6. No CSP connect-src errors in browser console
7. Direct navigation to deep routes still loads app (SPA fallback)
8. Response headers include `X-Davar-Edge-Cache` for cacheable reads

---

## 10. Files Already Present in This Repo

- [web/.env.production](web/.env.production)
- [web/wrangler.toml](web/wrangler.toml)
- [web/public/\_redirects](web/public/_redirects)
- [plans/cloudflare-deployment-plan.md](plans/cloudflare-deployment-plan.md)

---

## 11. Troubleshooting

### CORS blocked

1. Confirm exact frontend origin exists in `DAVAR_ALLOWED_ORIGINS`
2. Confirm backend was redeployed after env change
3. Confirm browser is using expected domain (not preview URL)

### API calls bypass proxy

1. Confirm `PUBLIC_API_BASE_URL=/api` in Pages environment variables
2. Confirm Pages Function exists at `web/functions/api/[[path]].ts`
3. Rebuild/redeploy Pages after env changes

### API calls fail or go to wrong host

1. Confirm `PUBLIC_API_BASE_URL=/api` in Pages environment variables
2. Confirm `BACKEND_API_ORIGIN=https://davar.onrender.com` in Pages environment variables
3. Rebuild/redeploy Pages after variable changes
4. Check network tab request URL host

### Build fails

1. Confirm dependencies are installed with Bun in `web`
2. Re-run build locally with:

```bash
cd web
bun install
bun run build
```

---

## 12. Support Path

If deployment fails:

1. Check **Workers & Pages** deployment logs first
2. Check Zone-level security/rule events in Cloudflare
3. Check Render service logs

---

## 13. Preview Lifecycle and Deployment Statuses

Cloudflare preview deployments are expected for pull requests that modify web files.

Normal lifecycle events:

1. PR opened or updated: a new preview deployment is created.
2. New commit pushed to same PR: previous preview can be superseded and shown as inactive.
3. PR merged or closed: preview deployment can be removed or marked destroyed.

Important interpretation:

- A preview marked destroyed after merge/close is usually expected cleanup, not a production failure.
- Production health should be validated on the `main` deployment and custom domain, not on expired preview URLs.

Canonical ownership for this repository:

1. Cloudflare Pages is the only frontend deployment owner.
2. Render is the backend deployment owner.
3. Vercel deployment integration should remain disabled to avoid duplicate preview and production statuses.
