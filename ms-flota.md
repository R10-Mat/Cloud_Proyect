# MS-FLOTA — Microservicio de Gestión de Flota

Microservicio REST API para la gestión de **conductores** y **vehículos** de la plataforma de logística Last-Mile Delivery.

**Stack:** FastAPI + SQLAlchemy + MySQL + Docker

---

## Estructura del Microservicio

```
Backend/MS-FLOTA/
├── Dockerfile
├── requirements.txt
└── app/
    ├── __init__.py
    ├── database.py          ← Conexión a MySQL
    ├── main.py              ← Punto de entrada de la app
    ├── models/
    │   ├── __init__.py
    │   └── flota.py         ← Tablas de la base de datos
    ├── schemas/
    │   ├── __init__.py
    │   └── flota.py         ← Validación de datos (entrada/salida)
    └── routers/
        ├── __init__.py
        └── flota.py         ← Endpoints REST
```

---

## Qué Hace Cada Archivo

### `app/database.py`

Configura la conexión a MySQL. Lee las credenciales desde variables de entorno y construye la URL de conexión con el driver PyMySQL.

| Componente | Para qué sirve |
|---|---|
| `DATABASE_URL` | URL completa: `mysql+pymysql://user:password@mysql_db:3306/mydb` |
| `engine` | Motor de SQLAlchemy que maneja la conexión a MySQL |
| `SessionLocal` | Crea sesiones de base de datos para cada request |
| `Base` | Clase base de la que heredan todos los modelos (tablas) |
| `get_db()` | Función que abre una sesión, la entrega al endpoint, y la cierra al terminar |

### `app/models/flota.py`

Define las 2 tablas en la base de datos con una relación **1 conductor → N vehículos**.

**Tabla `conductores`:**

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | INT | Primary Key, autoincrement |
| `nombre` | VARCHAR(100) | NOT NULL |
| `licencia` | VARCHAR(50) | NOT NULL, UNIQUE, INDEX |
| `telefono` | VARCHAR(20) | NOT NULL |
| `estado` | VARCHAR(20) | NOT NULL, default = `"disponible"` |

**Tabla `vehiculos`:**

| Columna | Tipo | Restricciones |
|---|---|---|
| `id` | INT | Primary Key, autoincrement |
| `placa` | VARCHAR(20) | NOT NULL, UNIQUE, INDEX |
| `marca` | VARCHAR(50) | NOT NULL |
| `capacidad_kg` | FLOAT | NOT NULL |
| `conductor_id` | INT | NOT NULL, Foreign Key → `conductores.id` |

**Relación:** Un conductor puede tener muchos vehículos. Un vehículo pertenece a un solo conductor.

### `app/schemas/flota.py`

Define qué datos acepta y devuelve cada endpoint usando Pydantic.

**Schemas de Vehículo:**

| Schema | Campos | Se usa en |
|---|---|---|
| `VehiculoCreate` | `placa`, `marca`, `capacidad_kg`, `conductor_id` | Body del POST |
| `VehiculoResponse` | Los mismos + `id` | Respuesta del API |

**Schemas de Conductor:**

| Schema | Campos | Se usa en |
|---|---|---|
| `ConductorCreate` | `nombre`, `licencia`, `telefono`, `estado` (opcional) | Body del POST |
| `ConductorResponse` | Los mismos + `id` + `vehiculos[]` | Respuesta del API |

### `app/routers/flota.py`

Contiene los 3 endpoints del Hito 1. Todos están bajo el prefijo `/flota`.

### `app/main.py`

Punto de entrada. Inicializa FastAPI, crea las tablas automáticamente al arrancar, y registra el router.

---

## Endpoints

### `POST /flota/conductores/` — Crear un conductor

**Qué hace:** Crea un nuevo conductor. Verifica que la licencia no exista ya en la base de datos.

**Body (JSON que se envía):**
```json
{
  "nombre": "Juan Pérez",
  "licencia": "LIC-001",
  "telefono": "555-1234"
}
```

> Nota: `estado` es opcional. Si no se envía, se asigna `"disponible"` automáticamente.

**Respuesta exitosa (201 Created):**
```json
{
  "nombre": "Juan Pérez",
  "licencia": "LIC-001",
  "telefono": "555-1234",
  "estado": "disponible",
  "id": 1,
  "vehiculos": []
}
```

**Error — licencia duplicada (400 Bad Request):**
```json
{
  "detail": "Ya existe un conductor con la licencia 'LIC-001'."
}
```

---

### `GET /flota/conductores/` — Listar todos los conductores

**Qué hace:** Devuelve todos los conductores registrados. Cada conductor incluye la lista de sus vehículos asignados.

