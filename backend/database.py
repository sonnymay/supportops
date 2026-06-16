import os

import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_UNAVAILABLE_DETAIL = (
    "SupportOps database is unavailable. Check SUPABASE_URL, SUPABASE_KEY, "
    "and Supabase table setup in Render."
)


class DatabaseConfigError(RuntimeError):
    """Raised when required Supabase configuration is missing."""


class DatabaseRequestError(RuntimeError):
    """Raised when Supabase rejects or cannot complete a request."""


def is_configured():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def require_config():
    if not is_configured():
        raise DatabaseConfigError("SUPABASE_URL and SUPABASE_KEY must be configured in Render.")


def get_headers():
    require_config()
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def handle_response(response):
    try:
        response.raise_for_status()
    except requests.RequestException as error:
        raise DatabaseRequestError(DATABASE_UNAVAILABLE_DETAIL) from error

    if response.status_code == 204 or not response.text:
        return None

    try:
        return response.json()
    except ValueError as error:
        raise DatabaseRequestError(DATABASE_UNAVAILABLE_DETAIL) from error


def request_supabase(method, table, params="", data=None):
    query = f"?{params}" if params else ""
    response = requests.request(
        method,
        f"{SUPABASE_URL}/rest/v1/{table}{query}",
        headers=get_headers(),
        json=data,
        timeout=20,
    )
    return handle_response(response)


def db_get(table, params=""):
    return request_supabase("GET", table, params=params)


def db_post(table, data):
    return request_supabase("POST", table, data=data)


def db_patch(table, id, data):
    return request_supabase("PATCH", table, params=f"id=eq.{id}", data=data)


def db_delete(table, id):
    return request_supabase("DELETE", table, params=f"id=eq.{id}")
