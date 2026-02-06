import app from "./index.html";

const port = Number(process.env.PORT ?? 3002);

Bun.serve({
  port,
  routes: {
    "/*": app,
  },
});

console.log(`[davar-web] server listening on http://localhost:${port}`);
