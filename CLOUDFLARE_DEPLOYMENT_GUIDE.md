# Cloudflare Deployment Guide

This guide explains how to deploy the Davar web frontend to Cloudflare Pages on the free tier, using:

- Custom domain from day one
- Cloudflare proxy for `/api/*`
- Render as backend origin

---

## 1. Architecture You Are Deploying

Flow:

1. Browser loads frontend from your custom domain on Cloudflare Pages
2. Frontend requests same-origin API paths such as `/api/v1/books`
3. Cloudflare forwards `/api/*` to `https://davar.onrender.com/api/*`
4. Render responds, Cloudflare returns response to browser

Why this is simpler:

- Browser talks to one origin (your domain)
- Less direct CORS pain for frontend requests
- You can apply edge protection in Cloudflare before traffic reaches Render

Free tier support:

- Cloudflare Pages hosting: yes
- Custom domain: yes
- SSL: yes
- Bot Fight Mode: yes
- Basic rate limiting: yes

---

## 2. Cloudflare Navigation (Important)

Cloudflare has two relevant areas:

- **Workers & Pages**: deployment, build config, environment variables, custom domain for Pages project
- **Zone Dashboard** (the menu with DNS, SSL/TLS, Security, Rules): domain-level DNS and security controls

If you only see DNS/SSL/Security, you are in the Zone dashboard, not the Pages deployment view.

---

## 3. Create the Pages Project

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

## 4. Configure Pages Environment Variables

In your Pages project settings, add production environment variables:

```bash
PUBLIC_API_BASE_URL=/api
PUBLIC_API_KEY=your_api_key_value
PUBLIC_NODE_ENV=production
```

Notes:

- `PUBLIC_API_BASE_URL=/api` makes frontend requests same-origin and proxy-friendly.
- Keep API key value aligned with backend expected key.
- These values are applied at build time.

---

## 5. Add Custom Domain (Now)

1. In Pages project, open **Custom domains**
2. Add your domain (example: `app.yourdomain.com`)
3. Complete DNS prompts until status is active

Once active, use this exact HTTPS origin in backend CORS.

---

## 6. Configure API Proxy in Cloudflare

Goal: forward frontend `/api/*` traffic to Render backend.

Recommended rule behavior:

- Incoming: `https://your-domain.com/api/*`
- Forward to: `https://davar.onrender.com/api/*`
- Preserve method, query string, and body

Where to configure:

- Use Cloudflare Rules or Worker-based routing, depending on your dashboard options.
- Keep the result equivalent to the mapping above.

### Recommended for this project: GitHub-managed Worker

If you prefer GitHub, connect your repository when Cloudflare prompts for it and deploy a dedicated Worker from source control.

Suggested Worker script:

```ts
export default {
   async fetch(request: Request): Promise<Response> {
      const url = new URL(request.url);

      // Keep path and query string and forward to Render.
      const upstream = new URL(url.pathname + url.search, "https://davar.onrender.com");

      const response = await fetch(upstream.toString(), {
         method: request.method,
         headers: request.headers,
         body: request.body,
         redirect: "follow",
      });

      return response;
   },
};
```

GitHub deployment sequence:

1. In Cloudflare, create a new Worker and choose GitHub as source.
2. Select this repository and the branch you deploy from.
3. Add the Worker code in the selected Worker directory.
4. Deploy Worker from Cloudflare.
5. Go to **Workers Routes** and add route pattern `your-domain.com/api/*` mapped to this Worker.

After setup, browser network requests should target your custom domain `/api/...`, not Render directly.

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
3. Browser API calls go to `https://your-domain.com/api/...`
4. Proxy forwards successfully and responses are `200`
5. No CORS errors in browser console
6. No CSP connect-src errors in browser console
7. Direct navigation to deep routes still loads app (SPA fallback)

---

## 10. Files Already Present in This Repo

- [web/.env.production](web/.env.production)
- [web/wrangler.toml](web/wrangler.toml)
- [web/public/_redirects](web/public/_redirects)
- [plans/cloudflare-deployment-plan.md](plans/cloudflare-deployment-plan.md)

---

## 11. Troubleshooting

### CORS blocked

1. Confirm exact frontend origin exists in `DAVAR_ALLOWED_ORIGINS`
2. Confirm backend was redeployed after env change
3. Confirm browser is using expected domain (not preview URL)

### API calls bypass proxy

1. Confirm `PUBLIC_API_BASE_URL=/api` in Pages environment variables
2. Rebuild/redeploy Pages after variable changes
3. Check network tab request URL host

### Proxy returns error

1. Test backend origin directly: `https://davar.onrender.com/api/v1/books`
2. Check Cloudflare rule target path mapping for `/api/*`
3. Check Render logs for rejected requests or upstream errors

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
