const express = require("express");
const Evento = require("../models/Evento");

const router = express.Router();

/**
 * @swagger
 * tags:
 *   name: Eventos
 *   description: Historial y tracking de eventos de entrega
 */

/**
 * @swagger
 * /eventos:
 *   post:
 *     summary: Registrar nuevo evento
 *     tags: [Eventos]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [pedido_id, conductor_id, tipo_evento, descripcion]
 *             properties:
 *               pedido_id:
 *                 type: integer
 *               conductor_id:
 *                 type: integer
 *               tipo_evento:
 *                 type: string
 *                 enum: [ASIGNADO, RECOGIDO, EN_CAMINO, ENTREGADO, FALLIDO]
 *               descripcion:
 *                 type: string
 *               coordenadas:
 *                 type: object
 *                 properties:
 *                   lat: { type: number }
 *                   lng: { type: number }
 *     responses:
 *       201:
 *         description: Evento registrado exitosamente
 *       400:
 *         description: Campos requeridos faltantes o inválidos
 *       500:
 *         description: Error interno del servidor
 */
router.post("/", async (req, res) => {
  try {
    const { pedido_id, conductor_id, tipo_evento, descripcion, coordenadas } = req.body;

    if (pedido_id == null || conductor_id == null || !tipo_evento || !descripcion) {
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

/**
 * @swagger
 * /eventos/pedido/{pedido_id}:
 *   get:
 *     summary: Obtener línea de tiempo de un pedido
 *     tags: [Eventos]
 *     parameters:
 *       - in: path
 *         name: pedido_id
 *         required: true
 *         schema:
 *           type: integer
 *         description: ID del pedido
 *     responses:
 *       200:
 *         description: Lista de eventos del pedido ordenados por timestamp
 *       400:
 *         description: pedido_id debe ser un número
 *       500:
 *         description: Error interno del servidor
 */
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

/**
 * @swagger
 * /eventos:
 *   get:
 *     summary: Listar todos los eventos
 *     tags: [Eventos]
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 50
 *         description: Cantidad máxima de eventos a retornar
 *       - in: query
 *         name: tipo_evento
 *         schema:
 *           type: string
 *           enum: [ASIGNADO, RECOGIDO, EN_CAMINO, ENTREGADO, FALLIDO]
 *         description: Filtrar por tipo de evento
 *     responses:
 *       200:
 *         description: Lista de eventos
 *       500:
 *         description: Error interno del servidor
 */
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
