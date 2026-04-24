import { useEffect, useState } from "react";
import { getConductores, createConductor } from "../api/flotaApi";

export default function Conductores() {
  const [conductores, setConductores] = useState([]);
  const [form, setForm] = useState({ nombre: "", licencia: "", telefono: "", estado: "disponible" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchConductores = async () => {
    try {
      const { data } = await getConductores();
      setConductores(data);
    } catch {
      setError("No se pudo conectar al backend.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchConductores(); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createConductor(form);
      setForm({ nombre: "", licencia: "", telefono: "", estado: "disponible" });
      fetchConductores(); // refresca la tabla
    } catch (err) {
      setError(err.response?.data?.detail || "Error al registrar conductor.");
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Gestión de Conductores</h1>

      {/* FORMULARIO */}
      <h2>Registrar conductor</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <input required placeholder="Nombre" value={form.nombre}
          onChange={e => setForm({ ...form, nombre: e.target.value })} />
        <input required placeholder="N° Licencia" value={form.licencia}
          onChange={e => setForm({ ...form, licencia: e.target.value })} />
        <input required placeholder="Teléfono" value={form.telefono}
          onChange={e => setForm({ ...form, telefono: e.target.value })} />
        <select value={form.estado} onChange={e => setForm({ ...form, estado: e.target.value })}>
          <option value="disponible">Disponible</option>
          <option value="en_ruta">En ruta</option>
          <option value="inactivo">Inactivo</option>
        </select>
        <button type="submit">Registrar</button>
      </form>
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* TABLA */}
      <h2>Lista de conductores</h2>
      {loading ? <p>Cargando...</p> : (
        <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
          <thead style={{ background: "#f0f0f0" }}>
            <tr>
              <th>ID</th><th>Nombre</th><th>Licencia</th><th>Teléfono</th><th>Estado</th><th>Vehículos</th>
            </tr>
          </thead>
          <tbody>
            {conductores.length === 0
              ? <tr><td colSpan="6" style={{ textAlign: "center" }}>Sin conductores registrados</td></tr>
              : conductores.map(c => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.nombre}</td>
                  <td>{c.licencia}</td>
                  <td>{c.telefono}</td>
                  <td>{c.estado}</td>
                  <td>{c.vehiculos?.length || 0} vehículo(s)</td>
                </tr>
              ))}
          </tbody>
        </table>
      )}
    </div>
  );
}