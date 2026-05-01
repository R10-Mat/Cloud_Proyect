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

## Requisitos

- Docker Desktop
- Node.js 20+ (solo para el frontend en desarrollo)
- Cuenta AWS con Athena y S3 configurados (para MS-ANALITICA)

## Configuración

```bash
# 1. Clonar el repositorio
git clone https://github.com/R10-Mat/Cloud_Proyect.git
cd Cloud_Proyect

# 2. Copiar y editar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

## Levantar el proyecto

```bash
# Construir y levantar todos los servicios
docker-compose up --build

# En segundo plano
docker-compose up --build -d

# Ver logs de un servicio
docker-compose logs -f ms_flota

# Detener todo
docker-compose down

# Detener y borrar volúmenes (resetea las bases de datos)
docker-compose down -v
```

## Frontend (desarrollo local)

```bash
cd Frontend
npm install
npm run dev
# Abrir http://localhost:5173
```

## URLs disponibles

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| MS-FLOTA Swagger | http://localhost:8000/docs |
| MS-PEDIDOS Swagger | http://localhost:8080/swagger-ui.html |
| MS-EVENTOS | http://localhost:3000 |
| MS-ORQUESTADOR Swagger | http://localhost:8001/docs |
| MS-ANALITICA Swagger | http://localhost:8002/docs |

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
