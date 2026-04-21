from fastapi import FastAPI
from app.database import Base, engine

# Crea las tablas automáticamente al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI corriendo correctamente"}

@app.get("/health")
def health():
    return {"status": "ok"}
