import os

from app.services.orquestador import OrquestadorService

FLOTA_URL = os.getenv("FLOTA_URL", "http://ms_flota:8000")


def get_orquestador_service() -> OrquestadorService:
    return OrquestadorService(flota_url=FLOTA_URL)
