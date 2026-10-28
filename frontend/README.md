# SupportOps frontend

React 19 + Vite + Tailwind CSS 4 single-page app for the SupportOps ticketing and RMA tool. It talks to the FastAPI backend in [`../backend`](../backend); see the [root README](../README.md) for the full project overview.

## Setup

```bash
cp .env.example .env   # then edit if your backend isn't on localhost:8000
npm ci
npm run dev            # http://localhost:5173
```

### Environment

| Variable            | Purpose                                                        |
|---------------------|----------------------------------------------------------------|
| `VITE_API_BASE_URL` | Base URL of the backend API, e.g. `http://localhost:8000`. Required; without it every API call fails with a configuration error. |

## Scripts

| Command           | What it does                         |
|-------------------|--------------------------------------|
| `npm run dev`     | Start the Vite dev server with HMR   |
| `npm run build`   | Production build into `dist/`        |
| `npm run preview` | Serve the production build locally   |
| `npm run lint`    | Run ESLint                           |

## Layout

- `src/api.js` – fetch wrapper (`api.get/post/put/delete`), `ApiError`, the `useApiResource` loading/error/data hook, and `warmupBackend()`, which pings `/health` on load so a sleeping Render free-tier backend starts waking early. Requests time out after 90s to allow for cold starts.
- `src/pages/` – one page per resource: Dashboard, Tickets, Customers, Devices, RMAs.
- `src/components/` – shared pieces: `AsyncState` (loading/error UI) and `AISuggestions` (calls `POST /ai/suggest`).

## Deployment

Deployed on Vercel. `vercel.json` rewrites all paths to `index.html` so client-side routes survive a refresh. Set `VITE_API_BASE_URL` in the Vercel project settings.
