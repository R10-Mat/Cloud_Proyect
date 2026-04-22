from fastapi import FastAPI

from app.database import Base, engine
from app.models.flota import Conductor, Vehiculo
from app.routers.flota import router as flota_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS-FLOTA API",
    description="Microservicio de gestión de flota: conductores y vehículos.",
    version="1.0.0",
)

app.include_router(flota_router)


@app.get("/")
def root():
    return {"message": "MS-FLOTA corriendo correctamente"}


@app.get("/health")
def health():
    return {"status": "ok"}
