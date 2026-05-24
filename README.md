# SupportOps

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/demo-supportops.vercel.app-brightgreen)](https://supportops.vercel.app)

> A lightweight ticketing and RMA workflow tool built by a tech support engineer, for tech support engineers.

**🔗 Live demo:** [supportops.vercel.app](https://supportops.vercel.app)
**📸 Screenshots:** see [below](#screenshots)

---

## Table of contents

- [Why this exists](#why-this-exists)
- [Features](#features)
- [Stack](#stack)
- [Architecture](#architecture)
- [Local development](#local-development)
- [API surface](#api-surface)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Why this exists

After 9 years on the front lines of technical support, I kept hitting the same walls with the tools I was given:

- Tickets, customers, and devices lived in three different systems that didn't talk to each other.
- RMA tracking was a spreadsheet someone forgot to update.
- Status changes had no audit trail when a customer asked *"who closed my ticket and why?"*
- The "enterprise" platforms were slow, bloated, and built for managers — not the agent actually working the queue.

SupportOps is the tool I wished I had. Tickets, devices, customers, RMAs, and a full status history — in one place, fast, and built around how support actually works.

---

## Features

- 🎫 **Tickets** with status, priority, assignee, and linked customer + device
- 👥 **Customers** directory (name, email, phone, company)
- 💻 **Devices** tied to customers by serial number and product type
- 📝 **Ticket notes** for agent-side context and handoffs
- 🕓 **Automatic status history** — every status change is logged with who and when
- 📦 **RMA tracking** — RMA number, serial, shipping status, resolution status, linked to the originating ticket

---

## Stack

| Layer    | Tech                                          |
|----------|-----------------------------------------------|
| Frontend | React 19, Vite, Tailwind CSS v4, React Router |
| Backend  | FastAPI (Python 3.11+), Pydantic              |
| Database | Supabase (Postgres + PostgREST)               |
| Hosting  | Vercel (frontend) · Render (backend)          |

---

## Architecture

```
┌───────────────┐      ┌──────────────┐      ┌──────────────┐
│  React + Vite │ ───▶ │   FastAPI    │ ───▶ │   Supabase   │
│   (Vercel)    │      │   (Render)   │      │ (PostgREST)  │
└───────────────┘      └──────────────┘      └──────────────┘
```

The FastAPI layer is intentionally thin — it validates with Pydantic, applies business rules (e.g. writing to `ticket_history` on every status change), and proxies to Supabase's REST API.

---

## Local development

### Prerequisites

- Python 3.11+
- Node.js 20+
- A Supabase project (free tier is fine) — grab your `SUPABASE_URL` and `SUPABASE_KEY`

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in SUPABASE_URL and SUPABASE_KEY
uvicorn main:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

---

## API surface

| Resource      | Endpoints                                    |
|---------------|----------------------------------------------|
| Customers     | `GET/POST/PUT/DELETE /customers`             |
| Devices       | `GET/POST/PUT /devices`                      |
| Tickets       | `GET/POST/PUT /tickets`, `GET /tickets/{id}` |
| Ticket Notes  | `GET/POST /ticket-notes`                     |
| RMAs          | `GET/POST/PUT /rmas`                         |

Status changes on tickets automatically append a row to `ticket_history`.

Full OpenAPI spec available at `http://localhost:8000/docs` when the backend is running.

---

## Screenshots

![Dashboard](public/screenshots/dashboard.png)
![Ticket Detail](public/screenshots/ticket-detail.png)

---

## Roadmap

- [ ] Full-text search across tickets and notes
- [ ] SLA timers with breach alerts
- [ ] Saved views / filters per agent
- [ ] CSV export of tickets and RMAs
- [ ] Role-based permissions (agent / lead / admin)

---

## Contributing

Issues and PRs are welcome — especially from anyone who's worked a support queue and has opinions on what's missing. Please open an issue describing the change before sending a large PR.

---

## License

[MIT](LICENSE) © Sonny May
