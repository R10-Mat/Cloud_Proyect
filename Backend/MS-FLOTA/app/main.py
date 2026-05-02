from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import Base, engine
from app.models.flota import Conductor, Vehiculo
from app.routers.flota import router as flota_router

app = FastAPI(
    title="MS-FLOTA API",
    description="Microservicio de gestión de flota: conductores y vehículos.",
    version="1.0.0",
)

# Configurar CORS global (permite cualquier origen: dev local + AWS Amplify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flota_router)


@app.on_event("startup")
def on_startup_create_tables():
    import time
    from sqlalchemy.exc import OperationalError

    max_attempts = 20
    attempt = 0
    while attempt < max_attempts:
        try:
            # intentamos conectar y crear las tablas
            with engine.connect():
                Base.metadata.create_all(bind=engine)
            break
        except OperationalError:
            attempt += 1
            time.sleep(1)
    if attempt == max_attempts:
        # Si no pudimos conectar, dejamos que la app continúe y falle visiblemente en logs
        pass


@app.get("/")
def root():
    return {"message": "MS-FLOTA corriendo correctamente"}


@app.get("/health")
def health():
    return {"status": "ok"}
