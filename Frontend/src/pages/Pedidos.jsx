import { useEffect, useState } from "react";
import { getPedidos, createPedido, updateEstado, deletePedido } from "../api/pedidosApi";

const ESTADO_BADGE = {
  PENDIENTE: "badge-orange",
  ASIGNADO: "badge-blue",
  EN_CAMINO: "badge-purple",
  ENTREGADO: "badge-green",
  CANCELADO: "badge-gray",
  FALLIDO: "badge-red",
};

const ESTADOS = ["PENDIENTE", "ASIGNADO", "EN_CAMINO", "ENTREGADO", "FALLIDO", "CANCELADO"];

const initialForm = {
  clienteNombre: "",
  clienteTelefono: "",
  clienteEmail: "",
  direccionOrigen: "",
  direccionDestino: "",
  paquetes: [{ descripcion: "", pesoKg: "", largoCm: "", anchoCm: "", altoCm: "", fragil: "" }],
};

export default function Pedidos() {
  const [pedidos, setPedidos] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [filtroEstado, setFiltroEstado] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [updatingId, setUpdatingId] = useState(null);

  const fetchPedidos = async () => {
    setLoading(true);
    try {
      const { data } = await getPedidos(filtroEstado || undefined);
      const arr = Array.isArray(data) ? data : data?.content ?? [];
      setPedidos(arr);
    } catch {
      setError("No se pudo conectar al servicio de pedidos.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPedidos(); }, [filtroEstado]);

  const openCreate = () => { setForm(initialForm); setError(""); setShowModal(true); };
  const closeModal = () => { setShowModal(false); setError(""); };

  const addDetalle = () =>
    setForm((f) => ({ ...f, paquetes: [...f.paquetes, { descripcion: "", pesoKg: "", largoCm: "", anchoCm: "", altoCm: "", fragil: "" }] }));

  const removeDetalle = (i) =>
    setForm((f) => ({ ...f, paquetes: f.paquetes.filter((_, idx) => idx !== i) }));

  const setDetalle = (i, field, val) =>
    setForm((f) => ({
      ...f,
      paquetes: f.paquetes.map((d, idx) => (idx === i ? { ...d, [field]: val } : d)),
    }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const payload = {
        clienteNombre: form.clienteNombre,
        clienteTelefono: form.clienteTelefono,
        clienteEmail: form.clienteEmail || undefined,
        direccionOrigen: form.direccionOrigen,
        direccionDestino: form.direccionDestino,
        paquetes: form.paquetes.map((d) => ({
          descripcion: d.descripcion,
          pesoKg: parseFloat(d.pesoKg),
          largoCm: d.largoCm ? parseFloat(d.largoCm) : undefined,
          anchoCm: d.anchoCm ? parseFloat(d.anchoCm) : undefined,
          altoCm: d.altoCm ? parseFloat(d.altoCm) : undefined,
          fragil: d.fragil || undefined,
        })),
      };
      await createPedido(payload);
      setSuccess("Pedido creado correctamente.");
      closeModal();
      fetchPedidos();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.message || err.response?.data?.detail || "Error al crear pedido.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleEstado = async (id, estado) => {
    setUpdatingId(id);
    try {
      await updateEstado(id, estado);
      fetchPedidos();
      setSuccess(`Pedido #${id} actualizado a ${estado}.`);
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.message || "Error al actualizar estado.");
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm(`¿Cancelar el pedido #${id}?`)) return;
    try {
      await deletePedido(id);
      setSuccess(`Pedido #${id} cancelado.`);
      fetchPedidos();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.message || "Error al cancelar pedido.");
    }
  };

  return (
    <div className="page-content">
      <div className="page-actions">
        <h2>Pedidos</h2>
        <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}
          style={{ maxWidth: 160 }}>
          <option value="">Todos los estados</option>
          {ESTADOS.map((e) => <option key={e} value={e}>{e}</option>)}
        </select>
        <button className="btn btn-primary" onClick={openCreate}>+ Nuevo pedido</button>
      </div>

      {success && <div className="alert alert-success">✅ {success}</div>}
      {error && !showModal && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="card">
        <div className="card-header">
          <h3>📦 Lista de pedidos</h3>
          <span className="topbar-badge">{pedidos.length} registros</span>
        </div>
        <div className="table-wrap">
          {loading ? (
            <div className="loading-state">⏳ Cargando pedidos...</div>
          ) : pedidos.length === 0 ? (
            <div className="empty-state">
              <div className="icon">📦</div>
              <p>No hay pedidos {filtroEstado ? `con estado "${filtroEstado}"` : "registrados"}.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>#</th><th>Cliente</th><th>Origen</th><th>Destino</th>
                  <th>Paquetes</th><th>Estado</th><th>Fecha</th><th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.map((p) => {
                  const estado = (p.estado ?? "").toUpperCase();
                  const proxEstados = ESTADOS.filter((e) => e !== estado && e !== "CANCELADO");
                  return (
                    <tr key={p.id}>
                      <td><strong>#{p.id}</strong></td>
                      <td>{p.clienteNombre ?? p.cliente_nombre}</td>
                      <td style={{ maxWidth: 140, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {p.direccionOrigen ?? p.direccion_origen}
                      </td>
                      <td style={{ maxWidth: 140, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {p.direccionDestino ?? p.direccion_destino}
                      </td>
                      <td>{(p.paquetes ?? []).length} paq.</td>
                      <td><span className={`badge ${ESTADO_BADGE[estado] ?? "badge-gray"}`}>{p.estado}</span></td>
                      <td>{p.fechaCreacion ? new Date(p.fechaCreacion).toLocaleDateString() : "—"}</td>
                      <td>
                        <div className="flex gap-12">
                          <select
                            value=""
                            disabled={updatingId === p.id}
                            onChange={(e) => e.target.value && handleEstado(p.id, e.target.value)}
                            style={{ fontSize: 12, padding: "4px 6px" }}
                          >
                            <option value="">Cambiar estado</option>
                            {proxEstados.map((s) => <option key={s} value={s}>{s}</option>)}
                          </select>
                          <button className="btn btn-danger btn-sm" onClick={() => handleDelete(p.id)}>🗑️</button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && closeModal()}>
          <div className="modal" style={{ maxWidth: 600 }}>
            <div className="modal-header">
              <h3>📦 Nuevo pedido</h3>
              <button className="btn btn-ghost btn-sm" onClick={closeModal}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && <div className="alert alert-error mb-20">⚠️ {error}</div>}
                <div className="form-grid mb-20">
                  <div className="form-group" style={{ gridColumn: "1/-1" }}>
                    <label>Nombre del cliente</label>
                    <input required placeholder="Ej: Ana Gómez" value={form.clienteNombre}
                      onChange={(e) => setForm({ ...form, clienteNombre: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Teléfono</label>
                    <input required placeholder="Ej: 5551234567" value={form.clienteTelefono}
                      onChange={(e) => setForm({ ...form, clienteTelefono: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Email (opcional)</label>
                    <input type="email" placeholder="Ej: ana@email.com" value={form.clienteEmail}
                      onChange={(e) => setForm({ ...form, clienteEmail: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Dirección origen</label>
                    <input required placeholder="Ej: Av. Principal 123" value={form.direccionOrigen}
                      onChange={(e) => setForm({ ...form, direccionOrigen: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Dirección destino</label>
                    <input required placeholder="Ej: Calle Secundaria 456" value={form.direccionDestino}
                      onChange={(e) => setForm({ ...form, direccionDestino: e.target.value })} />
                  </div>
                </div>

                <div style={{ marginBottom: 12, display: "flex", alignItems: "center", gap: 10 }}>
                  <strong style={{ fontSize: 13 }}>📦 Paquetes</strong>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={addDetalle}>+ Agregar</button>
                </div>

                {form.paquetes.map((d, i) => (
                  <div key={i} className="card" style={{ marginBottom: 10, padding: "14px 16px" }}>
                    <div className="flex justify-between items-center" style={{ marginBottom: 10 }}>
                      <strong style={{ fontSize: 12, color: "var(--text-muted)" }}>Paquete #{i + 1}</strong>
                      {form.paquetes.length > 1 && (
                        <button type="button" className="btn btn-danger btn-sm" onClick={() => removeDetalle(i)}>✕</button>
                      )}
                    </div>
                    <div className="form-grid">
                      <div className="form-group" style={{ gridColumn: "1/-1" }}>
                        <label>Descripción</label>
                        <input required placeholder="Ej: Laptop, ropa, documentos..." value={d.descripcion}
                          onChange={(e) => setDetalle(i, "descripcion", e.target.value)} />
                      </div>
                      <div className="form-group">
                        <label>Peso (kg)</label>
                        <input required type="number" step="0.01" min="0.01" placeholder="2.5" value={d.pesoKg}
                          onChange={(e) => setDetalle(i, "pesoKg", e.target.value)} />
                      </div>
                      <div className="form-group">
                        <label>Frágil</label>
                        <select value={d.fragil} onChange={(e) => setDetalle(i, "fragil", e.target.value)}>
                          <option value="">No especificado</option>
                          <option value="SI">Sí</option>
                          <option value="NO">No</option>
                        </select>
                      </div>
                      <div className="form-group">
                        <label>Largo (cm)</label>
                        <input type="number" step="0.1" min="0" placeholder="40" value={d.largoCm}
                          onChange={(e) => setDetalle(i, "largoCm", e.target.value)} />
                      </div>
                      <div className="form-group">
                        <label>Ancho (cm)</label>
                        <input type="number" step="0.1" min="0" placeholder="30" value={d.anchoCm}
                          onChange={(e) => setDetalle(i, "anchoCm", e.target.value)} />
                      </div>
                      <div className="form-group">
                        <label>Alto (cm)</label>
                        <input type="number" step="0.1" min="0" placeholder="10" value={d.altoCm}
                          onChange={(e) => setDetalle(i, "altoCm", e.target.value)} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? "Creando..." : "Crear pedido"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
