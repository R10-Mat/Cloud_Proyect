import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Conductores from "./pages/Conductores";
import Vehiculos from "./pages/Vehiculos";
import Pedidos from "./pages/Pedidos";
import Tracking from "./pages/Tracking";

const TITLES = {
  "/": "Dashboard",
  "/conductores": "Conductores",
  "/vehiculos": "Vehículos",
  "/pedidos": "Pedidos",
  "/tracking": "Tracking de envíos",
};

function Topbar() {
  const { pathname } = useLocation();
  const title = TITLES[pathname] ?? "LastMile";
  return (
    <header className="topbar">
      <h2>{title}</h2>
      <span className="topbar-badge">Last-Mile Delivery Platform</span>
    </header>
  );
}

function Layout() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="main">
        <Topbar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/conductores" element={<Conductores />} />
          <Route path="/vehiculos" element={<Vehiculos />} />
          <Route path="/pedidos" element={<Pedidos />} />
          <Route path="/tracking" element={<Tracking />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout />
    </BrowserRouter>
  );
}
