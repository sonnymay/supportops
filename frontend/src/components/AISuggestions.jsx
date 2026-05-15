import { useState } from "react";
import { api } from "../api";

const confidenceColor = (c) => ({
  high: "bg-purple-100 text-purple-700",
  medium: "bg-purple-50 text-purple-600",
  low: "bg-gray-100 text-gray-500",
}[(c || "").toLowerCase()] || "bg-purple-50 text-purple-600");

export default function AISuggestions({ ticketId }) {
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState(null);
  const [error, setError] = useState(null);
  const [note, setNote] = useState(null);

  const run = async () => {
    if (!ticketId) return;
    setLoading(true);
    setError(null);
    setMatches(null);
    setNote(null);
    try {
      const res = await api.post("/ai/suggest", { ticket_id: ticketId });
      if (res?.detail) {
        setError(res.detail);
      } else if (res?.error) {
        setError(res.error);
      } else {
        setMatches(res?.matches || []);
        if (res?.note) setNote(res.note);
      }
    } catch (e) {
      setError(e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-4 border-l-4 border-purple-500">
      <div className="flex justify-between items-center mb-3">
        <div>
          <h3 className="font-semibold text-purple-700">AI Resolution Suggester</h3>
          <p className="text-xs text-gray-500">
            Finds the 3 most similar resolved tickets and drafts a suggested fix.
          </p>
        </div>
        <button
          onClick={run}
          disabled={loading || !ticketId}
          className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 text-sm disabled:opacity-50"
        >
          {loading ? "Thinking…" : "Suggest Fixes"}
        </button>
      </div>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-100 rounded px-3 py-2 mt-2">
          {error}
        </div>
      )}

      {note && !error && (
        <p className="text-sm text-gray-500 mt-2">{note}</p>
      )}

      {matches && matches.length === 0 && !note && !error && (
        <p className="text-sm text-gray-500 mt-2">No similar resolved tickets found yet.</p>
      )}

      {matches && matches.length > 0 && (
        <div className="mt-4 space-y-3">
          {matches.map((m, i) => (
            <div
              key={m.ticket_id || i}
              className="border border-purple-100 rounded-lg p-4 bg-purple-50/40"
            >
              <div className="flex justify-between items-start gap-2 mb-2">
                <p className="font-medium text-sm text-purple-900">
                  #{i + 1} · {m.title || "Untitled ticket"}
                </p>
                {m.confidence && (
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${confidenceColor(m.confidence)}`}>
                    {m.confidence}
                  </span>
                )}
              </div>
              {m.similarity_reason && (
                <p className="text-xs text-gray-600 mb-2">
                  <span className="font-semibold text-purple-700">Why similar: </span>
                  {m.similarity_reason}
                </p>
              )}
              {m.suggested_resolution && (
                <p className="text-sm text-gray-800 whitespace-pre-wrap">
                  <span className="font-semibold text-purple-700">Suggested fix: </span>
                  {m.suggested_resolution}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
