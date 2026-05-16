const mongoose = require("mongoose");

const EventoSchema = new mongoose.Schema(
  {
    pedido_id: { type: Number, required: true, index: true },
    conductor_id: { type: Number, required: true },
    tipo_evento: {
      type: String,
      required: true,
      enum: ["creado", "pendiente", "asignado", "en_camino", "recogido", "retraso", "entregado", "fallido", "cancelado"],
    },
    descripcion: { type: String, required: true },
    timestamp: { type: Date, default: Date.now },
    coordenadas: {
      lat: { type: Number },
      lng: { type: Number },
    },
  },
  { versionKey: false }
);

module.exports = mongoose.model("Evento", EventoSchema);
