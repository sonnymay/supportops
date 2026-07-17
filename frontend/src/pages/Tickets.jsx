import { useEffect, useState } from "react";
import { api } from "../api";
import AISuggestions from "../components/AISuggestions";
import { LoadingState, ErrorState, InlineError } from "../components/AsyncState";

const STATUSES = ["Open", "In Progress", "Waiting on Customer", "Resolved", "Closed"];
const PRIORITIES = ["Low", "Medium", "High", "Critical"];

const priorityColor = (p) => ({
  Low: "bg-gray-100 text-gray-600",
  Medium: "bg-blue-100 text-blue-700",
  High: "bg-orange-100 text-orange-700",
  Critical: "bg-red-100 text-red-700",
}[p] || "");

const statusColor = (s) => ({
  Open: "bg-green-100 text-green-700",
  "In Progress": "bg-yellow-100 text-yellow-700",
  "Waiting on Customer": "bg-purple-100 text-purple-700",
  Resolved: "bg-blue-100 text-blue-700",
  Closed: "bg-gray-100 text-gray-500",
}[s] || "");

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [devices, setDevices] = useState([]);
  const [selected, setSelected] = useState(null);
  const [notes, setNotes] = useState([]);
  const [history, setHistory] = useState([]);
  const [newNote, setNewNote] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ title: "", description: "", status: "Open", priority: "Medium", customer_id: "", device_id: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [actionError, setActionError] = useState(null);
  const [detailError, setDetailError] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [noteSaving, setNoteSaving] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [t, c, d] = await Promise.all([
        api.get("/tickets"),
        api.get("/customers"),
        api.get("/devices"),
      ]);
      setTickets(t);
      setCustomers(c);
      setDevices(d);
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  const loadDetail = async (t) => {
    setSelected(t);
    setDetailError(null);
    setDetailLoading(true);
    setNotes([]);
    setHistory([]);
    try {
      const [ticketNotes, ticketHistory] = await Promise.all([
        api.get(`/tickets/${t.id}/notes`),
        api.get(`/tickets/${t.id}/history`),
      ]);
      setNotes(ticketNotes);
      setHistory(ticketHistory);
    } catch (e) {
      setDetailError(e.message || String(e));
    } finally {
      setDetailLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <LoadingState message="Loading tickets…" />;
  if (error) return <ErrorState error={error} onRetry={load} />;

  const handleSubmit = async () => {
    setActionError(null);
    if (!form.title.trim()) {
      setActionError("Title is required.");
      return;
    }

    setSaving(true);
    try {
      if (editing) {
        await api.put(`/tickets/${editing}`, form);
      } else {
        await api.post("/tickets", form);
      }
      setForm({ title: "", description: "", status: "Open", priority: "Medium", customer_id: "", device_id: "" });
      setEditing(null);
      setShowForm(false);
      await load();
    } catch (e) {
      setActionError(e.message || String(e));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (t) => {
    setForm({ title: t.title, description: t.description || "", status: t.status, priority: t.priority, customer_id: t.customer_id || "", device_id: t.device_id || "" });
    setEditing(t.id);
    setActionError(null);
    setShowForm(true);
    setSelected(null);
  };

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    setDetailError(null);
    setNoteSaving(true);
    try {
      await api.post("/notes", { ticket_id: selected.id, note_text: newNote, created_by: "Agent" });
      setNewNote("");
      setNotes(await api.get(`/tickets/${selected.id}/notes`));
    } catch (e) {
      setDetailError(e.message || String(e));
    } finally {
      setNoteSaving(false);
    }
  };

  const getName = (arr, id) => arr.find(x => x.id === id)?.name || "—";
  const normalizedQuery = query.trim().toLowerCase();
  const filteredTickets = tickets.filter((ticket) => {
    const customer = customers.find((item) => item.id === ticket.customer_id);
    const device = devices.find((item) => item.id === ticket.device_id);
    const searchable = [
      ticket.title,
      ticket.description,
      customer?.name,
      device?.serial_number,
      device?.model,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return (
      (!normalizedQuery || searchable.includes(normalizedQuery)) &&
      (!statusFilter || ticket.status === statusFilter) &&
      (!priorityFilter || ticket.priority === priorityFilter)
    );
  });

  if (selected) return (
    <div>
      <button onClick={() => setSelected(null)} className="text-blue-600 hover:underline mb-4 text-sm">← Back to Tickets</button>
      <InlineError error={detailError} />
      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-1">{selected.title}</h2>
            <p className="text-gray-500 text-sm mb-3">{selected.description || "No description"}</p>
            <div className="flex gap-2">
              <span className={`whitespace-nowrap text-xs px-2 py-1 rounded-full font-medium ${statusColor(selected.status)}`}>{selected.status}</span>
              <span className={`whitespace-nowrap text-xs px-2 py-1 rounded-full font-medium ${priorityColor(selected.priority)}`}>{selected.priority}</span>
            </div>
          </div>
          <button onClick={() => handleEdit(selected)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">Edit Ticket</button>
        </div>
        <div className="mt-4 grid grid-cols-1 gap-4 text-sm text-gray-600 sm:grid-cols-2">
          <p><span className="font-medium">Customer:</span> {getName(customers, selected.customer_id)}</p>
          <p><span className="font-medium">Device:</span> {devices.find(d => d.id === selected.device_id)?.serial_number || "—"}</p>
        </div>
      </div>

      {/* AI Suggestions */}
      {selected && <AISuggestions ticketId={selected.id} />}

      {/* Notes */}
      <div className="bg-white rounded-lg shadow p-6 mb-4">
        <h3 className="font-semibold mb-3">Notes</h3>
        {detailLoading ? <p className="text-gray-400 text-sm">Loading notes…</p> : notes.length === 0 ? <p className="text-gray-400 text-sm">No notes yet</p> : notes.map(n => (
          <div key={n.id} className="border-b py-3 text-sm">
            <p>{n.note_text}</p>
            <p className="text-gray-400 text-xs mt-1">{n.created_by} · {new Date(n.created_at).toLocaleString()}</p>
          </div>
        ))}
        <div className="mt-4 flex gap-2">
          <input disabled={noteSaving} className="min-w-0 flex-1 border rounded px-3 py-2 text-sm disabled:bg-gray-100" placeholder="Add a note..."
            value={newNote} onChange={e => setNewNote(e.target.value)} />
          <button disabled={noteSaving || !newNote.trim()} onClick={handleAddNote} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm disabled:cursor-not-allowed disabled:opacity-50">
            {noteSaving ? "Adding…" : "Add"}
          </button>
        </div>
      </div>

      {/* History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold mb-3">Status History</h3>
        {detailLoading ? <p className="text-gray-400 text-sm">Loading history…</p> : history.length === 0 ? <p className="text-gray-400 text-sm">No history yet</p> : history.map(h => (
          <div key={h.id} className="border-b py-2 text-sm flex gap-2 items-center">
            <span className={`whitespace-nowrap px-2 py-0.5 rounded-full text-xs ${statusColor(h.old_status)}`}>{h.old_status}</span>
            <span className="text-gray-400">→</span>
            <span className={`whitespace-nowrap px-2 py-0.5 rounded-full text-xs ${statusColor(h.new_status)}`}>{h.new_status}</span>
            <span className="text-gray-400 text-xs ml-auto">{new Date(h.changed_at).toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold">Tickets</h2>
        <button onClick={() => { setShowForm(!showForm); setEditing(null); setActionError(null); setForm({ title: "", description: "", status: "Open", priority: "Medium", customer_id: "", device_id: "" }); }}
          className="self-start bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 sm:self-auto">
          {showForm ? "Cancel" : "+ New Ticket"}
        </button>
      </div>

      <InlineError error={actionError} />

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-semibold mb-4">{editing ? "Edit Ticket" : "New Ticket"}</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="text-sm text-gray-600">Title *</label>
              <input className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.title}
                onChange={e => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="md:col-span-2">
              <label className="text-sm text-gray-600">Description</label>
              <textarea className="w-full border rounded px-3 py-2 mt-1 text-sm" rows={3} value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">Status</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.status}
                onChange={e => setForm({ ...form, status: e.target.value })}>
                {STATUSES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">Priority</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.priority}
                onChange={e => setForm({ ...form, priority: e.target.value })}>
                {PRIORITIES.map(p => <option key={p}>{p}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">Customer</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.customer_id}
                onChange={e => setForm({ ...form, customer_id: e.target.value })}>
                <option value="">— None —</option>
                {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">Device</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.device_id}
                onChange={e => setForm({ ...form, device_id: e.target.value })}>
                <option value="">— None —</option>
                {devices.map(d => <option key={d.id} value={d.id}>{d.serial_number} — {d.model}</option>)}
              </select>
            </div>
          </div>
          <button onClick={handleSubmit} disabled={saving} className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50">
            {saving ? "Saving…" : editing ? "Update" : "Create"}
          </button>
        </div>
      )}

      <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_180px_160px]">
        <div>
          <label htmlFor="ticket-search" className="sr-only">Search tickets</label>
          <input
            id="ticket-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search tickets, customers, or devices"
            className="w-full border bg-white px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="ticket-status-filter" className="sr-only">Filter by status</label>
          <select
            id="ticket-status-filter"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value)}
            className="w-full border bg-white px-3 py-2 text-sm"
          >
            <option value="">All statuses</option>
            {STATUSES.map((status) => <option key={status}>{status}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="ticket-priority-filter" className="sr-only">Filter by priority</label>
          <select
            id="ticket-priority-filter"
            value={priorityFilter}
            onChange={(event) => setPriorityFilter(event.target.value)}
            className="w-full border bg-white px-3 py-2 text-sm"
          >
            <option value="">All priorities</option>
            {PRIORITIES.map((priority) => <option key={priority}>{priority}</option>)}
          </select>
        </div>
      </div>

      <p className="mb-2 text-xs text-gray-500" aria-live="polite">
        Showing {filteredTickets.length} of {tickets.length} tickets
      </p>

      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full min-w-[680px] text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              {["Title", "Status", "Priority", "Customer", "Actions"].map(h => (
                <th key={h} className="px-4 py-3 text-left">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredTickets.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-gray-400">
                  {tickets.length === 0 ? "No tickets yet" : "No tickets match these filters"}
                </td>
              </tr>
            ) : filteredTickets.map(t => (
              <tr key={t.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{t.title}</td>
                <td className="px-4 py-3"><span className={`whitespace-nowrap text-xs px-2 py-1 rounded-full font-medium ${statusColor(t.status)}`}>{t.status}</span></td>
                <td className="px-4 py-3"><span className={`whitespace-nowrap text-xs px-2 py-1 rounded-full font-medium ${priorityColor(t.priority)}`}>{t.priority}</span></td>
                <td className="px-4 py-3 text-gray-600">{getName(customers, t.customer_id)}</td>
                <td className="px-4 py-3">
                  <button onClick={() => loadDetail(t)} className="text-blue-600 hover:underline">View</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
