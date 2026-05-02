from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from app.services.orquestador import obtener_resumen, obtener_detalle_envio

app = FastAPI(
    title="MS-ORQUESTADOR",
    description="BFF - Orquestador de microservicios Last Mile Delivery",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"mensaje": "MS-ORQUESTADOR - Last Mile Delivery", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok", "servicio": "ms-orquestador"}


@app.get("/dashboard/resumen")
async def dashboard_resumen():
    datos = await obtener_resumen()
    return {
        "total_conductores": datos["total_conductores"],
        "total_pedidos": datos["total_pedidos"],
        "fecha_consulta": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/dashboard/envio/{pedido_id}")
async def dashboard_envio(pedido_id: int):
    detalle = await obtener_detalle_envio(pedido_id)
    if detalle is None:
        raise HTTPException(status_code=404, detail=f"Pedido {pedido_id} no encontrado")
    return detalle
