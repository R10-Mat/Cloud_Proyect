import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export const getConductores = () => API.get("/flota/conductores/");

export const createConductor = (data) => API.post("/flota/conductores/", data);

export const createVehiculo = (data) => API.post("/flota/vehiculos/", data);