import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: "📊", section: "General" },
  { to: "/conductores", label: "Conductores", icon: "👤", section: "Flota" },
  { to: "/vehiculos", label: "Vehículos", icon: "🚚", section: "Flota" },
  { to: "/pedidos", label: "Pedidos", icon: "📦", section: "Envíos" },
  { to: "/tracking", label: "Tracking", icon: "📍", section: "Envíos" },
];

export default function Sidebar() {
  let lastSection = null;

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>🚀 LastMile</h1>
        <p>Delivery Platform</p>
      </div>

      <nav className="sidebar-nav">
        {links.map((link) => {
          const showSection = link.section !== lastSection;
          if (showSection) lastSection = link.section;
          return (
            <div key={link.to}>
              {showSection && (
                <div className="nav-section">{link.section}</div>
              )}
              <NavLink
                to={link.to}
                end={link.to === "/"}
                className={({ isActive }) =>
                  "nav-link" + (isActive ? " active" : "")
                }
              >
                <span className="icon">{link.icon}</span>
                {link.label}
              </NavLink>
            </div>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        v1.0.0 · Cloud Project
      </div>
    </aside>
  );
}
