from fastapi import FastAPI

from app.routers.analitica import router as analitica_router

app = FastAPI(
    title="MS-ANALITICA",
    description="Microservicio de reportes analíticos con AWS Athena - Last Mile Delivery",
    version="1.0.0",
)

app.include_router(analitica_router)


@app.get("/")
def root():
    return {"mensaje": "MS-ANALITICA - Last Mile Delivery", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok", "servicio": "ms-analitica"}
