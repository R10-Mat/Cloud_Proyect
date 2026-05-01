# 🚀 Last-Mile Delivery Platform

Plataforma de logística de última milla implementada con arquitectura de microservicios, orquestada con Docker Compose.

## Arquitectura

```
Frontend (React + Vite)
        │
        ▼
MS-ORQUESTADOR :8001  ──── agrega datos de todos los servicios
    │           │
    ▼           ▼
MS-FLOTA     MS-PEDIDOS     MS-EVENTOS
 :8000          :8080          :3000
 FastAPI       Spring Boot    Node.js
 MySQL         PostgreSQL     MongoDB

MS-ANALITICA :8002
 FastAPI + AWS Athena + S3
```

## Microservicios

| Servicio | Stack | Puerto | Base de datos |
|----------|-------|--------|---------------|
| MS-FLOTA | Python + FastAPI | 8000 | MySQL 8.0 |
| MS-PEDIDOS | Java + Spring Boot 3 | 8080 | PostgreSQL 16 |
| MS-EVENTOS | Node.js + Express | 3000 | MongoDB 6 |
| MS-ORQUESTADOR | Python + FastAPI | 8001 | — (BFF) |
| MS-ANALITICA | Python + FastAPI + Boto3 | 8002 | AWS Athena + S3 |

---

## ▶️ Cómo correr el proyecto (cualquier máquina)

### Requisito único: Docker Desktop

Todo el backend corre dentro de Docker, no necesitás instalar Python, Java, Node.js ni ninguna base de datos por separado.

**Descargar Docker Desktop:**
- **Mac**: https://www.docker.com/products/docker-desktop → "Download for Mac"
- **Windows**: https://www.docker.com/products/docker-desktop → "Download for Windows"

> En Windows asegurate de tener WSL 2 habilitado (Docker Desktop lo pide al instalar).

---

### Paso 1 — Clonar el repositorio

**Mac / Linux (Terminal):**
```bash
git clone https://github.com/R10-Mat/Cloud_Proyect.git
cd Cloud_Proyect
```

**Windows (PowerShell o Git Bash):**
```powershell
git clone https://github.com/R10-Mat/Cloud_Proyect.git
cd Cloud_Proyect
```

> Si no tenés Git: https://git-scm.com/downloads

---

### Paso 2 — Configurar variables de entorno

**Mac / Linux:**
```bash
cp .env.example .env
```

**Windows (PowerShell):**
```powershell
copy .env.example .env
```

El archivo `.env` ya tiene valores por defecto que funcionan localmente. No necesitás cambiar nada para correr el proyecto (excepto MS-ANALITICA que requiere credenciales AWS reales).

---

### Paso 3 — Levantar todos los servicios

Asegurate de que Docker Desktop esté abierto y corriendo, luego:

```bash
docker-compose up --build
```

La primera vez tarda varios minutos porque descarga las imágenes de Docker. Las siguientes veces es mucho más rápido.

Cuando veas esto en los logs, todo está listo:

```
✔ ms_flota_app      — INFO: Application startup complete.
✔ ms_pedidos_app    — Started MsPedidosApplication
✔ ms_eventos_app    — ✅ Conectado a MongoDB
✔ ms_orquestador_app — INFO: Application startup complete.
```

---

### Paso 4 — Levantar el Frontend

Abrí **otra terminal** (sin cerrar la del docker-compose) y ejecutá:

**Requiere Node.js 20+**: https://nodejs.org → LTS

```bash
cd Frontend
npm install
npm run dev
```

Luego abrí en el navegador: **http://localhost:5173**

---

### Detener el proyecto

```bash
# Detener los contenedores (conserva los datos)
docker-compose down

# Detener y borrar todos los datos (reinicio limpio)
docker-compose down -v
```

---

## URLs disponibles

| Servicio | URL |
|----------|-----|
| **Frontend** | http://localhost:5173 |
| MS-FLOTA Swagger | http://localhost:8000/docs |
| MS-PEDIDOS Swagger | http://localhost:8080/swagger-ui.html |
| MS-EVENTOS | http://localhost:3000 |
| MS-ORQUESTADOR Swagger | http://localhost:8001/docs |
| MS-ANALITICA Swagger | http://localhost:8002/docs |

---

## Endpoints principales

### MS-FLOTA (`:8000`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/flota/conductores/` | Listar conductores |
| POST | `/flota/conductores/` | Crear conductor |
| PATCH | `/flota/conductores/{id}` | Actualizar conductor |
| DELETE | `/flota/conductores/{id}` | Eliminar conductor |
| GET | `/flota/vehiculos/` | Listar vehículos |
| POST | `/flota/vehiculos/` | Registrar vehículo |

### MS-PEDIDOS (`:8080`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/pedidos` | Crear pedido |
| GET | `/api/pedidos` | Listar pedidos |
| GET | `/api/pedidos/{id}` | Obtener pedido |
| PATCH | `/api/pedidos/{id}/estado` | Actualizar estado |
| DELETE | `/api/pedidos/{id}` | Cancelar pedido |

### MS-EVENTOS (`:3000`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/eventos` | Registrar evento |
| GET | `/eventos/pedido/{pedido_id}` | Línea de tiempo del pedido |

### MS-ORQUESTADOR (`:8001`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard/resumen` | Total conductores + pedidos |
| GET | `/dashboard/envio/{pedido_id}` | Detalle completo del envío |

### MS-ANALITICA (`:8002`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/analitica/entregas-por-mes` | Entregas agrupadas por mes |
| GET | `/analitica/conductores-actividad` | Actividad de conductores |
