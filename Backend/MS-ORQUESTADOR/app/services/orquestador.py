import httpx
from fastapi import HTTPException, status

from app.schemas.orquestador import (
    AsignarPedidoRequest,
    AsignarPedidoResponse,
    CompletarPedidoRequest,
    CompletarPedidoResponse,
    ConductorDisponibleResponse,
)


class OrquestadorService:
    def __init__(self, flota_url: str):
        self.flota_url = flota_url

    async def _get_conductor(self, client: httpx.AsyncClient, conductor_id: int) -> dict:
        resp = await client.get(f"{self.flota_url}/flota/conductores/{conductor_id}")
        if resp.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conductor con id {conductor_id} no encontrado en MS-FLOTA.",
            )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error al consultar MS-FLOTA.",
            )
        return resp.json()

    async def _get_vehiculo(self, client: httpx.AsyncClient, vehiculo_id: int) -> dict:
        resp = await client.get(f"{self.flota_url}/flota/vehiculos/{vehiculo_id}")
        if resp.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehículo con id {vehiculo_id} no encontrado en MS-FLOTA.",
            )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error al consultar MS-FLOTA.",
            )
        return resp.json()

    async def _actualizar_estado_conductor(
        self, client: httpx.AsyncClient, conductor_id: int, estado: str
    ) -> None:
        resp = await client.patch(
            f"{self.flota_url}/flota/conductores/{conductor_id}",
            json={"estado": estado},
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al actualizar estado del conductor en MS-FLOTA.",
            )

    async def asignar_pedido(self, data: AsignarPedidoRequest) -> AsignarPedidoResponse:
        async with httpx.AsyncClient() as client:
            conductor = await self._get_conductor(client, data.conductor_id)

            if conductor["estado"] != "disponible":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El conductor '{conductor['nombre']}' no está disponible (estado: {conductor['estado']}).",
                )

            vehiculo = await self._get_vehiculo(client, data.vehiculo_id)

            if vehiculo["conductor_id"] != data.conductor_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El vehículo {data.vehiculo_id} no pertenece al conductor {data.conductor_id}.",
                )

            await self._actualizar_estado_conductor(client, data.conductor_id, "ocupado")

        return AsignarPedidoResponse(
            pedido_id=data.pedido_id,
            conductor_id=data.conductor_id,
            vehiculo_id=data.vehiculo_id,
            estado="asignado",
            mensaje=f"Conductor '{conductor['nombre']}' asignado al pedido {data.pedido_id}.",
        )

    async def completar_pedido(self, data: CompletarPedidoRequest) -> CompletarPedidoResponse:
        async with httpx.AsyncClient() as client:
            await self._get_conductor(client, data.conductor_id)
            await self._actualizar_estado_conductor(client, data.conductor_id, "disponible")

        return CompletarPedidoResponse(
            pedido_id=data.pedido_id,
            conductor_id=data.conductor_id,
            estado="completado",
            mensaje=f"Pedido {data.pedido_id} completado. Conductor {data.conductor_id} liberado.",
        )

    async def obtener_conductores_disponibles(self) -> list[ConductorDisponibleResponse]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.flota_url}/flota/conductores/")
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Error al consultar conductores en MS-FLOTA.",
                )
            conductores = resp.json()

        return [c for c in conductores if c["estado"] == "disponible"]
