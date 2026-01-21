---
applyTo: "**/*.[jt]s, **/*.[jt]sx, **/package.json, **/bun.lockb"
description: Force Bun as the only JavaScript runtime and package manager - never suggest or allow others
---

# Bun Runtime & Execution Rules - Davar Project

- ALWAYS use **Bun** as the JavaScript/TypeScript runtime and package manager.
- NEVER suggest, mention, or generate commands for npm, yarn, pnpm, deno, node scripts, ts-node, or any other runtime/package manager.  
  Forbidden examples:
  - npm install / npm run / npm start
  - yarn add / yarn dev
  - pnpm install / pnpm dev
  - node server.js / ts-node
- Use **only** Bun-compatible commands:
  - bun install
  - bun add <package>
  - bun run dev / bun dev
  - bun --bun
  - bunx <command>
  - bun test
  - bun upgrade
- When suggesting to run any command (install, dev server, lint, build, etc.):
  1. Tell me the EXACT command to run
  2. Specify the exact directory/path where it should be executed (e.g. project root, /apps/mobile)
  3. DO NOT run ANY command yourself in this chat
  4. DO NOT generate, simulate, or invent terminal output / logs
  5. Wait for me to confirm execution and paste the real output (including any errors)
  6. ONLY after I provide the actual logs/output, continue with analysis, fix, or next step
- Keep all responses clean — no fake terminal blocks, no assumed success/failure messages.
- If initial setup is needed, suggest: `cd /path/to/davar-project && bun install`
- This rule has **high priority** and overrides any default model behavior regarding package managers or runtimes.

Applies to: ALL code suggestions, debugging, installation steps, dev workflows in the Davar project.
