from fastapi import FastAPI

from app.routers.orquestador import router as orquestador_router

app = FastAPI(
    title="MS-ORQUESTADOR API",
    description="Microservicio orquestador: coordina la asignación de flota a pedidos.",
    version="1.0.0",
)

app.include_router(orquestador_router)


@app.get("/")
def root():
    return {"message": "MS-ORQUESTADOR corriendo correctamente"}


@app.get("/health")
def health():
    return {"status": "ok"}
