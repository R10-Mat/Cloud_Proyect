const express = require("express");
const Evento = require("../models/Evento");

const router = express.Router();

// POST /eventos - Registrar nuevo evento
router.post("/", async (req, res) => {
  try {
    const { pedido_id, conductor_id, tipo_evento, descripcion, coordenadas } = req.body;

    if (!pedido_id || !conductor_id || !tipo_evento || !descripcion) {
      return res.status(400).json({ error: "Campos requeridos: pedido_id, conductor_id, tipo_evento, descripcion" });
    }

    const evento = new Evento({ pedido_id, conductor_id, tipo_evento, descripcion, coordenadas });
    await evento.save();
    res.status(201).json(evento);
  } catch (err) {
    if (err.name === "ValidationError") {
      return res.status(400).json({ error: err.message });
    }
    res.status(500).json({ error: "Error interno del servidor" });
  }
});

// GET /eventos/pedido/:pedido_id - Línea de tiempo de un pedido
router.get("/pedido/:pedido_id", async (req, res) => {
  try {
    const pedido_id = parseInt(req.params.pedido_id);
    if (isNaN(pedido_id)) {
      return res.status(400).json({ error: "pedido_id debe ser un número" });
    }

    const eventos = await Evento.find({ pedido_id }).sort({ timestamp: 1 });
    res.json({ pedido_id, total: eventos.length, eventos });
  } catch (err) {
    res.status(500).json({ error: "Error interno del servidor" });
  }
});

// GET /eventos - Listar todos (útil para debugging y dashboard)
router.get("/", async (req, res) => {
  try {
    const { limit = 50, tipo_evento } = req.query;
    const filtro = tipo_evento ? { tipo_evento } : {};
    const eventos = await Evento.find(filtro).sort({ timestamp: -1 }).limit(parseInt(limit));
    res.json(eventos);
  } catch (err) {
    res.status(500).json({ error: "Error interno del servidor" });
  }
});

module.exports = router;
