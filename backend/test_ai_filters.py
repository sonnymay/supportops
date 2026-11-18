"""ai.py must escape the caller-supplied ticket id before building PostgREST filters."""

from unittest.mock import patch

import ai

CRAFTED = "t1&status=eq.Closed"


def test_fetch_ticket_escapes_id():
    with patch("ai.db_get", return_value=[{"id": "t1"}]) as db_get:
        ai._fetch_ticket(CRAFTED)
    assert db_get.call_args.args[1] == "id=eq.t1%26status%3Deq.Closed"


def test_fetch_notes_escapes_id():
    with patch("ai.db_get", return_value=[]) as db_get:
        ai._fetch_notes(CRAFTED)
    params = db_get.call_args.args[1]
    assert "&status=eq.Closed" not in params
    assert params.endswith("&order=created_at.asc")
