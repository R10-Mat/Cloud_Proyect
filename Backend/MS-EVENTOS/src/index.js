const express = require("express");
const mongoose = require("mongoose");
const swaggerJsdoc = require("swagger-jsdoc");
const swaggerUi = require("swagger-ui-express");

const eventosRouter = require("./routes/eventos");

const swaggerOptions = {
  definition: {
    openapi: "3.0.0",
    info: {
      title: "MS-EVENTOS API",
      version: "1.0.0",
      description: "Microservicio de historial y tracking de eventos de entrega - Last Mile Delivery",
    },
    servers: [{ url: "http://localhost:3000" }],
  },
  apis: ["./src/routes/*.js"],
};
const swaggerSpec = swaggerJsdoc(swaggerOptions);

const app = express();
const PORT = process.env.PORT || 3000;

// CORS: permitir requests desde Amplify y cualquier origen
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
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Construcción de la URI de MongoDB desde variables de entorno
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
  .then(() => console.log("✅ Conectado a MongoDB"))
  .catch((err) => {
    console.error("❌ Error conectando a MongoDB:", err.message);
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
