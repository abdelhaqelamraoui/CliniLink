This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

<<<<<<< Updated upstream
## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
=======
Client application for CliniLink. It talks only to the API Gateway.
Next.js 16 (App Router) · React 19 · Tailwind CSS 4 · TypeScript.

Planned areas:
- Patient app: search, book, queue, reports, ratings
- Doctor portal: agenda, availability, prices, reports
- Back-office: staff and admin console

Done so far: landing page, in English and Arabic.

## Run

```bash
npm install
npm run dev          # http://localhost:3000
npm run build && npm start
npm run lint
```

## Docker

From this folder, with `compose.yaml`:

```bash
# Production build: same image as the platform compose
docker compose up -d --build                           # http://localhost:3000

# Development: next dev with hot reload, your local files are mounted
docker compose --profile dev up --build frontend-dev   # http://localhost:3001

docker compose --profile dev down
```

| File | Purpose |
|---|---|
| `Dockerfile` | Production. Multi-stage: `npm ci` → `next build` → Next's standalone server only. Runs as a non-root user, with a health check |
| `Dockerfile.dev` | Development. Installs dependencies; compose mounts the source and runs `next dev` |
| `compose.yaml` | `frontend` (production, port 3000) and `frontend-dev` (profile `dev`, port 3001) |

The dev container keeps its own `node_modules` and `.next` (Linux builds), so it never mixes them
with the ones on your machine. `WATCHPACK_POLLING` makes hot reload reliable on macOS and Windows.

The frontend is also in `infra/docker-compose.yml`, to start it with the rest of the platform:

```bash
docker compose -f ../infra/docker-compose.yml up -d --build frontend
```

`NEXT_PUBLIC_SITE_URL` (build argument) is the public URL used for canonical and hreflang links.

## Languages (English / Arabic)

- Every page lives under `app/[lang]/`, so the URLs are `/en/...` and `/ar/...`.
- `proxy.ts` (Next 16's name for middleware) redirects `/` to the visitor's language. It uses the
  `NEXT_LOCALE` cookie if set, then the browser's `Accept-Language`, then English. Visiting
  `/en` or `/ar` saves that choice in the cookie.
- For Arabic, the layout sets `lang="ar" dir="rtl"` and uses the IBM Plex Sans Arabic font. Components
  use logical Tailwind classes (`ms-`, `me-`, `start-`, `text-start`), so the layout mirrors on its
  own. Directional icons use `rtl:-scale-x-100`.
- Translations are in `i18n/dictionaries/en.ts` and `ar.ts`. English defines the `Dictionary` type,
  so a key missing or misspelled in Arabic is a TypeScript error at build time.
- Server components read the text with `await getDictionary()`, which finds the locale through
  `next/root-params`. The dictionaries never reach the client bundle.

To add a language: add it to `i18n/config.ts`, add `i18n/dictionaries/<code>.ts` typed as
`Dictionary`, and register it in `i18n/get-dictionary.ts`.

## Logo and icons

- `public/logo-mark.svg`: the logo mark (medical cross with a "link" node). In pages, use
  `<Logo id="..." />` or `<LogoMark />` from `components/logo.tsx`.
- `app/icon.svg`, `app/favicon.ico` (16/32/48 px), `app/apple-icon.png` (180 px) are generated from
  the mark with `npm run icons`. Next.js adds the `<link rel="icon">` tags automatically.

## Structure

```
app/
  [lang]/layout.tsx      html lang/dir, fonts, metadata per language
  [lang]/page.tsx        landing page
  global-not-found.tsx   404 for URLs outside /en and /ar
  globals.css            Tailwind + theme
  icon.svg, favicon.ico, apple-icon.png
components/
  landing/               header, hero, queue card, features, steps, audiences, CTA, footer
  logo.tsx, icons.tsx, language-switcher.tsx
i18n/                    locales, dictionaries, getDictionary()
proxy.ts                 language redirect + cookie
scripts/generate-icons.mjs
```
>>>>>>> Stashed changes
