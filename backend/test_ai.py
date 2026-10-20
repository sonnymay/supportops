from unittest.mock import patch

import ai


def test_recent_resolved_fetches_notes_in_one_query():
    tickets = [{"id": "a"}, {"id": "b"}]
    notes = [
        {"ticket_id": "b", "note_text": "second"},
        {"ticket_id": "a", "note_text": "first"},
    ]
    with patch("ai.db_get", side_effect=[tickets, notes]) as db_get:
        result = ai._fetch_recent_resolved()

    assert db_get.call_count == 2
    assert "ticket_id=in.(a,b)" in db_get.call_args_list[1].args[1]
    assert result[0]["_notes"] == [notes[1]]
    assert result[1]["_notes"] == [notes[0]]


def test_recent_resolved_skips_notes_query_when_no_tickets():
    with patch("ai.db_get", return_value=[]) as db_get:
        assert ai._fetch_recent_resolved() == []
    assert db_get.call_count == 1
