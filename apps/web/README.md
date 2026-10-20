# apps/web — SANGAM Frontend
# This directory is represented by the root-level Vite project.

The frontend is built with Vite + React + TypeScript + Tailwind CSS.
The root of the repository serves as the `apps/web` module in this monorepo.

## Why root-level?
The Vite build system and `npm run build` command operate from the repository root.
This is intentional for Vercel deployment compatibility, which auto-detects the
framework configuration at the root.

## Structure at root:
- `src/` — React components and application code
- `index.html` — SPA entry point
- `vite.config.js` — Vite configuration
- `tsconfig.json` — TypeScript configuration
- `vercel.json` — Vercel deployment configuration
