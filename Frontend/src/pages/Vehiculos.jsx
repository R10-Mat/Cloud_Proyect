import { useEffect, useState } from "react";
import { getVehiculos, createVehiculo, getConductores } from "../api/flotaApi";

const initialForm = { placa: "", marca: "", capacidad_kg: "", conductor_id: "" };

export default function Vehiculos() {
  const [vehiculos, setVehiculos] = useState([]);
  const [conductores, setConductores] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [search, setSearch] = useState("");

  const fetch = async () => {
    setLoading(true);
    try {
      const [rv, rc] = await Promise.all([getVehiculos(), getConductores()]);
      setVehiculos(rv.data);
      setConductores(rc.data);
    } catch {
      setError("No se pudo conectar al servicio de flota.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, []);

  const openCreate = () => { setForm(initialForm); setError(""); setShowModal(true); };
  const closeModal = () => { setShowModal(false); setError(""); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await createVehiculo({ ...form, capacidad_kg: parseFloat(form.capacidad_kg), conductor_id: parseInt(form.conductor_id) });
      setSuccess("Vehículo registrado correctamente.");
      closeModal();
      fetch();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || "Error al registrar vehículo.");
    } finally {
      setSubmitting(false);
    }
  };

  const conductorNombre = (id) => conductores.find((c) => c.id === id)?.nombre ?? `#${id}`;

  const filtered = vehiculos.filter(
    (v) =>
      v.placa?.toLowerCase().includes(search.toLowerCase()) ||
      v.marca?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page-content">
      <div className="page-actions">
        <h2>Vehículos</h2>
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input placeholder="Buscar por placa o marca..." value={search}
            onChange={(e) => setSearch(e.target.value)} />
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Nuevo vehículo</button>
      </div>

      {success && <div className="alert alert-success">✅ {success}</div>}
      {error && !showModal && <div className="alert alert-error">⚠️ {error}</div>}

      <div className="card">
        <div className="card-header">
          <h3>🚚 Flota de vehículos</h3>
          <span className="topbar-badge">{vehiculos.length} vehículos</span>
        </div>
        <div className="table-wrap">
          {loading ? (
            <div className="loading-state">⏳ Cargando vehículos...</div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <div className="icon">🚚</div>
              <p>{search ? "Sin resultados." : "No hay vehículos registrados."}</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Placa</th><th>Marca</th><th>Capacidad (kg)</th><th>Conductor</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((v) => (
                  <tr key={v.id}>
                    <td><strong>#{v.id}</strong></td>
                    <td><code style={{ background: "#f1f5f9", padding: "2px 8px", borderRadius: 4, fontSize: 12 }}>{v.placa}</code></td>
                    <td>{v.marca}</td>
                    <td>{v.capacidad_kg?.toLocaleString()} kg</td>
                    <td>
                      <span className="badge badge-blue">👤 {conductorNombre(v.conductor_id)}</span>
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
              <h3>🚚 Registrar vehículo</h3>
              <button className="btn btn-ghost btn-sm" onClick={closeModal}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                {error && <div className="alert alert-error mb-20">⚠️ {error}</div>}
                <div className="form-grid">
                  <div className="form-group">
                    <label>Placa</label>
                    <input required placeholder="Ej: ABC-123" value={form.placa}
                      onChange={(e) => setForm({ ...form, placa: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Marca</label>
                    <input required placeholder="Ej: Toyota" value={form.marca}
                      onChange={(e) => setForm({ ...form, marca: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Capacidad (kg)</label>
                    <input required type="number" step="0.1" min="1" placeholder="Ej: 1500" value={form.capacidad_kg}
                      onChange={(e) => setForm({ ...form, capacidad_kg: e.target.value })} />
                  </div>
                  <div className="form-group">
                    <label>Conductor asignado</label>
                    <select required value={form.conductor_id}
                      onChange={(e) => setForm({ ...form, conductor_id: e.target.value })}>
                      <option value="">— Seleccionar —</option>
                      {conductores.map((c) => (
                        <option key={c.id} value={c.id}>{c.nombre} ({c.licencia})</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={closeModal}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                  {submitting ? "Registrando..." : "Registrar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
