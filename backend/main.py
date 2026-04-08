from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import supabase
from pydantic import BaseModel
from typing import Optional
import uuid

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

# --- Customers ---
@app.get("/customers")
def get_customers():
    return supabase.table("customers").select("*").execute().data

@app.post("/customers")
def create_customer(c: Customer):
    return supabase.table("customers").insert(c.dict()).execute().data

@app.put("/customers/{id}")
def update_customer(id: str, c: Customer):
    return supabase.table("customers").update(c.dict()).eq("id", id).execute().data

@app.delete("/customers/{id}")
def delete_customer(id: str):
    return supabase.table("customers").delete().eq("id", id).execute().data

# --- Devices ---
@app.get("/devices")
def get_devices():
    return supabase.table("devices").select("*").execute().data

@app.post("/devices")
def create_device(d: Device):
    return supabase.table("devices").insert(d.dict()).execute().data

@app.put("/devices/{id}")
def update_device(id: str, d: Device):
    return supabase.table("devices").update(d.dict()).eq("id", id).execute().data

# --- Tickets ---
@app.get("/tickets")
def get_tickets():
    return supabase.table("tickets").select("*").execute().data

@app.get("/tickets/{id}")
def get_ticket(id: str):
    result = supabase.table("tickets").select("*").eq("id", id).execute().data
    if not result:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return result[0]

@app.post("/tickets")
def create_ticket(t: Ticket):
    return supabase.table("tickets").insert(t.dict()).execute().data

@app.put("/tickets/{id}")
def update_ticket(id: str, t: Ticket):
    data = t.dict()
    old = supabase.table("tickets").select("status").eq("id", id).execute().data
    if old and old[0]["status"] != data["status"]:
        supabase.table("ticket_history").insert({
            "ticket_id": id,
            "old_status": old[0]["status"],
            "new_status": data["status"],
            "changed_by": "Agent"
        }).execute()
    return supabase.table("tickets").update(data).eq("id", id).execute().data

# --- Notes ---
@app.get("/tickets/{id}/notes")
def get_notes(id: str):
    return supabase.table("ticket_notes").select("*").eq("ticket_id", id).execute().data

@app.post("/notes")
def create_note(n: TicketNote):
    return supabase.table("ticket_notes").insert(n.dict()).execute().data

# --- History ---
@app.get("/tickets/{id}/history")
def get_history(id: str):
    return supabase.table("ticket_history").select("*").eq("ticket_id", id).execute().data

# --- RMAs ---
@app.get("/rmas")
def get_rmas():
    return supabase.table("rmas").select("*").execute().data

@app.post("/rmas")
def create_rma(r: RMA):
    return supabase.table("rmas").insert(r.dict()).execute().data

@app.put("/rmas/{id}")
def update_rma(id: str, r: RMA):
    return supabase.table("rmas").update(r.dict()).eq("id", id).execute().data

# --- Dashboard ---
@app.get("/dashboard")
def dashboard():
    tickets = supabase.table("tickets").select("status, priority").execute().data
    rmas = supabase.table("rmas").select("resolution_status").execute().data
    return {
        "open_tickets": sum(1 for t in tickets if t["status"] == "Open"),
        "in_progress": sum(1 for t in tickets if t["status"] == "In Progress"),
        "closed_tickets": sum(1 for t in tickets if t["status"] == "Closed"),
        "critical": sum(1 for t in tickets if t["priority"] == "Critical"),
        "rmas_in_progress": sum(1 for r in rmas if r["resolution_status"] == "Pending"),
    }

# --- Root ---
@app.get("/")
def root():
    return {"status": "SupportOps API running"}