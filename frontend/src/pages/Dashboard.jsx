import { useEffect, useState } from "react";
import { api } from "../api";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => { api.get("/dashboard").then(setStats); }, []);

  if (!stats) return <p>Loading...</p>;

  const cards = [
    { label: "Open Tickets", value: stats.open_tickets, color: "bg-blue-500" },
    { label: "In Progress", value: stats.in_progress, color: "bg-yellow-500" },
    { label: "Closed Tickets", value: stats.closed_tickets, color: "bg-green-500" },
    { label: "Critical", value: stats.critical, color: "bg-red-500" },
    { label: "RMAs Pending", value: stats.rmas_in_progress, color: "bg-purple-500" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {cards.map(({ label, value, color }) => (
          <div key={label} className={`${color} text-white rounded-lg p-6`}>
            <p className="text-sm opacity-80">{label}</p>
            <p className="text-4xl font-bold mt-1">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
