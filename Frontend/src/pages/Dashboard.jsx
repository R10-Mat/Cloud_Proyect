import { useEffect, useState } from "react";
import { getResumen } from "../api/orquestadorApi";
import { getPedidos } from "../api/pedidosApi";
import { getConductores } from "../api/flotaApi";

function StatCard({ icon, value, label, colorClass, loading }) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${colorClass}`}>{icon}</div>
      <div className="stat-info">
        <div className="stat-value">{loading ? "—" : value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}

const ESTADO_BADGE = {
  PENDIENTE: "badge-orange",
  ASIGNADO: "badge-blue",
  EN_CAMINO: "badge-purple",
  ENTREGADO: "badge-green",
  CANCELADO: "badge-gray",
  FALLIDO: "badge-red",
};

export default function Dashboard() {
  const [resumen, setResumen] = useState(null);
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const [rResumen, rPedidos, rConductores] = await Promise.allSettled([
          getResumen(),
          getPedidos(),
          getConductores(),
        ]);

        if (rResumen.status === "fulfilled") {
          setResumen(rResumen.value.data);
        } else {
          // Fallback: usar datos directos
          const conductores = rConductores.status === "fulfilled" ? rConductores.value.data : [];
          const pedidosData = rPedidos.status === "fulfilled"
            ? (Array.isArray(rPedidos.value.data) ? rPedidos.value.data : rPedidos.value.data?.content ?? [])
            : [];
          setResumen({
            total_conductores: conductores.length,
            total_pedidos: pedidosData.length,
          });
        }

        if (rPedidos.status === "fulfilled") {
          const data = rPedidos.value.data;
          const arr = Array.isArray(data) ? data : data?.content ?? [];
          setPedidos(arr.slice(0, 5));
        }
      } catch {
        setError("No se pudo cargar el dashboard.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const entregados = pedidos.filter((p) => p.estado === "ENTREGADO" || p.estado === "entregado").length;
  const pendientes = pedidos.filter((p) => p.estado === "PENDIENTE" || p.estado === "pendiente").length;

  return (
    <div className="page-content">
      <div className="page-actions">
        <h2>Dashboard</h2>
        {resumen?.fecha_consulta && (
          <span className="topbar-badge">
            Actualizado {new Date(resumen.fecha_consulta).toLocaleTimeString()}
          </span>
        )}
      </div>

      {error && <div className="alert alert-error">⚠️ {error} — Verificá que los servicios estén corriendo.</div>}

      <div className="stats-grid">
        <StatCard icon="🚗" value={resumen?.total_conductores ?? 0} label="Conductores activos" colorClass="blue" loading={loading} />
        <StatCard icon="📦" value={resumen?.total_pedidos ?? 0} label="Pedidos totales" colorClass="purple" loading={loading} />
        <StatCard icon="✅" value={entregados} label="Entregados (recientes)" colorClass="green" loading={loading} />
        <StatCard icon="🕐" value={pendientes} label="Pendientes (recientes)" colorClass="orange" loading={loading} />
      </div>

      <div className="card">
        <div className="card-header">
          <h3>📋 Últimos pedidos</h3>
        </div>
        <div className="table-wrap">
          {loading ? (
            <div className="loading-state">⏳ Cargando datos...</div>
          ) : pedidos.length === 0 ? (
            <div className="empty-state">
              <div className="icon">📭</div>
              <p>No hay pedidos registrados aún.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Cliente</th>
                  <th>Origen</th>
                  <th>Destino</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.map((p) => (
                  <tr key={p.id}>
                    <td><strong>#{p.id}</strong></td>
                    <td>{p.clienteNombre ?? p.cliente_nombre}</td>
                    <td>{p.direccionOrigen ?? p.direccion_origen}</td>
                    <td>{p.direccionDestino ?? p.direccion_destino}</td>
                    <td>
                      <span className={`badge ${ESTADO_BADGE[p.estado?.toUpperCase()] ?? "badge-gray"}`}>
                        {p.estado}
                      </span>
                    </td>
                    <td>{p.fechaCreacion ? new Date(p.fechaCreacion).toLocaleDateString() : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
