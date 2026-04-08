import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def db_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    with httpx.Client() as client:
        r = client.get(url, headers=get_headers())
        return r.json()

def db_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    with httpx.Client() as client:
        r = client.post(url, headers=get_headers(), json=data)
        return r.json()

def db_patch(table, id, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}"
    with httpx.Client() as client:
        r = client.patch(url, headers=get_headers(), json=data)
        return r.json()

def db_delete(table, id):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}"
    with httpx.Client() as client:
        r = client.delete(url, headers=get_headers())
        return r.json()
