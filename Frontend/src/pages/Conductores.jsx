import { useEffect, useState } from "react";
import { getConductores, createConductor, updateConductor, deleteConductor } from "../api/flotaApi";

const ESTADO_BADGE = {
  disponible: "badge-green",
  en_ruta: "badge-blue",
  inactivo: "badge-gray",
};

const initialForm = { nombre: "", licencia: "", telefono: "", estado: "disponible" };

export default function Conductores() {
  const [conductores, setConductores] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [search, setSearch] = useState("");

  const fetchConductores = async () => {
    setLoading(true);
    try {
      const { data } = await getConductores();
      setConductores(data);
    } catch {
      setError("No se pudo conectar al servicio de flota.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchConductores(); }, []);

  const openCreate = () => {
    setForm(initialForm);
    setEditId(null);
    setError("");
    setShowModal(true);
  };

  const openEdit = (c) => {
    setForm({ nombre: c.nombre, licencia: c.licencia, telefono: c.telefono, estado: c.estado });
    setEditId(c.id);
    setError("");
    setShowModal(true);
  };

  const closeModal = () => { setShowModal(false); setError(""); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (editId) {
        await updateConductor(editId, form);
        setSuccess("Conductor actualizado correctamente.");
      } else {
        await createConductor(form);
        setSuccess("Conductor registrado correctamente.");
      }
      closeModal();
      fetchConductores();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al guardar conductor.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id, nombre) => {
    if (!confirm(`¿Eliminar al conductor "${nombre}"?`)) return;
    try {
      await deleteConductor(id);
      setSuccess("Conductor eliminado.");
      fetchConductores();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al eliminar.");
    }
  };

  const filtered = conductores.filter(
    (c) =>
      c.nombre.toLowerCase().includes(search.toLowerCase()) ||
      c.licencia.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page-content">
      <div className="page-actions">
        <h2>Conductores</h2>
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            placeholder="Buscar por nombre o licencia..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Nuevo conductor</button>
      </div>

      {success && <div className="alert alert-success">✅ {success}</div>}
      {error && !showModal && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="card">
        <div className="card-header">
          <h3>👤 Lista de conductores</h3>
          <span className="topbar-badge">{conductores.length} registros</span>
        </div>
        <div className="table-wrap">
          {loading ? (
            <div className="loading-state">⏳ Cargando conductores...</div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <div className="icon">👤</div>
              <p>{search ? "Sin resultados para tu búsqueda." : "No hay conductores registrados."}</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Nombre</th><th>Licencia</th><th>Teléfono</th><th>Estado</th><th>Vehículos</th><th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => (
                  <tr key={c.id}>
                    <td><strong>#{c.id}</strong></td>
                    <td>{c.nombre}</td>
                    <td><code style={{ background: "#f1f5f9", padding: "2px 6px", borderRadius: 4, fontSize: 12 }}>{c.licencia}</code></td>
                    <td>{c.telefono}</td>
                    <td><span className={`badge ${ESTADO_BADGE[c.estado] ?? "badge-gray"}`}>{c.estado}</span></td>
                    <td>{c.vehiculos?.length ?? 0} vehículo(s)</td>
                    <td>
                      <div className="flex gap-12">
                        <button className="btn btn-ghost btn-sm" onClick={() => openEdit(c)}>✏️ Editar</button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(c.id, c.nombre)}>🗑️</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && closeModal()}>
          <div className="modal">
            <div className="modal-header">
              <h3>{editId ? "✏️ Editar conductor" : "➕ Nuevo conductor"}</h3>
              <button className="btn btn-ghost btn-sm" onClick={closeModal}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && <div className="alert alert-error mb-20">⚠️ {error}</div>}
                <div className="form-grid">
                  <div className="form-group" style={{ gridColumn: "1/-1" }}>
                    <label>Nombre completo</label>
                    <input required placeholder="Ej: Juan Pérez" value={form.nombre}
                      onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>N° de licencia</label>
                    <input required placeholder="Ej: LIC-001" value={form.licencia}
                      onChange={(e) => setForm({ ...form, licencia: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Teléfono</label>
                    <input required placeholder="Ej: 555-1234" value={form.telefono}
                      onChange={(e) => setForm({ ...form, telefono: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Estado</label>
                    <select value={form.estado} onChange={(e) => setForm({ ...form, estado: e.target.value })}>
                      <option value="disponible">Disponible</option>
                      <option value="en_ruta">En ruta</option>
                      <option value="inactivo">Inactivo</option>
                    </select>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? "Guardando..." : editId ? "Actualizar" : "Registrar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
