```markdown
# Plataforma "Last-Mile Delivery" - Especificación Técnica Completa

## Índice

1. [Arquitectura General](#1-arquitectura-general)
2. [Reglas del Equipo](#2-reglas-del-equipo)
3. [Microservicio MS-FLOTA (Gestión de Flota)](#3-microservicio-ms-flota-gestión-de-flota)
4. [Microservicio MS-PEDIDOS (Gestión de Envíos)](#4-microservicio-ms-pedidos-gestión-de-envíos)
5. [Microservicio MS-EVENTOS (Historial y Tracking)](#5-microservicio-ms-eventos-historial-y-tracking)
6. [Microservicio MS-ORQUESTADOR (Vista Unificada)](#6-microservicio-ms-orquestador-vista-unificada)
7. [Microservicio MS-ANALITICA (Reportes AWS Athena)](#7-microservicio-ms-analitica-reportes-aws-athena)
8. [Estructura de Carpetas del Proyecto](#8-estructura-de-carpetas-del-proyecto)
9. [Configuración del Entorno (.env)](#9-configuración-del-entorno-env)
10. [Docker Compose Global](#10-docker-compose-global)
11. [Ejecución del Proyecto](#11-ejecución-del-proyecto)
12. [Endpoints Globales por Microservicio](#12-endpoints-globales-por-microservicio)

---

## 1. Arquitectura General

El proyecto es una plataforma de **logística de última milla (Last-Mile Delivery)** compuesta por **5 microservicios** y **3 bases de datos**, orquestados con Docker Compose.

```
                    ┌─────────────────────────────────────────┐
                    │            Frontend (cliente)           │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │      MS-ORQUESTADOR (BFF) - Puerto 8001 │
                    │            FastAPI - Sin BD             │
                    └───────┬─────────────┬───────────────────┘
                            │             │
            ┌───────────────┘             └───────────────┐
            │                                             │
            ▼                                             ▼
┌───────────────────────┐                   ┌───────────────────────┐
│   MS-FLOTA - Puerto 8000 │                 │  MS-PEDIDOS - Puerto 8080 │
│  FastAPI + MySQL       │                   │  Spring Boot + PostgreSQL│
│  Conductores y vehículos│                   │  Pedidos y paquetes      │
└───────────┬───────────┘                   └───────────┬───────────┘
            │                                             │
            │                          ┌──────────────────┘
            │                          │
            │                          ▼
            │              ┌───────────────────────────┐
            │              │  MS-EVENTOS - Puerto 3000   │
            │              │  Node.js + MongoDB          │
            │              │  Bitácora de eventos        │
            │              └───────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────────┐
│            MS-ANALITICA - Puerto 8002                      │
│            FastAPI + Boto3 + AWS Athena + S3               │
│            Reportes analíticos                             │
└───────────────────────────────────────────────────────────┘
```

---

## 2. Reglas del Equipo

| Regla | Descripción |
|-------|-------------|
| **Monorepo** | Todo el código en un solo repositorio. Cada MS en su propia carpeta. |
| **Contenedorización aislada** | Cada MS tiene su propio `Dockerfile` con sus dependencias. |
| **Un solo `.env` global** | Todas las credenciales en la raíz del proyecto. |
| **Orquestación centralizada** | Un único `docker-compose.yml` en la raíz. |

---

## 3. Microservicio MS-FLOTA (Gestión de Flota)

### Datos Generales

| Campo | Valor |
|-------|-------|
| **Responsable** | [Nombre del integrante] |
| **Stack** | Python + FastAPI + SQLAlchemy + MySQL |
| **Puerto interno** | 8000 |
| **Nombre del contenedor** | `ms_flota_app` |
| **Base de datos** | MySQL 8.0 (contenedor: `mysql_db`) |

### Entidades (Modelos)

#### Tabla `conductores`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | INT | PK, autoincrement |
| `nombre` | VARCHAR(100) | NOT NULL |
| `licencia` | VARCHAR(50) | NOT NULL, UNIQUE, INDEX |
| `telefono` | VARCHAR(20) | NOT NULL |
| `estado` | VARCHAR(20) | NOT NULL, default = `"disponible"` |

#### Tabla `vehiculos`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | INT | PK, autoincrement |
| `placa` | VARCHAR(20) | NOT NULL, UNIQUE, INDEX |
| `marca` | VARCHAR(50) | NOT NULL |
| `capacidad_kg` | FLOAT | NOT NULL |
| `conductor_id` | INT | NOT NULL, FK → `conductores.id` |

**Relación**: Un conductor → muchos vehículos.

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Mensaje de bienvenida |
| `GET` | `/health` | Health check (`{"status": "ok"}`) |
| `POST` | `/flota/conductores/` | Crear conductor |
| `GET` | `/flota/conductores/` | Listar todos los conductores (con sus vehículos) |
| `GET` | `/flota/conductores/{id}` | Obtener un conductor por ID (recomendado añadir) |
| `POST` | `/flota/vehiculos/` | Registrar vehículo |

### Ejemplo de Request/Response

**Crear conductor**:
```bash
POST /flota/conductores/
Body:
{
  "nombre": "Juan Pérez",
  "licencia": "LIC-001",
  "telefono": "555-1234"
}

