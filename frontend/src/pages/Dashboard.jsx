import { Link } from "react-router-dom";
import { useApiResource } from "../api";
import { LoadingState, ErrorState } from "../components/AsyncState";

export default function Dashboard() {
  const { data: stats, loading, error, reload } = useApiResource("/dashboard");

  if (loading) return <LoadingState message="Loading dashboard…" />;
  if (error) return <ErrorState error={error} onRetry={reload} />;

  const cards = [
    { label: "Open Tickets", value: stats.open_tickets, color: "bg-blue-500", to: "/tickets?status=Open" },
    { label: "In Progress", value: stats.in_progress, color: "bg-yellow-500", to: "/tickets?status=In+Progress" },
    { label: "Closed Tickets", value: stats.closed_tickets, color: "bg-green-500", to: "/tickets?status=Closed" },
    { label: "Critical", value: stats.critical, color: "bg-red-500", to: "/tickets?priority=Critical" },
    { label: "RMAs Pending", value: stats.rmas_in_progress, color: "bg-purple-500", to: "/rmas?resolution=Pending" },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {cards.map(({ label, value, color, to }) => (
          <Link
            key={label}
            to={to}
            aria-label={`${label}: ${value} ${value === 1 ? "item" : "items"}. Open queue`}
            className={`${color} block rounded-lg p-6 text-white transition hover:brightness-95 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700`}
          >
            <p className="text-sm opacity-80">{label}</p>
            <p className="text-3xl font-bold mt-1">{value}</p>
            <p className="mt-4 text-xs font-medium opacity-80">Open queue →</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
