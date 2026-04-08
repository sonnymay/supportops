import os
import requests
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
    r = requests.get(url, headers=get_headers())
    return r.json()

def db_post(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=get_headers(), json=data)
    return r.json()

def db_patch(table, id, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}"
    r = requests.patch(url, headers=get_headers(), json=data)
    return r.json()

def db_delete(table, id):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}"
    r = requests.delete(url, headers=get_headers())
    return r.json()
