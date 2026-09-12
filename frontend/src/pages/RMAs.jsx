import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { LoadingState, ErrorState, InlineError } from "../components/AsyncState";

const SHIPPING_STATUSES = ["Pending", "Shipped", "Delivered", "Returned"];
const RESOLUTION_STATUSES = ["Pending", "In Progress", "Completed", "Cancelled"];

export default function RMAs() {
  const [rmas, setRmas] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [form, setForm] = useState({ ticket_id: "", rma_number: "", serial_number: "", shipping_status: "Pending", resolution_status: "Pending" });
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [r, t] = await Promise.all([api.get("/rmas"), api.get("/tickets")]);
      setRmas(r);
      setTickets(t);
    } catch (e) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) return <LoadingState message="Loading RMAs…" />;
  if (error) return <ErrorState error={error} onRetry={load} />;

  const handleSubmit = async () => {
    setActionError(null);
    if (!form.ticket_id) {
      setActionError("Ticket is required.");
      return;
    }
    if (!form.rma_number.trim()) {
      setActionError("RMA number is required.");
      return;
    }

    setSaving(true);
    try {
      if (editing) {
        await api.put(`/rmas/${editing}`, form);
      } else {
        await api.post("/rmas", form);
      }
      setForm({ ticket_id: "", rma_number: "", serial_number: "", shipping_status: "Pending", resolution_status: "Pending" });
      setEditing(null);
      setShowForm(false);
      await load();
    } catch (e) {
      setActionError(e.message || String(e));
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (r) => {
    setForm({ ticket_id: r.ticket_id, rma_number: r.rma_number, serial_number: r.serial_number || "", shipping_status: r.shipping_status, resolution_status: r.resolution_status });
    setEditing(r.id);
    setActionError(null);
    setShowForm(true);
  };

  const getTicketTitle = (id) => tickets.find(t => t.id === id)?.title || "—";

  const statusColor = (s) => s === "Pending" ? "bg-yellow-100 text-yellow-700" : s === "Completed" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600";
  const shippingStatuses = [...new Set([...SHIPPING_STATUSES, ...rmas.map((rma) => rma.shipping_status).filter(Boolean)])];
  const resolutionStatuses = [...new Set([...RESOLUTION_STATUSES, ...rmas.map((rma) => rma.resolution_status).filter(Boolean)])];
  const query = searchParams.get("q") || "";
  const shippingFilter = shippingStatuses.includes(searchParams.get("shipping")) ? searchParams.get("shipping") : "";
  const resolutionFilter = resolutionStatuses.includes(searchParams.get("resolution")) ? searchParams.get("resolution") : "";
  const hasActiveFilters = Boolean(query || shippingFilter || resolutionFilter);
  const updateFilter = (key, value) => {
    setSearchParams((current) => {
      const next = new URLSearchParams(current);
      if (value) next.set(key, value);
      else next.delete(key);
      return next;
    }, { replace: true });
  };
  const normalizedQuery = query.trim().toLowerCase();
  const filteredRmas = rmas.filter((rma) => {
    const ticket = tickets.find((item) => item.id === rma.ticket_id);
    const searchable = [rma.rma_number, rma.serial_number, ticket?.title]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();

    return (
      (!normalizedQuery || searchable.includes(normalizedQuery)) &&
      (!shippingFilter || rma.shipping_status === shippingFilter) &&
      (!resolutionFilter || rma.resolution_status === resolutionFilter)
    );
  });

  return (
    <div>
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-2xl font-bold">RMAs</h2>
        <button onClick={() => { setShowForm(!showForm); setEditing(null); setActionError(null); setForm({ ticket_id: "", rma_number: "", serial_number: "", shipping_status: "Pending", resolution_status: "Pending" }); }}
          className="self-start bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 sm:self-auto">
          {showForm ? "Cancel" : "+ New RMA"}
        </button>
      </div>

      <InlineError error={actionError} />

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-semibold mb-4">{editing ? "Edit RMA" : "New RMA"}</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="text-sm text-gray-600">Ticket *</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.ticket_id}
                onChange={e => setForm({ ...form, ticket_id: e.target.value })}>
                <option value="">— Select Ticket —</option>
                {tickets.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">RMA Number *</label>
              <input className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.rma_number}
                onChange={e => setForm({ ...form, rma_number: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">Serial Number</label>
              <input className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.serial_number}
                onChange={e => setForm({ ...form, serial_number: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">Shipping Status</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.shipping_status}
                onChange={e => setForm({ ...form, shipping_status: e.target.value })}>
                {shippingStatuses.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">Resolution Status</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.resolution_status}
                onChange={e => setForm({ ...form, resolution_status: e.target.value })}>
                {resolutionStatuses.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <button onClick={handleSubmit} disabled={saving} className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50">
            {saving ? "Saving…" : editing ? "Update" : "Create"}
          </button>
        </div>
      )}

      <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-[minmax(0,1fr)_180px_180px_auto]">
        <div>
          <label htmlFor="rma-search" className="sr-only">Search RMAs</label>
          <input
            id="rma-search"
            type="search"
            value={query}
            onChange={(event) => updateFilter("q", event.target.value)}
            placeholder="Search RMA numbers, serial numbers, or tickets"
            className="w-full border bg-white px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="rma-shipping-filter" className="sr-only">Filter by shipping status</label>
          <select
            id="rma-shipping-filter"
            value={shippingFilter}
            onChange={(event) => updateFilter("shipping", event.target.value)}
            className="w-full border bg-white px-3 py-2 text-sm"
          >
            <option value="">All shipping</option>
            {shippingStatuses.map((status) => <option key={status}>{status}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="rma-resolution-filter" className="sr-only">Filter by resolution status</label>
          <select
            id="rma-resolution-filter"
            value={resolutionFilter}
            onChange={(event) => updateFilter("resolution", event.target.value)}
            className="w-full border bg-white px-3 py-2 text-sm"
          >
            <option value="">All resolutions</option>
            {resolutionStatuses.map((status) => <option key={status}>{status}</option>)}
          </select>
        </div>
        <button
          type="button"
          disabled={!hasActiveFilters}
          onClick={() => setSearchParams({}, { replace: true })}
          className="border bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Clear filters
        </button>
      </div>

      <p className="mb-2 text-xs text-gray-500" aria-live="polite">
        Showing {filteredRmas.length} of {rmas.length} RMAs
      </p>

      <div className="bg-white rounded-lg shadow overflow-x-auto">
        <table className="w-full min-w-[820px] text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              {["RMA Number", "Ticket", "Serial Number", "Shipping", "Resolution", "Actions"].map(h => (
                <th key={h} className="px-4 py-3 text-left">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredRmas.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-gray-400">
                  {rmas.length === 0 ? "No RMAs yet" : "No RMAs match these filters"}
                </td>
              </tr>
            ) : filteredRmas.map(r => (
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 font-mono font-medium">{r.rma_number}</td>
                <td className="px-4 py-3 text-gray-600">{getTicketTitle(r.ticket_id)}</td>
                <td className="px-4 py-3 text-gray-600">{r.serial_number || "—"}</td>
                <td className="px-4 py-3"><span className={`whitespace-nowrap text-xs px-2 py-1 rounded-full font-medium ${statusColor(r.shipping_status)}`}>{r.shipping_status}</span></td>
                <td className="px-4 py-3"><span className={`whitespace-nowrap text-xs px-2 py-1 rounded-full font-medium ${statusColor(r.resolution_status)}`}>{r.resolution_status}</span></td>
                <td className="px-4 py-3">
                  <button disabled={saving} onClick={() => handleEdit(r)} className="text-blue-600 hover:underline disabled:opacity-50">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