Response (201 Created):
{
  "id": 1,
  "nombre": "Juan Pérez",
  "licencia": "LIC-001",
  "telefono": "555-1234",
  "estado": "disponible",
  "vehiculos": []
}
```

**Listar conductores**:
```bash
GET /flota/conductores/

Response (200 OK):
[
  {
    "id": 1,
    "nombre": "Juan Pérez",
    "licencia": "LIC-001",
    "telefono": "555-1234",
    "estado": "disponible",
    "vehiculos": [
      {
        "id": 1,
        "placa": "ABC-123",
        "marca": "Toyota",
        "capacidad_kg": 1500.0,
        "conductor_id": 1
      }
    ]
  }
]
```

### Instrucción para IA

> Desarrolla MS-FLOTA en FastAPI con SQLAlchemy. Conéctate a MySQL usando variables de entorno. Crea los modelos `Conductor` y `Vehiculo` con la relación 1:N. Implementa los endpoints de creación y listado. Incluye validación de licencia única y existencia de conductor al crear vehículo.

---

## 4. Microservicio MS-PEDIDOS (Gestión de Envíos)

### Datos Generales

| Campo | Valor |
|-------|-------|
| **Responsable** | [Nombre del integrante] |
| **Stack** | Java + Spring Boot 3 + JPA/Hibernate + PostgreSQL |
| **Puerto interno** | 8080 |
| **Nombre del contenedor** | `ms_pedidos_app` |
| **Base de datos** | PostgreSQL (contenedor: `postgres_db`) |

### Entidades (Modelos)

#### Tabla `pedidos`

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | Long | PK, autoincrement |
| `cliente_nombre` | String | NOT NULL |
| `direccion_origen` | String | NOT NULL |
| `direccion_destino` | String | NOT NULL |
| `estado` | String | `'creado'`, `'asignado'`, `'en_camino'`, `'entregado'` |
| `fecha_creacion` | Date | Auto now |

#### Tabla `detalle_paquete` (Relación 1:N con `pedidos`)

| Columna | Tipo | Restricciones |
|---------|------|---------------|
| `id` | Long | PK, autoincrement |
| `pedido_id` | Long | FK → `pedidos.id` |
| `peso_kg` | Float | NOT NULL |
| `dimensiones` | String | Ej: `"30x20x10 cm"` |
| `contenido_desc` | String | Descripción del contenido |

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/pedidos` | Crear un pedido con sus detalles |
| `GET` | `/pedidos` | Listar todos los pedidos (con paginación) |
| `PUT` | `/pedidos/{id}/estado` | Actualizar el estado del pedido |

### Ejemplo de Request/Response

**Crear pedido**:
```bash
POST /pedidos
Body:
{
  "cliente_nombre": "Ana Gómez",
  "direccion_origen": "Calle 123, Ciudad A",
  "direccion_destino": "Calle 456, Ciudad B",
  "detalles": [
    {
      "peso_kg": 5.5,
      "dimensiones": "30x20x10 cm",
      "contenido_desc": "Electrónicos"
    }
  ]
}
```

### Instrucción para IA

> Desarrolla MS-PEDIDOS en Spring Boot 3 con JPA/Hibernate. Usa PostgreSQL con credenciales desde variables de entorno. Crea las entidades `Pedido` y `DetallePaquete` con relación OneToMany. Implementa DTOs para request/response y un Controlador RESTful con los endpoints especificados.

---

## 5. Microservicio MS-EVENTOS (Historial y Tracking)

### Datos Generales

| Campo | Valor |
|-------|-------|
| **Responsable** | [Nombre del integrante] |
| **Stack** | Node.js + Express + Mongoose + MongoDB |
| **Puerto interno** | 3000 |
| **Nombre del contenedor** | `ms_eventos_app` |
| **Base de datos** | MongoDB (contenedor: `mongo_db`) |

