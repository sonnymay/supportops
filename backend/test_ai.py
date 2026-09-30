"""Tests that ai.py escapes ticket ids before building PostgREST filters."""

from unittest.mock import patch

import pytest

pytest.importorskip("anthropic")

import ai  # noqa: E402  (imported after the optional-dependency check)


def test_fetch_ticket_escapes_id():
    with patch.object(ai, "db_get", return_value=[{"id": "x"}]) as db_get:
        ai._fetch_ticket("abc&select=*")
    assert db_get.call_args.args == ("tickets", "id=eq.abc%26select%3D%2A")


def test_fetch_notes_escapes_id():
    with patch.object(ai, "db_get", return_value=[]) as db_get:
        ai._fetch_notes("a,b&c")
    assert db_get.call_args.args == ("ticket_notes", "ticket_id=eq.a%2Cb%26c&order=created_at.asc")
