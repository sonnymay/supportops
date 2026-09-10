import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()


def escape_filter_value(value: str, *, wildcard: bool = False) -> str:
    """Make a user-supplied value safe to interpolate into a PostgREST filter string.

    The value is percent-encoded so query-string delimiters cannot create new
    parameters.

    ``wildcard=True`` additionally quotes the complete ``*value*`` pattern for use
    inside a PostgREST logical expression. Embedded backslashes and double quotes
    are escaped within that quoted value, so commas and parentheses cannot terminate
    an ``or=(...)`` expression. Operators and other template structure remain the
    caller's responsibility.
    """
    if wildcard:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return quote(f'"*{escaped}*"', safe="*")
    return quote(value, safe="")


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_UNAVAILABLE_DETAIL = (
    "SupportOps data service is temporarily unavailable. It may be starting up; retry in a moment."
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
    try:
        response = requests.request(
            method,
            f"{SUPABASE_URL}/rest/v1/{table}{query}",
            headers=get_headers(),
            json=data,
            timeout=20,
        )
    except requests.RequestException as error:
        raise DatabaseRequestError(DATABASE_UNAVAILABLE_DETAIL) from error

    return handle_response(response)


def db_get(table, params=""):
    return request_supabase("GET", table, params=params)


def db_post(table, data):
    return request_supabase("POST", table, data=data)


def db_patch(table, id, data):
    return request_supabase("PATCH", table, params=f"id=eq.{escape_filter_value(id)}", data=data)


def db_delete(table, id):
    return request_supabase("DELETE", table, params=f"id=eq.{escape_filter_value(id)}")