### Colección MongoDB: `eventos`

**Estructura del documento**:
```json
{
  "_id": "ObjectId",
  "pedido_id": 123,           // Referencia al ID de MS-PEDIDOS
  "conductor_id": 5,          // Referencia al ID de MS-FLOTA
  "tipo_evento": "recogido",  // 'recogido', 'retraso', 'entregado'
  "descripcion": "Paquete recogido en origen",
  "timestamp": "2025-04-25T10:30:00Z",
  "coordenadas": {
    "lat": -34.6037,
    "lng": -58.3816
  }
}
```

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/eventos` | Registrar un nuevo evento |
| `GET` | `/eventos/pedido/{pedido_id}` | Línea de tiempo completa de un pedido |

### Ejemplo de Request/Response

**Registrar evento**:
```bash
POST /eventos
Body:
{
  "pedido_id": 123,
  "conductor_id": 5,
  "tipo_evento": "entregado",
  "descripcion": "Paquete entregado al cliente",
  "coordenadas": {
    "lat": -34.6037,
    "lng": -58.3816
  }
}
```

### Instrucción para IA

> Desarrolla MS-EVENTOS en Node.js con Express y Mongoose. Conéctate a MongoDB usando variables de entorno. Crea el esquema `Evento` con los campos especificados. Implementa endpoints para insertar eventos y consultar el historial por `pedido_id`.

---

## 6. Microservicio MS-ORQUESTADOR (Vista Unificada)

### Datos Generales

| Campo | Valor |
|-------|-------|
| **Responsable** | [Nombre del integrante] |
| **Stack** | Python + FastAPI + httpx |
| **Puerto interno** | 8001 |
| **Nombre del contenedor** | `ms_orquestador_app` |
| **Base de datos** | **NINGUNA** (solo orquesta llamadas HTTP) |

### Endpoints

| Método | Ruta | Descripción | Llama a |
|--------|------|-------------|---------|
| `GET` | `/dashboard/resumen` | Total de conductores + total de pedidos | MS-FLOTA (`/flota/conductores/`), MS-PEDIDOS (`/pedidos`) |
| `GET` | `/dashboard/envio/{pedido_id}` | Datos del pedido + línea de tiempo | MS-PEDIDOS (`/pedidos/{id}`), MS-EVENTOS (`/eventos/pedido/{id}`) |

### Ejemplo de Response

**GET /dashboard/resumen**:
```json
{
  "total_conductores": 10,
  "total_pedidos": 245,
  "fecha_consulta": "2025-04-25T12:00:00Z"
}
```

**GET /dashboard/envio/123**:
```json
{
  "pedido": {
    "id": 123,
    "cliente_nombre": "Ana Gómez",
    "estado": "entregado"
  },
  "linea_tiempo": [
    {
      "tipo_evento": "recogido",
      "timestamp": "2025-04-25T08:00:00Z",
      "descripcion": "Paquete recogido"
    },
    {
      "tipo_evento": "entregado",
      "timestamp": "2025-04-25T10:30:00Z",
      "descripcion": "Paquete entregado"
    }
  ]
}
```

### Instrucción para IA

> Desarrolla MS-ORQUESTADOR en FastAPI. NO uses bases de datos. Usa `httpx` de forma asíncrona para consumir:
> - `http://ms_flota_app:8000/flota/conductores/`
> - `http://ms_pedidos_app:8080/pedidos`
> - `http://ms_pedidos_app:8080/pedidos/{id}`
> - `http://ms_eventos_app:3000/eventos/pedido/{id}`
> 
> Consolida las respuestas en schemas Pydantic.

---

## 7. Microservicio MS-ANALITICA (Reportes AWS Athena)

### Datos Generales

| Campo | Valor |
|-------|-------|
| **Responsable** | [Nombre del integrante] (recomendado: Data Science) |
| **Stack** | Python + FastAPI + Boto3 + AWS Athena + S3 |
| **Puerto interno** | 8002 |
| **Nombre del contenedor** | `ms_analitica_app` |
| **Base de datos** | AWS Athena (consulta sobre CSV/JSON en S3) |

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/analitica/entregas-por-mes` | Envíos agrupados por mes |
| `GET` | `/analitica/conductores-actividad` | Cruce de datos de conductores y eventos |

### Flujo de trabajo

1. Un proceso de ingesta (ETL) sube archivos CSV/JSON a un bucket S3.
2. AWS Glue cataloga los datos como tablas.
3. MS-ANALITICA ejecuta queries SQL sobre Athena.
4. Athena lee desde S3 y devuelve resultados.
5. MS-ANALITICA formatea y devuelve JSON al frontend.

### Ejemplo de query Athena

```sql
SELECT 
  DATE_TRUNC('month', fecha_entrega) as mes,
  COUNT(*) as total_entregas
