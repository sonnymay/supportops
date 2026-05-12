from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import db_get, db_post, db_patch, db_delete
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="SupportOps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://supportops.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class Customer(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

class Device(BaseModel):
    serial_number: str
    model: Optional[str] = None
    product_type: Optional[str] = None
    customer_id: Optional[str] = None

class Ticket(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "Open"
    priority: Optional[str] = "Medium"
    customer_id: Optional[str] = None
    device_id: Optional[str] = None
    assigned_user_id: Optional[str] = None

class TicketNote(BaseModel):
    ticket_id: str
    note_text: str
    created_by: Optional[str] = "Agent"

class RMA(BaseModel):
    ticket_id: str
    rma_number: str
    serial_number: Optional[str] = None
    shipping_status: Optional[str] = "Pending"
    resolution_status: Optional[str] = "Pending"

# --- Health ---
@app.get("/health")
def health():
    return {"status": "ok"}

# --- Customers ---
@app.get("/customers")
def get_customers():
    return db_get("customers", "order=created_at.desc")

@app.post("/customers")
def create_customer(c: Customer):
    return db_post("customers", c.dict())

@app.put("/customers/{id}")
def update_customer(id: str, c: Customer):
    return db_patch("customers", id, c.dict())

@app.delete("/customers/{id}")
def delete_customer(id: str):
    return db_delete("customers", id)

# --- Devices ---
@app.get("/devices")
def get_devices():
    return db_get("devices", "order=created_at.desc")

@app.post("/devices")
def create_device(d: Device):
    return db_post("devices", d.dict())

@app.put("/devices/{id}")
def update_device(id: str, d: Device):
    return db_patch("devices", id, d.dict())

# --- Tickets ---
@app.get("/tickets")
def get_tickets():
    return db_get("tickets", "order=created_at.desc")

@app.get("/tickets/{id}")
def get_ticket(id: str):
    result = db_get("tickets", f"id=eq.{id}")
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result[0]

@app.post("/tickets")
def create_ticket(t: Ticket):
    return db_post("tickets", t.dict())

@app.put("/tickets/{id}")
def update_ticket(id: str, t: Ticket):
    data = t.dict()
    old = db_get("tickets", f"id=eq.{id}&select=status")
    if old and old[0]["status"] != data["status"]:
        db_post("ticket_history", {
            "ticket_id": id,
            "old_status": old[0]["status"],
            "new_status": data["status"],
            "changed_by": "Agent"
        })
    return db_patch("tickets", id, data)

# --- Notes ---
@app.get("/tickets/{id}/notes")
def get_notes(id: str):
    return db_get("ticket_notes", f"ticket_id=eq.{id}&order=created_at.asc")

@app.post("/notes")
def create_note(n: TicketNote):
    return db_post("ticket_notes", n.dict())

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
    return db_post("rmas", r.dict())

@app.put("/rmas/{id}")
def update_rma(id: str, r: RMA):
    return db_patch("rmas", id, r.dict())

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

# --- Root ---
@app.get("/")
def root():
    return {"status": "SupportOps API running"}
