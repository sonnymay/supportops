import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import Devices from "./pages/Devices";
import Tickets from "./pages/Tickets";
import RMAs from "./pages/RMAs";

export default function App() {
  const navigation = [
    { to: "/", label: "Dashboard" },
    { to: "/tickets", label: "Tickets" },
    { to: "/customers", label: "Customers" },
    { to: "/devices", label: "Devices" },
    { to: "/rmas", label: "RMAs" },
  ];

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100 lg:flex">
        <aside className="bg-gray-950 text-white p-4 lg:w-60 lg:min-h-screen lg:p-5">
          <div className="mb-4 flex items-center justify-between lg:mb-8">
            <h1 className="text-xl font-bold">SupportOps</h1>
            <span className="text-xs text-gray-400 lg:hidden">Service console</span>
          </div>
          <nav aria-label="Primary" className="grid grid-cols-3 gap-2 sm:grid-cols-5 lg:flex lg:flex-col">
            {navigation.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `min-w-0 px-2 py-2 text-center text-sm font-medium transition lg:px-3 lg:text-left ${
                  isActive ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"
                }`
              }
            >
              {label}
            </NavLink>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1 p-4 sm:p-6 lg:p-8">
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