FROM pedidos
WHERE estado = 'entregado'
GROUP BY DATE_TRUNC('month', fecha_entrega)
ORDER BY mes DESC
```

### Instrucción para IA

> Desarrolla MS-ANALITICA en FastAPI. Usa `boto3` para conectarte a AWS Athena. Crea endpoints que:
> 1. Reciban la query SQL o tengan queries predefinidas.
> 2. Ejecuten `start_query_execution` en Athena.
> 3. Esperen la finalización con `get_query_execution`.
> 4. Obtengan resultados desde S3 usando `get_query_results`.
> 5. Retornen JSON formateado.

---

## 8. Estructura de Carpetas del Proyecto

```
Last-Mile-Delivery/
├── .env                           # Variables de entorno globales
├── docker-compose.yml             # Orquestación de todos los servicios
├── MS-FLOTA/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models/
│       │   └── flota.py
│       ├── schemas/
│       │   └── flota.py
│       └── routers/
│           └── flota.py
├── MS-PEDIDOS/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/
│       └── main/
│           └── java/
│               └── com/
│                   └── delivery/
│                       ├── PedidosApplication.java
│                       ├── controller/
│                       ├── entity/
│                       ├── repository/
│                       └── dto/
├── MS-EVENTOS/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── index.js
│       ├── models/
│       │   └── Evento.js
│       └── routes/
│           └── eventos.js
├── MS-ORQUESTADOR/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── schemas.py
│       └── services/
│           └── orquestador.py
└── MS-ANALITICA/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py
        ├── athena_client.py
        └── routers/
            └── analitica.py
```

---

## 9. Configuración del Entorno (.env)

Crea un archivo `.env` en la **raíz del proyecto**:

```env
# ===== BASE DE DATOS MS-FLOTA (MySQL) =====
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=mydb
MYSQL_USER=user
MYSQL_PASSWORD=password

# ===== BASE DE DATOS MS-PEDIDOS (PostgreSQL) =====
POSTGRES_DB=pedidosdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# ===== BASE DE DATOS MS-EVENTOS (MongoDB) =====
MONGO_INITDB_ROOT_USERNAME=mongo
MONGO_INITDB_ROOT_PASSWORD=mongo123
MONGO_DATABASE=eventosdb

# ===== AWS ATHENA (MS-ANALITICA) =====
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_REGION=us-east-1
ATHENA_S3_OUTPUT_LOCATION=s3://tu-bucket-athena-resultados/

# ===== CONEXIONES INTERNAS (no cambiar nombres) =====
MS_FLOTA_URL=http://ms_flota_app:8000
MS_PEDIDOS_URL=http://ms_pedidos_app:8080
MS_EVENTOS_URL=http://ms_eventos_app:3000
```

---

## 10. Docker Compose Global

`docker-compose.yml` en la raíz:

```yaml
version: '3.8'

services:
  # ===== BASES DE DATOS =====
  mysql_db:
    image: mysql:8.0
    container_name: mysql_db
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - delivery_network

  postgres_db:
    image: postgres:15
    container_name: postgres_db
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - delivery_network

  mongo_db:
    image: mongo:6
    container_name: mongo_db
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: ${MONGO_DATABASE}
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    networks:
      - delivery_network

  # ===== MICROSERVICIOS =====
  ms_flota_app:
    build: ./MS-FLOTA
    container_name: ms_flota_app
    ports:
      - "8000:8000"
    environment:
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
    depends_on:
      - mysql_db
    networks:
      - delivery_network

  ms_pedidos_app:
    build: ./MS-PEDIDOS
    container_name: ms_pedidos_app
    ports:
      - "8080:8080"
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    depends_on:
      - postgres_db
    networks:
      - delivery_network

  ms_eventos_app:
    build: ./MS-EVENTOS
    container_name: ms_eventos_app
    ports:
      - "3000:3000"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD}
      MONGO_DATABASE: ${MONGO_DATABASE}
    depends_on:
      - mongo_db
    networks:
      - delivery_network

  ms_orquestador_app:
    build: ./MS-ORQUESTADOR
    container_name: ms_orquestador_app
    ports:
      - "8001:8001"
    environment:
      MS_FLOTA_URL: ${MS_FLOTA_URL}
      MS_PEDIDOS_URL: ${MS_PEDIDOS_URL}
      MS_EVENTOS_URL: ${MS_EVENTOS_URL}
    depends_on:
      - ms_flota_app
      - ms_pedidos_app
      - ms_eventos_app
    networks:
      - delivery_network

  ms_analitica_app:
    build: ./MS-ANALITICA
    container_name: ms_analitica_app
    ports:
      - "8002:8002"
    environment:
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_REGION: ${AWS_REGION}
      ATHENA_S3_OUTPUT_LOCATION: ${ATHENA_S3_OUTPUT_LOCATION}
    networks:
      - delivery_network

