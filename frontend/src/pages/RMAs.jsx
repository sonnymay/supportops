import { useEffect, useState } from "react";
import { api } from "../api";

export default function RMAs() {
  const [rmas, setRmas] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [form, setForm] = useState({ ticket_id: "", rma_number: "", serial_number: "", shipping_status: "Pending", resolution_status: "Pending" });
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);

  const load = () => {
    api.get("/rmas").then(setRmas);
    api.get("/tickets").then(setTickets);
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async () => {
    if (!form.ticket_id) return alert("Ticket is required");
    if (!form.rma_number) return alert("RMA number is required");
    if (editing) {
      await api.put(`/rmas/${editing}`, form);
    } else {
      await api.post("/rmas", form);
    }
    setForm({ ticket_id: "", rma_number: "", serial_number: "", shipping_status: "Pending", resolution_status: "Pending" });
    setEditing(null);
    setShowForm(false);
    load();
  };

  const handleEdit = (r) => {
    setForm({ ticket_id: r.ticket_id, rma_number: r.rma_number, serial_number: r.serial_number || "", shipping_status: r.shipping_status, resolution_status: r.resolution_status });
    setEditing(r.id);
    setShowForm(true);
  };

  const getTicketTitle = (id) => tickets.find(t => t.id === id)?.title || "—";

  const statusColor = (s) => s === "Pending" ? "bg-yellow-100 text-yellow-700" : s === "Completed" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600";

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">RMAs</h2>
        <button onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ ticket_id: "", rma_number: "", serial_number: "", shipping_status: "Pending", resolution_status: "Pending" }); }}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          {showForm ? "Cancel" : "+ New RMA"}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-semibold mb-4">{editing ? "Edit RMA" : "New RMA"}</h3>
          <div className="grid grid-cols-2 gap-4">
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
                {["Pending", "Shipped", "Delivered", "Returned"].map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-600">Resolution Status</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.resolution_status}
                onChange={e => setForm({ ...form, resolution_status: e.target.value })}>
                {["Pending", "In Progress", "Completed", "Cancelled"].map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <button onClick={handleSubmit} className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">
            {editing ? "Update" : "Create"}
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              {["RMA Number", "Ticket", "Serial Number", "Shipping", "Resolution", "Actions"].map(h => (
                <th key={h} className="px-4 py-3 text-left">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rmas.length === 0 ? (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-400">No RMAs yet</td></tr>
            ) : rmas.map(r => (
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 font-mono font-medium">{r.rma_number}</td>
                <td className="px-4 py-3 text-gray-600">{getTicketTitle(r.ticket_id)}</td>
                <td className="px-4 py-3 text-gray-600">{r.serial_number || "—"}</td>
                <td className="px-4 py-3"><span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor(r.shipping_status)}`}>{r.shipping_status}</span></td>
                <td className="px-4 py-3"><span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor(r.resolution_status)}`}>{r.resolution_status}</span></td>
                <td className="px-4 py-3">
                  <button onClick={() => handleEdit(r)} className="text-blue-600 hover:underline">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
