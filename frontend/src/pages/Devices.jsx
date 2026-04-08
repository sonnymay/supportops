import { useEffect, useState } from "react";
import { api } from "../api";

export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [form, setForm] = useState({ serial_number: "", model: "", product_type: "", customer_id: "" });
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const load = () => {
    api.get("/devices").then(setDevices);
    api.get("/customers").then(setCustomers);
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async () => {
    if (!form.serial_number) return alert("Serial number is required");
    if (editing) {
      await api.put(`/devices/${editing}`, form);
    } else {
      await api.post("/devices", form);
    }
    setForm({ serial_number: "", model: "", product_type: "", customer_id: "" });
    setEditing(null);
    setShowForm(false);
    load();
  };

  const handleEdit = (d) => {
    setForm({ serial_number: d.serial_number, model: d.model || "", product_type: d.product_type || "", customer_id: d.customer_id || "" });
    setEditing(d.id);
    setShowForm(true);
  };

  const getCustomerName = (id) => customers.find(c => c.id === id)?.name || "—";

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Devices</h2>
        <button
          onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ serial_number: "", model: "", product_type: "", customer_id: "" }); }}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "+ New Device"}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-semibold mb-4">{editing ? "Edit Device" : "New Device"}</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-600">Serial Number *</label>
              <input className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.serial_number}
                onChange={e => setForm({ ...form, serial_number: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">Model</label>
              <input className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.model}
                onChange={e => setForm({ ...form, model: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">Product Type</label>
              <input className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.product_type}
                onChange={e => setForm({ ...form, product_type: e.target.value })} />
            </div>
            <div>
              <label className="text-sm text-gray-600">Customer</label>
              <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.customer_id}
                onChange={e => setForm({ ...form, customer_id: e.target.value })}>
                <option value="">— None —</option>
                {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
          </div>
          <button onClick={handleSubmit}
            className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">
            {editing ? "Update" : "Create"}
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              {["Serial Number", "Model", "Product Type", "Customer", "Actions"].map(h => (
                <th key={h} className="px-4 py-3 text-left">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {devices.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-400">No devices yet</td></tr>
            ) : devices.map(d => (
              <tr key={d.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 font-mono font-medium">{d.serial_number}</td>
                <td className="px-4 py-3 text-gray-600">{d.model || "—"}</td>
                <td className="px-4 py-3 text-gray-600">{d.product_type || "—"}</td>
                <td className="px-4 py-3 text-gray-600">{getCustomerName(d.customer_id)}</td>
                <td className="px-4 py-3">
                  <button onClick={() => handleEdit(d)} className="text-blue-600 hover:underline mr-2">Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
