"""Tests that ai.py escapes ticket ids before building PostgREST filters."""

from unittest.mock import patch

import ai

HOSTILE_ID = "x&status=eq.Open,id=neq.1"
ESCAPED_ID = "x%26status%3Deq.Open%2Cid%3Dneq.1"


def test_fetch_ticket_escapes_id():
    with patch.object(ai, "db_get", return_value=[{"id": "t"}]) as db_get:
        ai._fetch_ticket(HOSTILE_ID)
    db_get.assert_called_once_with("tickets", f"id=eq.{ESCAPED_ID}")


def test_fetch_notes_escapes_ticket_id():
    with patch.object(ai, "db_get", return_value=[]) as db_get:
        ai._fetch_notes(HOSTILE_ID)
    db_get.assert_called_once_with(
        "ticket_notes", f"ticket_id=eq.{ESCAPED_ID}&order=created_at.asc"
    )
