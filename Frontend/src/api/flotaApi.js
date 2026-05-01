import axios from "axios";

const FLOTA = axios.create({ baseURL: "http://localhost:8000" });

export const getConductores = () => FLOTA.get("/flota/conductores/");
export const getConductor = (id) => FLOTA.get(`/flota/conductores/${id}`);
export const createConductor = (data) => FLOTA.post("/flota/conductores/", data);
export const updateConductor = (id, data) => FLOTA.patch(`/flota/conductores/${id}`, data);
export const deleteConductor = (id) => FLOTA.delete(`/flota/conductores/${id}`);

export const getVehiculos = () => FLOTA.get("/flota/vehiculos/");
export const createVehiculo = (data) => FLOTA.post("/flota/vehiculos/", data);
