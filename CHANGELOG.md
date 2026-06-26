# Changelog

All notable changes to SupportOps are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Planned
- Role-based auth (agent / lead / admin) with JWT bearer tokens
- SLA timers with breach alerts
- CSV export of tickets and RMAs
- Email intake — create tickets from inbound email via webhook
- Full-text search across tickets and notes (`GET /tickets/search`)
- Webhook notifications for ticket status changes (Slack, Discord)
- Saved views / filter presets per agent (`GET /tickets/filter`)

---

## [1.3.0] — Ticket search and filter endpoints

### Added
- `GET /tickets/search?q=` — case-insensitive ilike search across ticket title and description
- `GET /tickets/filter` — filter tickets by `status`, `priority`, and `assigned_user_id`; supports saved-view query params

---

## [1.2.0] — AI Resolution Suggester

### Added
- `POST /ai/suggest` — Claude Haiku reads the open ticket plus its full note history, compares against the 30 most-recently-resolved tickets, and returns the top 3 resolution suggestions with confidence scores
- `ANTHROPIC_MODEL` env var to control which Claude model is used

---

## [1.1.0] — Docker and cold-start UX

### Added
- `Dockerfile` and `docker-compose.yml` for local development
- Frontend warm-up ping on app load with informative loading state for Render free-tier cold starts
- `render.yaml` deploy config
- `GET /health/dependencies` — reports Supabase connectivity and configuration status

---

## [1.0.0] — Initial release

### Added
- Tickets with status, priority, assignee, linked customer and device
- Customers directory (name, email, phone, company)
- Devices tied to customers by serial number and product type
- Ticket notes for agent context and handoffs
- Automatic status history — every status change logged with actor and timestamp
- RMA tracking linked to originating ticket
- `GET /dashboard` — open/in-progress/closed counts, critical count, RMAs in progress
- FastAPI + Pydantic backend with Supabase PostgREST
- GitHub Actions CI with mocked Supabase and AI boundaries
- Vercel (frontend) + Render (backend) hosting
