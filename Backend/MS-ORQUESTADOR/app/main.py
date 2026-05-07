from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime, timezone

from app.services.orquestador import obtener_resumen, obtener_detalle_envio, crear_pedido

app = FastAPI(
    title="MS-ORQUESTADOR",
    description="BFF - Orquestador de microservicios Last Mile Delivery",
    version="1.0.0",
)

# CORS: permitir requests desde Amplify y cualquier origen
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


@app.post("/dashboard/pedido", status_code=201)
async def dashboard_crear_pedido(datos_pedido: dict):
    try:
        resultado = await crear_pedido(datos_pedido)
        return resultado
    except httpx.HTTPStatusError as exc:
        # Re-raise la excepción del backend de pedidos con su mismo código y detalle
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Error en MS-PEDIDOS: {exc.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
