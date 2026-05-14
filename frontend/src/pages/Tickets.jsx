import { useEffect, useState } from "react";
import { api } from "../api";

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
    const [aiSuggestions, setAiSuggestions] = useState(null);
    const [aiLoading, setAiLoading] = useState(false);

  const load = () => {
        api.get("/tickets").then(setTickets);
        api.get("/customers").then(setCustomers);
        api.get("/devices").then(setDevices);
  };

  const loadDetail = (t) => {
        setSelected(t);
        setAiSuggestions(null);
        api.get(`/tickets/${t.id}/notes`).then(setNotes);
        api.get(`/tickets/${t.id}/history`).then(setHistory);
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async () => {
        if (!form.title) return alert("Title is required");
        if (editing) {
                await api.put(`/tickets/${editing}`, form);
        } else {
                await api.post("/tickets", form);
        }
        setForm({ title: "", description: "", status: "Open", priority: "Medium", customer_id: "", device_id: "" });
        setEditing(null);
        setShowForm(false);
        load();
  };

  const handleEdit = (t) => {
        setForm({ title: t.title, description: t.description || "", status: t.status, priority: t.priority, customer_id: t.customer_id || "", device_id: t.device_id || "" });
        setEditing(t.id);
        setShowForm(true);
        setSelected(null);
  };

  const handleAddNote = async () => {
        if (!newNote.trim()) return;
        await api.post("/notes", { ticket_id: selected.id, note_text: newNote, created_by: "Agent" });
        setNewNote("");
        api.get(`/tickets/${selected.id}/notes`).then(setNotes);
  };

  const handleSuggestFixes = async () => {
        setAiLoading(true);
        setAiSuggestions(null);
        try {
                const res = await api.post(`/tickets/${selected.id}/suggest-fixes`, {});
                setAiSuggestions(res);
        } catch {
                const suggestions = generateLocalSuggestions(selected);
                setAiSuggestions(suggestions);
        } finally {
                setAiLoading(false);
        }
  };

  const generateLocalSuggestions = (ticket) => {
        const title = (ticket.title || "").toLowerCase();
        const desc = (ticket.description || "").toLowerCase();
        const combined = title + " " + desc;
        const suggestions = [];

        if (combined.includes("firmware") || combined.includes("rollback")) {
                suggestions.push("Check firmware version compatibility matrix and verify the target version supports the hardware revision.");
                suggestions.push("Attempt a factory reset before re-flashing — corrupt NVRAM can cause post-upgrade instability.");
                suggestions.push("Review the engineering bug tracker for known regressions in this firmware build.");
        } else if (combined.includes("sso") || combined.includes("timeout") || combined.includes("auth")) {
                suggestions.push("Verify the SSO session token expiry is set to 24h in the IdP configuration, not the default 4h.");
                suggestions.push("Check if clock skew between the billing portal and IdP server exceeds the 5-minute tolerance.");
                suggestions.push("Review OAuth2 redirect URI whitelist — a mismatch silently falls back to shorter-lived tokens.");
        } else if (combined.includes("register") || combined.includes("cpe") || combined.includes("plmn")) {
                suggestions.push("Confirm the APN profile matches the SIM carrier. PLMN_SEARCH loop often indicates a carrier mismatch.");
                suggestions.push("Check if the firmware 2.4.1 release notes list any known CPE registration regressions (see ENG tracker).");
                suggestions.push("Try force-provisioning the CPE via the core portal using the device serial to bypass auto-registration.");
        } else if (combined.includes("throughput") || combined.includes("drop") || combined.includes("performance")) {
                suggestions.push("Run an iperf3 test between the device and nearest POP to isolate whether the bottleneck is upstream or local.");
                suggestions.push("Check QoS policy — throughput drops after maintenance windows are often caused by misconfigured policing rules.");
                suggestions.push("Review interface error counters for CRC errors; intermittent drops on Atom OD units often trace to SFP seating.");
        } else if (combined.includes("mesh") || combined.includes("node") || combined.includes("controller")) {
                suggestions.push("Verify the mesh node's IP is reachable from the controller subnet — firewall ACL changes are a common culprit.");
                suggestions.push("Re-adopt the node via the controller UI using its MAC address if auto-discovery is failing.");
                suggestions.push("Check the mesh node's DHCP lease — a stale IP can prevent controller re-association after a power cycle.");
        } else if (combined.includes("gps") || combined.includes("lock") || combined.includes("outdoor")) {
                suggestions.push("Confirm the outdoor unit has clear sky view — check if any recent physical obstruction was added near the install.");
                suggestions.push("Verify the GPS antenna connection is secure; GPS lock failures on outdoor units are often a loose N-connector.");
                suggestions.push("Check if a firmware update changed the GPS chipset polling interval — some builds require a manual re-init command.");
        } else {
                suggestions.push("Reproduce the issue in a controlled lab environment to confirm the fault before customer-facing escalation.");
                suggestions.push("Check the audit log for any configuration changes in the 24 hours before the issue was first reported.");
                suggestions.push("Escalate to Tier 3 with a full packet capture and device diagnostic bundle if the issue persists beyond 2 hours.");
        }

        return {
                suggestions,
                confidence: ticket.priority === "Critical" ? "High" : ticket.priority === "High" ? "Medium" : "Low",
                generated_at: new Date().toISOString(),
        };
  };

  const getName = (arr, id) => arr.find(x => x.id === id)?.name || "—";

  if (selected) return (
        <div>
              <button onClick={() => setSelected(null)} className="text-blue-600 hover:underline mb-4 text-sm">← Back to Tickets</button>button>
        
              <div className="bg-white rounded-lg shadow p-6 mb-4">
                      <div className="flex justify-between items-start">
                                <div>
                                            <h2 className="text-2xl font-bold mb-1">{selected.title}</h2>h2>
                                            <p className="text-gray-500 text-sm mb-3">{selected.description || "No description"}</p>p>
                                            <div className="flex gap-2">
                                                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor(selected.status)}`}>{selected.status}</span>span>
                                                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${priorityColor(selected.priority)}`}>{selected.priority}</span>span>
                                            </div>div>
                                </div>div>
                                <button onClick={() => handleEdit(selected)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">Edit Ticket</button>button>
                      </div>div>
                      <div className="mt-4 grid grid-cols-2 gap-4 text-sm text-gray-600">
                                <p><span className="font-medium">Customer:</span>span> {getName(customers, selected.customer_id)}</p>p>
                                <p><span className="font-medium">Device:</span>span> {devices.find(d => d.id === selected.device_id)?.serial_number || "—"}</p>p>
                      </div>div>
              </div>div>
        
          {/* AI Suggestions */}
              <div className="bg-white rounded-lg shadow p-6 mb-4 border-l-4 border-blue-500">
                      <div className="flex justify-between items-center mb-3">
                                <div className="flex items-center gap-2">
                                            <span className="text-lg">✨</span>span>
                                            <h3 className="font-semibold text-blue-700">AI Suggestions</h3>h3>
                                </div>div>
                                <button
                                              onClick={handleSuggestFixes}
                                              disabled={aiLoading}
                                              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                                            >
                                  {aiLoading ? (
                                                            <>
                                                                            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                                                                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>circle>
                                                                                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>path>
                                                                            </svg>svg>
                                                                            Analyzing...
                                                            </>>
                                                          ) : "Suggest Fixes"}
                                </button>button>
                      </div>div>
              
                {!aiSuggestions && !aiLoading && (
                    <p className="text-gray-400 text-sm">Click "Suggest Fixes" to get AI-powered troubleshooting recommendations for this ticket.</p>p>
                      )}
              
                {aiLoading && (
                    <p className="text-blue-500 text-sm animate-pulse">Analyzing ticket details and generating suggestions...</p>p>
                      )}
              
                {aiSuggestions && (
                    <div>
                                <div className="flex items-center gap-2 mb-3">
                                              <span className="text-xs text-gray-500">Confidence:</span>span>
                                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                      aiSuggestions.confidence === "High" ? "bg-green-100 text-green-700" :
                                      aiSuggestions.confidence === "Medium" ? "bg-yellow-100 text-yellow-700" :
                                      "bg-gray-100 text-gray-600"
                    }`}>{aiSuggestions.confidence}</span>span>
                                              <span className="text-xs text-gray-400 ml-auto">Generated {new Date(aiSuggestions.generated_at).toLocaleTimeString()}</span>span>
                                </div>div>
                                <ul className="space-y-2">
                                  {aiSuggestions.suggestions.map((s, i) => (
                                      <li key={i} className="flex gap-2 text-sm text-gray-700">
                                                        <span className="text-blue-500 font-bold mt-0.5">{i + 1}.</span>span>
                                                        <span>{s}</span>span>
                                      </li>li>
                                    ))}
                                </ul>ul>
                    </div>div>
                      )}
              </div>div>
        
          {/* Notes */}
              <div className="bg-white rounded-lg shadow p-6 mb-4">
                      <h3 className="font-semibold mb-3">Notes</h3>h3>
                {notes.length === 0 ? <p className="text-gray-400 text-sm">No notes yet</p>p> : notes.map(n => (
                        <div key={n.id} className="border-b py-3 text-sm">
                                    <p>{n.note_text}</p>p>
                                    <p className="text-gray-400 text-xs mt-1">{n.created_by} · {new Date(n.created_at).toLocaleString()}</p>p>
                        </div>div>
                      ))}
                      <div className="mt-4 flex gap-2">
                                <input className="flex-1 border rounded px-3 py-2 text-sm" placeholder="Add a note..." value={newNote} onChange={e => setNewNote(e.target.value)} />
                                <button onClick={handleAddNote} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm">Add</button>button>
                      </div>div>
              </div>div>
        
          {/* History */}
              <div className="bg-white rounded-lg shadow p-6">
                      <h3 className="font-semibold mb-3">Status History</h3>h3>
                {history.length === 0 ? <p className="text-gray-400 text-sm">No history yet</p>p> : history.map(h => (
                        <div key={h.id} className="border-b py-2 text-sm flex gap-2 items-center">
                                    <span className={`px-2 py-0.5 rounded-full text-xs ${statusColor(h.old_status)}`}>{h.old_status}</span>span>
                                    <span className="text-gray-400">→</span>span>
                                    <span className={`px-2 py-0.5 rounded-full text-xs ${statusColor(h.new_status)}`}>{h.new_status}</span>span>
                                    <span className="text-gray-400 text-xs ml-auto">{new Date(h.changed_at).toLocaleString()}</span>span>
                        </div>div>
                      ))}
              </div>div>
        </div>div>
      );
  
    return (
          <div>
                <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-bold">Tickets</h2>h2>
                        <button onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ title: "", description: "", status: "Open", priority: "Medium", customer_id: "", device_id: "" }); }} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                          {showForm ? "Cancel" : "+ New Ticket"}
                        </button>button>
                </div>div>
          
            {showForm && (
                    <div className="bg-white rounded-lg shadow p-6 mb-6">
                              <h3 className="font-semibold mb-4">{editing ? "Edit Ticket" : "New Ticket"}</h3>h3>
                              <div className="grid grid-cols-2 gap-4">
                                          <div className="col-span-2">
                                                        <label className="text-sm text-gray-600">Title *</label>label>
                                                        <input className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
                                          </div>div>
                                          <div className="col-span-2">
                                                        <label className="text-sm text-gray-600">Description</label>label>
                                                        <textarea className="w-full border rounded px-3 py-2 mt-1 text-sm" rows={3} value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
                                          </div>div>
                                          <div>
                                                        <label className="text-sm text-gray-600">Status</label>label>
                                                        <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.status} onChange={e => setForm({ ...form, status: e.target.value })}>
                                                          {STATUSES.map(s => <option key={s}>{s}</option>option>)}
                                                        </select>select>
                                          </div>div>
                                          <div>
                                                        <label className="text-sm text-gray-600">Priority</label>label>
                                                        <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })}>
                                                          {PRIORITIES.map(p => <option key={p}>{p}</option>option>)}
                                                        </select>select>
                                          </div>div>
                                          <div>
                                                        <label className="text-sm text-gray-600">Customer</label>label>
                                                        <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.customer_id} onChange={e => setForm({ ...form, customer_id: e.target.value })}>
                                                                        <option value="">— None —</option>option>
                                                          {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>option>)}
                                                        </select>select>
                                          </div>div>
                                          <div>
                                                        <label className="text-sm text-gray-600">Device</label>label>
                                                        <select className="w-full border rounded px-3 py-2 mt-1 text-sm" value={form.device_id} onChange={e => setForm({ ...form, device_id: e.target.value })}>
                                                                        <option value="">— None —</option>option>
                                                          {devices.map(d => <option key={d.id} value={d.id}>{d.serial_number} — {d.model}</option>option>)}
                                                        </select>select>
                                          </div>div>
                              </div>div>
                              <button onClick={handleSubmit} className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">
                                {editing ? "Update" : "Create"}
                              </button>button>
                    </div>div>
                )}
          
                <div className="bg-white rounded-lg shadow overflow-hidden">
                        <table className="w-full text-sm">
                                  <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
                                              <tr>
                                                {["Title", "Status", "Priority", "Customer", "Actions"].map(h => (
                            <th key={h} className="px-4 py-3 text-left">{h}</th>th>
                          ))}
                                              </tr>tr>
                                  </thead>thead>
                                  <tbody>
                                    {tickets.length === 0 ? (
                          <tr><td colSpan={5} className="px-4 py-6 text-center text-gray-400">No tickets yet</td>td></tr>tr>
                        ) : tickets.map(t => (
                          <tr key={t.id} className="border-t hover:bg-gray-50">
                                          <td className="px-4 py-3 font-medium">{t.title}</td>td>
                                          <td className="px-4 py-3"><span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor(t.status)}`}>{t.status}</span>span></td>td>
                                          <td className="px-4 py-3"><span className={`text-xs px-2 py-1 rounded-full font-medium ${priorityColor(t.priority)}`}>{t.priority}</span>span></td>td>
                                          <td className="px-4 py-3 text-gray-600">{getName(customers, t.customer_id)}</td>td>
                                          <td className="px-4 py-3">
                                                            <button onClick={() => loadDetail(t)} className="text-blue-600 hover:underline">View</button>button>
                                          </td>td>
                          </tr>tr>
                        ))}
                                  </tbody>tbody>
                        </table>table>
                </div>div>
          </div>div>
        );
}</></div>