**No requiere body ni parámetros.**

**Respuesta exitosa (200 OK):**
```json
[
  {
    "nombre": "Juan Pérez",
    "licencia": "LIC-001",
    "telefono": "555-1234",
    "estado": "disponible",
    "id": 1,
    "vehiculos": [
      {
        "placa": "ABC-123",
        "marca": "Toyota",
        "capacidad_kg": 1500.0,
        "conductor_id": 1,
        "id": 1
      }
    ]
  },
  {
    "nombre": "María López",
    "licencia": "LIC-002",
    "telefono": "555-5678",
    "estado": "disponible",
    "id": 2,
    "vehiculos": []
  }
]
```

---

### `POST /flota/vehiculos/` — Registrar un vehículo

**Qué hace:** Registra un vehículo nuevo. Valida que el `conductor_id` exista en la tabla de conductores antes de crear.

**Body (JSON que se envía):**
```json
{
  "placa": "ABC-123",
  "marca": "Toyota",
  "capacidad_kg": 1500.0,
  "conductor_id": 1
}
```

**Respuesta exitosa (201 Created):**
```json
{
  "placa": "ABC-123",
  "marca": "Toyota",
  "capacidad_kg": 1500.0,
  "conductor_id": 1,
  "id": 1
}
```

**Error — conductor no existe (404 Not Found):**
```json
{
  "detail": "No existe un conductor con id 99."
}
```

---

### Endpoints base

| Método | Ruta | Respuesta |
|---|---|---|
| `GET` | `/` | `{"message": "MS-FLOTA corriendo correctamente"}` |
| `GET` | `/health` | `{"status": "ok"}` |

---

## Configuración del `.env`

Crear un archivo `.env` en la **raíz del proyecto** (donde está `docker_compose.yml`) con:

```env
MYSQL_ROOT_PASSWORD=root
MYSQL_DATABASE=mydb
MYSQL_USER=user
MYSQL_PASSWORD=password
```

> Este archivo está en el `.gitignore`, cada persona debe crearlo en su máquina.

---

## Cómo Ejecutar

### Requisito

Tener instalado **Docker Desktop** (incluye Docker Compose).

### Comandos

```bash
# Desde la raíz del proyecto (donde está docker_compose.yml)

# Construir y levantar los contenedores
docker-compose -f docker_compose.yml up --build

# Para correr en segundo plano
docker-compose -f docker_compose.yml up --build -d

# Para detener
docker-compose -f docker_compose.yml down

# Para detener y borrar los datos de MySQL
docker-compose -f docker_compose.yml down -v
```

### Qué pasa al ejecutar

1. Docker levanta el contenedor `mysql_db` con MySQL 8.0 y crea la base de datos `mydb`
2. Docker construye y levanta el contenedor `ms_flota_app` con FastAPI
3. Al iniciar, FastAPI crea automáticamente las tablas `conductores` y `vehiculos` en MySQL
4. La API queda disponible en `http://localhost:8000`

---

## Cómo Inyectar Datos

### Opción 1: Swagger UI (recomendado)

Abrir `http://localhost:8000/docs` en el navegador. Ahí aparecen todos los endpoints con un botón **"Try it out"** para probar directamente.

**Orden para inyectar datos:**
1. Primero crear conductores con `POST /flota/conductores/`
2. Después crear vehículos con `POST /flota/vehiculos/` (necesita el `id` de un conductor que ya exista)
3. Verificar con `GET /flota/conductores/` que todo se registró bien

### Opción 2: curl desde terminal

```bash
# Crear conductor
curl -X POST http://localhost:8000/flota/conductores/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Juan Pérez", "licencia": "LIC-001", "telefono": "555-1234"}'

# Crear vehículo (conductor_id debe existir)
curl -X POST http://localhost:8000/flota/vehiculos/ \
  -H "Content-Type: application/json" \
  -d '{"placa": "ABC-123", "marca": "Toyota", "capacidad_kg": 1500.0, "conductor_id": 1}'

# Listar todos los conductores con sus vehículos
curl http://localhost:8000/flota/conductores/
```

### Opción 3: Postman

Importar los endpoints manualmente o usar la URL de OpenAPI: `http://localhost:8000/openapi.json`

---

## Resumen de URLs

| URL | Qué es |
|---|---|
| `http://localhost:8000` | Raíz del API |
| `http://localhost:8000/docs` | Swagger UI (interfaz visual para probar endpoints) |
| `http://localhost:8000/redoc` | Documentación alternativa |
| `http://localhost:8000/health` | Health check |
| `http://localhost:8000/openapi.json` | Spec OpenAPI en JSON |
