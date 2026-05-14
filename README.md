# SupportOps

> A lightweight ticketing and RMA workflow tool built by a tech support engineer, for tech support engineers.

**Live demo:** [supportops.vercel.app](https://supportops.vercel.app)

---

## Why this exists

After 9 years on the front lines of technical support, I kept hitting the same walls with the tools I was given:

- Tickets, customers, and devices lived in three different systems that didn't talk to each other.
- RMA tracking was a spreadsheet someone forgot to update.
- Status changes had no audit trail when a customer asked "who closed my ticket and why?"
- The "enterprise" platforms were slow, bloated, and built for managers — not the agent actually working the queue.

SupportOps is the tool I wished I had. Tickets, devices, customers, RMAs, and a full status history — in one place, fast, and built around how support actually works.

---

## Features

- **Tickets** with status, priority, assignee, and linked customer + device
- **Customers** directory (name, email, phone, company)
- **Devices** tied to customers by serial number and product type
- **Ticket notes** for agent-side context and handoffs
- **Automatic status history** — every status change is logged with who and when
- **RMA tracking** — RMA number, serial, shipping status, resolution status, linked to the originating ticket

---

## Stack

| Layer    | Tech                                    |
|----------|-----------------------------------------|
| Frontend | React 19, Vite, Tailwind CSS v4, React Router |
| Backend  | FastAPI (Python), Pydantic              |
| Database | Supabase (PostgREST)                    |
| Hosting  | Vercel (frontend) + Render (backend)    |

---

## Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  React + Vite │ ───▶ │   FastAPI    │ ───▶ │  Supabase    │
│   (Vercel)    │      │   (Render)   │      │ (PostgREST)  │
└──────────────┘      └──────────────┘      └──────────────┘
```

The FastAPI layer is intentionally thin — it validates with Pydantic, applies business rules (e.g. writing to `ticket_history` on status change), and proxies to Supabase's REST API.

---

## Local development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "SUPABASE_URL=your-url"  > .env
echo "SUPABASE_KEY=your-key" >> .env
uvicorn main:app --reload
```

API runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`.

---

## API surface

| Resource    | Endpoints                                 |
|-------------|-------------------------------------------|
| Customers   | `GET/POST/PUT/DELETE /customers`          |
| Devices     | `GET/POST/PUT /devices`                   |
| Tickets     | `GET/POST/PUT /tickets`, `GET /tickets/{id}` |
| Ticket Notes| `GET/POST /ticket-notes`                  |
| RMAs        | `GET/POST/PUT /rmas`                      |

Status changes on tickets automatically append a row to `ticket_history`.

---

## Roadmap

- [ ] Full-text ticket search
- [ ] SLA timers + breach alerts
- [ ] CSV export for reporting
- [ ] Role-based auth (agent / manager / admin)
- [ ] Email-to-ticket intake

---

## Screenshots

<!-- Add screenshots of the dashboard, ticket detail (with AI Suggestions), and RMA views here. -->
_Coming soon._

---

## About

Built by [Sonny May](https://github.com/sonnymay) — tech support engineer, 9 years in the trenches.

Built and used internally at Baicells Technologies to manage real support tickets, RMAs, and device history.

If you've worked support and recognize the pain this is solving, I'd love to hear from you.
