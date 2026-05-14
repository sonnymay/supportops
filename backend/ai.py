from __future__ import annotations

import os
import json
import re
from typing import Any, Optional

from anthropic import Anthropic
from dotenv import load_dotenv

from database import db_get

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

_client: Optional[Anthropic] = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        if not ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        _client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _fetch_ticket(ticket_id: str) -> dict[str, Any]:
    result = db_get("tickets", f"id=eq.{ticket_id}")
    if not isinstance(result, list) or not result:
        raise ValueError(f"Ticket {ticket_id} not found")
    return result[0]


def _fetch_notes(ticket_id: str) -> list[dict[str, Any]]:
    notes = db_get("ticket_notes", f"ticket_id=eq.{ticket_id}&order=created_at.asc")
    return notes if isinstance(notes, list) else []


def _fetch_recent_resolved(limit: int = 30) -> list[dict[str, Any]]:
    params = (
        "status=in.(Resolved,Closed)"
        "&order=created_at.desc"
        f"&limit={limit}"
    )
    tickets = db_get("tickets", params)
    if not isinstance(tickets, list):
        return []
    for t in tickets:
        t["_notes"] = _fetch_notes(t["id"])
    return tickets


def _summarize_notes(notes: list[dict[str, Any]], max_chars: int = 600) -> str:
    if not notes:
        return "(no notes)"
    text = " | ".join(
        f"{n.get('created_by', 'Agent')}: {n.get('note_text', '').strip()}"
        for n in notes
        if n.get("note_text")
    )
    return text[:max_chars]


def _build_prompt(ticket: dict[str, Any], notes: list[dict[str, Any]], history: list[dict[str, Any]]) -> str:
    target = {
        "id": ticket.get("id"),
        "title": ticket.get("title"),
        "description": ticket.get("description") or "",
        "status": ticket.get("status"),
        "priority": ticket.get("priority"),
        "notes": _summarize_notes(notes),
    }

    past = []
    for t in history:
        past.append({
            "id": t.get("id"),
            "title": t.get("title"),
            "description": (t.get("description") or "")[:400],
            "status": t.get("status"),
            "priority": t.get("priority"),
            "notes": _summarize_notes(t.get("_notes", [])),
        })

    return (
        "You are an expert technical support assistant. Compare the OPEN ticket below "
        "to the list of recently RESOLVED/CLOSED tickets and select the top 3 most "
        "similar past tickets. For each, summarize the suggested resolution based on "
        "the past ticket's notes and outcome.\n\n"
        "Return ONLY a valid JSON object matching this schema exactly:\n"
        "{\n"
        '  "matches": [\n'
        "    {\n"
        '      "ticket_id": "<id of past ticket>",\n'
        '      "title": "<title of past ticket>",\n'
        '      "similarity_reason": "<1-2 sentences on why it is similar>",\n'
        '      "suggested_resolution": "<concrete steps drawn from past notes>",\n'
        '      "confidence": "low|medium|high"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "OPEN TICKET:\n"
        f"{json.dumps(target, indent=2)}\n\n"
        "PAST RESOLVED TICKETS:\n"
        f"{json.dumps(past, indent=2)}\n\n"
        "Respond with the JSON object only — no prose, no markdown fences."
    )


def _extract_json(text: str) -> dict[str, Any]:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    return json.loads(text)


def suggest_for_ticket(ticket_id: str) -> dict[str, Any]:
    ticket = _fetch_ticket(ticket_id)
    notes = _fetch_notes(ticket_id)
    history = _fetch_recent_resolved(30)

    if not history:
        return {"matches": [], "note": "No resolved tickets available for comparison."}

    prompt = _build_prompt(ticket, notes, history)
    client = _get_client()

    msg = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = "".join(block.text for block in msg.content if getattr(block, "type", None) == "text")

    try:
        parsed = _extract_json(raw)
    except json.JSONDecodeError:
        return {"matches": [], "raw": raw, "error": "Model returned non-JSON output"}

    matches = parsed.get("matches", [])[:3]
    return {"matches": matches}