# ===== VOLÚMENES =====
volumes:
  mysql_data:
  postgres_data:
  mongo_data:

# ===== REDES =====
networks:
  delivery_network:
    driver: bridge
```

---

## 11. Ejecución del Proyecto

### Prerrequisitos

- Docker Desktop instalado (incluye Docker Compose)
- Cuenta AWS configurada (para MS-ANALITICA, opcional al inicio)

### Comandos

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd Last-Mile-Delivery

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Construir y levantar todos los servicios
docker-compose up --build

# Levantar en segundo plano
docker-compose up --build -d

# Ver logs de un servicio específico
docker-compose logs -f ms_flota_app

# Detener todos los servicios
docker-compose down

# Detener y borrar volúmenes (reiniciar bases de datos)
docker-compose down -v
```

### Verificación

Una vez levantados todos los contenedores:

| Servicio | URL |
|----------|-----|
| MS-FLOTA Swagger | http://localhost:8000/docs |
| MS-PEDIDOS Swagger | http://localhost:8080/swagger-ui.html |
| MS-EVENTOS | http://localhost:3000 |
| MS-ORQUESTADOR | http://localhost:8001/docs |
| MS-ANALITICA | http://localhost:8002/docs |

---

## 12. Endpoints Globales por Microservicio

### MS-FLOTA (puerto 8000)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Bienvenida |
| GET | `/health` | Health check |
| POST | `/flota/conductores/` | Crear conductor |
| GET | `/flota/conductores/` | Listar conductores |
| POST | `/flota/vehiculos/` | Crear vehículo |

### MS-PEDIDOS (puerto 8080)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/pedidos` | Crear pedido |
| GET | `/pedidos` | Listar pedidos |
| PUT | `/pedidos/{id}/estado` | Actualizar estado |

### MS-EVENTOS (puerto 3000)

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/eventos` | Registrar evento |
| GET | `/eventos/pedido/{pedido_id}` | Línea de tiempo |

### MS-ORQUESTADOR (puerto 8001)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard/resumen` | Totales globales |
| GET | `/dashboard/envio/{pedido_id}` | Detalle completo de envío |

### MS-ANALITICA (puerto 8002)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/analitica/entregas-por-mes` | Entregas agrupadas por mes |
| GET | `/analitica/conductores-actividad` | Actividad de conductores |

---

## Apéndice: Recomendaciones adicionales

### Para MS-FLOTA (ya implementado)
- ✅ Agregar endpoint `GET /flota/conductores/{id}` para validación desde MS-EVENTOS.
- ✅ Incluir validación de que un conductor existe antes de asignar vehículo.

### Para MS-PEDIDOS
- Implementar paginación en `GET /pedidos` (page, size).
- Agregar endpoint `GET /pedidos/{id}` para consulta individual.

### Para MS-EVENTOS
- Agregar índice en `pedido_id` para búsquedas rápidas.
- Ordenar resultados por `timestamp` ascendente.

### Para MS-ORQUESTADOR
- Manejar timeouts y errores de servicios downstream.
- Cachear respuestas del dashboard/resumen (ej: cada 30 segundos).

### Para MS-ANALITICA
- Implementar caché de resultados para queries pesadas.
- Agregar endpoint de health check que verifique conexión con Athena.

---

## Notas finales

Este documento sirve como **única fuente de verdad** para el desarrollo de la plataforma. Cada desarrollador debe:

1. Seguir la estructura de carpetas definida.
2. Usar las variables de entorno del `.env` global.
3. Asegurar que su microservicio se levante correctamente con `docker-compose up`.
4. Documentar cualquier desviación en este mismo documento.

```
