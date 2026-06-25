import ai
import database
from database import DatabaseConfigError, DatabaseRequestError, db_delete, db_get, db_patch, db_post

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="SupportOps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://supportops.vercel.app",
    ],
    # Allow Vercel preview deploys (e.g. supportops-git-branch-sonnymay.vercel.app)
    allow_origin_regex=r"https://supportops-[a-z0-9-]+(-sonnymay)?\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(DatabaseConfigError)
def database_config_error(_request: Request, exc: DatabaseConfigError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})

@app.exception_handler(DatabaseRequestError)
def database_request_error(_request: Request, exc: DatabaseRequestError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})

# --- Models ---
class Customer(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    company: str | None = None

class Device(BaseModel):
    serial_number: str
    model: str | None = None
    product_type: str | None = None
    customer_id: str | None = None

class Ticket(BaseModel):
    title: str
    description: str | None = None
    status: str | None = "Open"
    priority: str | None = "Medium"
    customer_id: str | None = None
    device_id: str | None = None
    assigned_user_id: str | None = None

class TicketNote(BaseModel):
    ticket_id: str
    note_text: str
    created_by: str | None = "Agent"

class RMA(BaseModel):
    ticket_id: str
    rma_number: str
    serial_number: str | None = None
    shipping_status: str | None = "Pending"
    resolution_status: str | None = "Pending"

def clean_empty_strings(data: dict, *keys: str) -> dict:
    for key in keys:
        if data.get(key) == "":
            data[key] = None
    return data

def model_data(model: BaseModel) -> dict:
    return model.model_dump()

# --- Health ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/dependencies")
def dependency_health(response: Response):
    configured = database.is_configured()
    reachable = False
    detail = None

    if not configured:
        response.status_code = 503
        detail = "SUPABASE_URL and SUPABASE_KEY must be configured in Render."
    else:
        try:
            db_get("customers", "select=id&limit=1")
            reachable = True
        except (DatabaseConfigError, DatabaseRequestError) as error:
            response.status_code = 503
            detail = str(error)

    return {
        "status": "ok" if reachable else "error",
        "supabase": {
            "configured": configured,
            "reachable": reachable,
            "detail": detail,
        },
    }

# --- Customers ---
@app.get("/customers")
def get_customers():
    return db_get("customers", "order=created_at.desc")

@app.post("/customers")
def create_customer(c: Customer):
    return db_post("customers", model_data(c))

@app.put("/customers/{id}")
def update_customer(id: str, c: Customer):
    return db_patch("customers", id, model_data(c))

@app.delete("/customers/{id}")
def delete_customer(id: str):
    return db_delete("customers", id)

# --- Devices ---
@app.get("/devices")
def get_devices():
    return db_get("devices", "order=created_at.desc")

@app.post("/devices")
def create_device(d: Device):
    return db_post("devices", clean_empty_strings(model_data(d), "customer_id"))

@app.put("/devices/{id}")
def update_device(id: str, d: Device):
    return db_patch("devices", id, clean_empty_strings(model_data(d), "customer_id"))

# --- Tickets ---
@app.get("/tickets")
def get_tickets():
    return db_get("tickets", "order=created_at.desc")

@app.get("/tickets/search")
def search_tickets(q: str = Query(..., min_length=1, description="Search term")):
    """Full-text search across ticket title and description.

    Uses Supabase PostgREST ilike filters -- case-insensitive substring match.
    Returns tickets where the term appears in title OR description, sorted by
    most recently created first.
    """
    term = q.strip()
    results = db_get(
        "tickets",
        f"or=(title.ilike.*{term}*,description.ilike.*{term}*)&order=created_at.desc",
    )
    return results if isinstance(results, list) else []

@app.get("/tickets/filter")
def filter_tickets(
    status: str | None = Query(None, description="Filter by status: Open, In Progress, Closed"),
    priority: str | None = Query(None, description="Filter by priority: Low, Medium, High, Critical"),
    assigned_user_id: str | None = Query(None, description="Filter by assigned agent ID"),
):
    """Return tickets filtered by any combination of status, priority, and assignee.

    All parameters are optional -- omitting a parameter means 'any value'.
    Results are sorted most-recently-created first.
    Supports the saved-views pattern: callers can persist query params as a named view.
    """
    parts: list[str] = []
    if status:
        parts.append(f"status=eq.{status}")
    if priority:
        parts.append(f"priority=eq.{priority}")
    if assigned_user_id:
        parts.append(f"assigned_user_id=eq.{assigned_user_id}")
    parts.append("order=created_at.desc")
    query = "&".join(parts)
    results = db_get("tickets", query)
    return results if isinstance(results, list) else []

@app.get("/tickets/{id}")
def get_ticket(id: str):
    result = db_get("tickets", f"id=eq.{id}")
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result[0]

@app.post("/tickets")
def create_ticket(t: Ticket):
    return db_post(
        "tickets",
        clean_empty_strings(model_data(t), "customer_id", "device_id", "assigned_user_id"),
    )

@app.put("/tickets/{id}")
def update_ticket(id: str, t: Ticket):
    data = clean_empty_strings(model_data(t), "customer_id", "device_id", "assigned_user_id")
    old = db_get("tickets", f"id=eq.{id}&select=status")
    if old and old[0]["status"] != data["status"]:
        db_post(
            "ticket_history",
            {
                "ticket_id": id,
                "old_status": old[0]["status"],
                "new_status": data["status"],
                "changed_by": "Agent",
            },
        )
    return db_patch("tickets", id, data)

# --- Notes ---
@app.get("/tickets/{id}/notes")
def get_notes(id: str):
    return db_get("ticket_notes", f"ticket_id=eq.{id}&order=created_at.asc")

@app.post("/notes")
def create_note(n: TicketNote):
    return db_post("ticket_notes", model_data(n))

# --- History ---
@app.get("/tickets/{id}/history")
def get_history(id: str):
    return db_get("ticket_history", f"ticket_id=eq.{id}&order=changed_at.asc")

# --- RMAs ---
@app.get("/rmas")
def get_rmas():
    return db_get("rmas", "order=created_at.desc")

@app.post("/rmas")
def create_rma(r: RMA):
    return db_post("rmas", model_data(r))

@app.put("/rmas/{id}")
def update_rma(id: str, r: RMA):
    return db_patch("rmas", id, model_data(r))

# --- Dashboard ---
@app.get("/dashboard")
def dashboard():
    tickets = db_get("tickets", "select=status,priority")
    rmas = db_get("rmas", "select=resolution_status")
    if not isinstance(tickets, list):
        tickets = []
    if not isinstance(rmas, list):
        rmas = []
    return {
        "open_tickets": sum(1 for t in tickets if t.get("status") == "Open"),
        "in_progress": sum(1 for t in tickets if t.get("status") == "In Progress"),
        "closed_tickets": sum(1 for t in tickets if t.get("status") == "Closed"),
        "critical": sum(1 for t in tickets if t.get("priority") == "Critical"),
        "rmas_in_progress": sum(1 for r in rmas if r.get("resolution_status") == "Pending"),
    }

# --- AI ---
class AISuggestRequest(BaseModel):
    ticket_id: str

@app.post("/ai/suggest")
def ai_suggest(req: AISuggestRequest):
    try:
        return ai.suggest_for_ticket(req.ticket_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI suggestion failed: {e}") from e

# --- Root ---
@app.get("/")
def root():
    return {"status": "SupportOps API running"}
