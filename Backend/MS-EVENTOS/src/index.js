const express = require("express");
const mongoose = require("mongoose");

const eventosRouter = require("./routes/eventos");

const app = express();
const PORT = process.env.PORT || 3000;

app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS");
  res.header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Accept, Origin");
  if (req.method === "OPTIONS") {
    return res.sendStatus(200);
  }
  next();
});

app.use(express.json());

const {
  MONGO_HOST,
  MONGO_INITDB_ROOT_USERNAME,
  MONGO_INITDB_ROOT_PASSWORD,
  MONGO_DATABASE,
  MONGO_URI,
} = process.env;

const mongoHost = MONGO_HOST || "mongo_db";

const mongoUri =
  MONGO_URI ||
  `mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@${mongoHost}:27017/${MONGO_DATABASE}?authSource=admin`;

mongoose
  .connect(mongoUri)
  .then(() => console.log(" Conectado a MongoDB"))
  .catch((err) => {
    console.error(" Error conectando a MongoDB:", err.message);
    process.exit(1);
  });

app.get("/", (req, res) => {
  res.json({ mensaje: "MS-EVENTOS - Last Mile Delivery", version: "1.0.0" });
});

app.get("/health", (req, res) => {
  const estado = mongoose.connection.readyState === 1 ? "ok" : "degraded";
  res.json({ status: estado, servicio: "ms-eventos" });
});

app.use("/eventos", eventosRouter);

app.listen(PORT, () => {
  console.log(`🚀 MS-EVENTOS corriendo en puerto ${PORT}`);
});
