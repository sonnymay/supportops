import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import Devices from "./pages/Devices";
import Tickets from "./pages/Tickets";
import RMAs from "./pages/RMAs";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100 flex">
        {/* Sidebar */}
        <aside className="w-56 bg-gray-900 text-white flex flex-col p-4 gap-2">
          <h1 className="text-xl font-bold mb-6">SupportOps</h1>
          {[
            { to: "/", label: "Dashboard" },
            { to: "/tickets", label: "Tickets" },
            { to: "/customers", label: "Customers" },
            { to: "/devices", label: "Devices" },
            { to: "/rmas", label: "RMAs" },
          ].map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `px-3 py-2 rounded text-sm font-medium transition ${
                  isActive ? "bg-blue-600" : "hover:bg-gray-700"
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </aside>

        {/* Main content */}
        <main className="flex-1 p-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/devices" element={<Devices />} />
            <Route path="/rmas" element={<RMAs />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
