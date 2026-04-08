import { useEffect, useState } from "react";
import { api } from "../api";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [form, setForm] = useState({ name: "", email: "", phone: "", company: "" });
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const load = () => api.get("/customers").then(setCustomers);

  useEffect(() => { load(); }, []);

  const handleSubmit = async () => {
    if (!form.name) return alert("Name is required");
    if (editing) {
      await api.put(`/customers/${editing}`, form);
    } else {
      await api.post("/customers", form);
    }
    setForm({ name: "", email: "", phone: "", company: "" });
    setEditing(null);
    setShowForm(false);
    load();
  };

  const handleEdit = (c) => {
    setForm({ name: c.name, email: c.email || "", phone: c.phone || "", company: c.company || "" });
    setEditing(c.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this customer?")) return;
    await api.delete(`/customers/${id}`);
    load();
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Customers</h2>
        <button
          onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ name: "", email: "", phone: "", company: "" }); }}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "+ New Customer"}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="font-semibold mb-4">{editing ? "Edit Customer" : "New Customer"}</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Name *", key: "name" },
              { label: "Email", key: "email" },
              { label: "Phone", key: "phone" },
              { label: "Company", key: "company" },
            ].map(({ label, key }) => (
              <div key={key}>
                <label className="text-sm text-gray-600">{label}</label>
                <input
                  className="w-full border rounded px-3 py-2 mt-1 text-sm"
                  value={form[key]}
                  onChange={e => setForm({ ...form, [key]: e.target.value })}
                />
              </div>
            ))}
          </div>
          <button
            onClick={handleSubmit}
            className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
          >
            {editing ? "Update" : "Create"}
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
            <tr>
              {["Name", "Email", "Phone", "Company", "Actions"].map(h => (
                <th key={h} className="px-4 py-3 text-left">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {customers.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-400">No customers yet</td></tr>
            ) : customers.map(c => (
              <tr key={c.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{c.name}</td>
                <td className="px-4 py-3 text-gray-600">{c.email || "—"}</td>
                <td className="px-4 py-3 text-gray-600">{c.phone || "—"}</td>
                <td className="px-4 py-3 text-gray-600">{c.company || "—"}</td>
                <td className="px-4 py-3 flex gap-2">
                  <button onClick={() => handleEdit(c)} className="text-blue-600 hover:underline">Edit</button>
                  <button onClick={() => handleDelete(c.id)} className="text-red-500 hover:underline">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
