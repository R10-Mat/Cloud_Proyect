import { useState } from "react";
import { getEventosByPedido, createEvento } from "../api/eventosApi";
import { getDetalleEnvio } from "../api/orquestadorApi";

const TIPO_ICON = {
  recogido: "📦",
  en_camino: "🚚",
  retraso: "⏳",
  entregado: "✅",
  fallido: "❌",
};

const TIPOS = ["recogido", "en_camino", "retraso", "entregado", "fallido"];

const initialEvento = { conductor_id: "", tipo_evento: "recogido", descripcion: "", lat: "", lng: "" };

export default function Tracking() {
  const [pedidoId, setPedidoId] = useState("");
  const [detalle, setDetalle] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [evento, setEvento] = useState(initialEvento);
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const buscar = async (e) => {
    e.preventDefault();
    if (!pedidoId) return;
    setError("");
    setDetalle(null);
    setLoading(true);
    try {
      // Intentar desde el orquestador primero
      const { data } = await getDetalleEnvio(pedidoId);
      setDetalle(data);
    } catch {
      // Fallback directo a MS-EVENTOS
      try {
        const { data } = await getEventosByPedido(pedidoId);
        setDetalle({ pedido: { id: pedidoId }, linea_tiempo: data.eventos ?? [] });
      } catch {
        setError(`No se encontró información para el pedido #${pedidoId}.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const registrarEvento = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createEvento({
        pedido_id: parseInt(pedidoId),
        conductor_id: parseInt(evento.conductor_id),
        tipo_evento: evento.tipo_evento,
        descripcion: evento.descripcion,
        coordenadas: evento.lat && evento.lng
          ? { lat: parseFloat(evento.lat), lng: parseFloat(evento.lng) }
          : undefined,
      });
      setSuccess("Evento registrado.");
      setShowModal(false);
      setEvento(initialEvento);
      // Recargar
      const { data } = await getEventosByPedido(pedidoId);
      setDetalle((prev) => ({ ...prev, linea_tiempo: data.eventos ?? [] }));
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.error || "Error al registrar evento.");
    } finally {
      setSubmitting(false);
    }
  };

  const tipoClass = (tipo) => {
    const map = { recogido: "recogido", en_camino: "en_camino", entregado: "entregado", retraso: "retraso", fallido: "fallido" };
    return map[tipo] ?? "default";
  };

  return (
    <div className="page-content">
      <div className="page-actions">
        <h2>Tracking de envíos</h2>
      </div>

      <div className="card mb-20">
        <div className="card-body">
          <form onSubmit={buscar} style={{ display: "flex", gap: 12, alignItems: "flex-end" }}>
            <div className="form-group flex-1">
              <label>ID del pedido</label>
              <input
                type="number"
                min="1"
                placeholder="Ej: 123"
                value={pedidoId}
                onChange={(e) => setPedidoId(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Buscando..." : "🔍 Buscar"}
            </button>
          </form>
        </div>
      </div>

      {error && <div className="alert alert-error">⚠️ {error}</div>}
      {success && <div className="alert alert-success">✅ {success}</div>}

      {detalle && (
        <>
          <div className="card mb-20">
            <div className="card-header">
              <h3>📦 Pedido #{detalle.pedido?.id}</h3>
              <button className="btn btn-primary btn-sm" onClick={() => setShowModal(true)}>+ Registrar evento</button>
            </div>
            <div className="card-body">
              {detalle.pedido?.clienteNombre && (
                <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
                  <div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600 }}>CLIENTE</div>
                    <div style={{ marginTop: 2 }}>{detalle.pedido.clienteNombre}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600 }}>ESTADO</div>
                    <div style={{ marginTop: 2 }}>
                      <span className="badge badge-blue">{detalle.pedido.estado}</span>
                    </div>
                  </div>
                  {detalle.pedido.direccionOrigen && (
                    <div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600 }}>ORIGEN → DESTINO</div>
                      <div style={{ marginTop: 2 }}>{detalle.pedido.direccionOrigen} → {detalle.pedido.direccionDestino}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>📍 Línea de tiempo</h3>
              <span className="topbar-badge">{(detalle.linea_tiempo ?? []).length} eventos</span>
            </div>
            <div className="card-body">
              {(detalle.linea_tiempo ?? []).length === 0 ? (
                <div className="empty-state">
                  <div className="icon">📍</div>
                  <p>No hay eventos registrados para este pedido.</p>
                </div>
              ) : (
                <div className="timeline">
                  {(detalle.linea_tiempo ?? []).map((ev, i) => (
                    <div key={i} className="timeline-item">
                      <div className={`timeline-dot ${tipoClass(ev.tipo_evento)}`}>
                        {TIPO_ICON[ev.tipo_evento] ?? "📌"}
                      </div>
                      <div className="timeline-content">
                        <strong>{ev.tipo_evento?.replace("_", " ").toUpperCase()}</strong>
                        <p>{ev.descripcion}</p>
                        {ev.timestamp && (
                          <time>{new Date(ev.timestamp).toLocaleString()}</time>
                        )}
                        {ev.coordenadas?.lat && (
                          <p style={{ marginTop: 2, fontSize: 11.5 }}>
                            📌 {ev.coordenadas.lat}, {ev.coordenadas.lng}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal">
            <div className="modal-header">
              <h3>📍 Registrar evento — Pedido #{pedidoId}</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>
            <form onSubmit={registrarEvento}>
              <div className="modal-body">
                <div className="form-grid">
                  <div className="form-group">
                    <label>ID del conductor</label>
                    <input required type="number" min="1" placeholder="Ej: 5" value={evento.conductor_id}
                      onChange={(e) => setEvento({ ...evento, conductor_id: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Tipo de evento</label>
                    <select value={evento.tipo_evento} onChange={(e) => setEvento({ ...evento, tipo_evento: e.target.value })}>
                      {TIPOS.map((t) => <option key={t} value={t}>{TIPO_ICON[t]} {t}</option>)}
                    </select>
                  </div>
                  <div className="form-group" style={{ gridColumn: "1/-1" }}>
                    <label>Descripción</label>
                    <textarea required placeholder="Ej: Paquete recogido en depósito central" value={evento.descripcion}
                      onChange={(e) => setEvento({ ...evento, descripcion: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Latitud (opcional)</label>
                    <input type="number" step="any" placeholder="-34.6037" value={evento.lat}
                      onChange={(e) => setEvento({ ...evento, lat: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Longitud (opcional)</label>
                    <input type="number" step="any" placeholder="-58.3816" value={evento.lng}
                      onChange={(e) => setEvento({ ...evento, lng: e.target.value })} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? "Registrando..." : "Registrar evento"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
