
# Web App for Davar

This is the web application package for Davar.

## Running the code

Run `bun install` to install dependencies.

Run `bun run dev` for production-parity local serving (builds `dist/` then serves it).

Run `bun run dev:hot` for Bun HTML hot-reload mode.

## Formatting

- This workspace uses Biome as the formatter/linter source of truth for JS/TS files.
- Use `bun run format` in this `web/` directory to format files.
- Prettier is intentionally not configured at project level in this workspace.
  
