from typing import Protocol

from app.modules.clientes.application.dto import ListarClientesQuery
from app.modules.clientes.domain.entities import Cliente


class ClienteRepository(Protocol):
    async def obtener_por_id(
        self,
        cliente_id: int,
        empresa_id: int,
        punto_emision_id: int,
    ) -> Cliente | None: ...

    async def obtener_por_identificacion(
        self,
        identificacion: str,
        empresa_id: int,
        punto_emision_id: int,
    ) -> Cliente | None: ...

    async def listar(
        self,
        empresa_id: int,
        punto_emision_id: int,
        query: ListarClientesQuery,
    ) -> tuple[list[Cliente], int]: ...

    async def guardar(self, cliente: Cliente) -> Cliente: ...

    async def eliminar(
        self,
        cliente_id: int,
        empresa_id: int,
        punto_emision_id: int,
    ) -> bool: ...
