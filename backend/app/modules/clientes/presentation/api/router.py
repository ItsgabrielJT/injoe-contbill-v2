from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.modules.clientes.application.dto import ContextoTenant
from app.modules.clientes.application.use_cases.actualizar_cliente import ActualizarClienteUseCase
from app.modules.clientes.application.use_cases.crear_cliente import CrearClienteUseCase
from app.modules.clientes.application.use_cases.eliminar_cliente import EliminarClienteUseCase
from app.modules.clientes.application.use_cases.listar_clientes import ListarClientesUseCase
from app.modules.clientes.application.use_cases.obtener_cliente import ObtenerClienteUseCase
from app.modules.clientes.domain.entities import TipoCliente
from app.modules.clientes.presentation.api.dependencies import (
    get_actualizar_cliente_use_case,
    get_crear_cliente_use_case,
    get_eliminar_cliente_use_case,
    get_listar_clientes_use_case,
    get_obtener_cliente_use_case,
    get_tenant,
)
from app.modules.clientes.presentation.api.schemas import (
    ClienteCreateRequest,
    ClienteDataResponse,
    ClienteListResponse,
    ClienteResponse,
    ClienteUpdateRequest,
    listar_clientes_query,
)

clientes_router = APIRouter(prefix="/clientes", tags=["clientes"])


@clientes_router.get("/", response_model=ClienteListResponse)
async def listar_clientes(
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[ListarClientesUseCase, Depends(get_listar_clientes_use_case)],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=200),
    search: str | None = Query(None),
    tipo_cliente: TipoCliente | None = Query(None),
    activo: bool | None = Query(None),
) -> ClienteListResponse:
    query = listar_clientes_query(page, size, search, tipo_cliente, activo)
    clientes, total = await use_case.execute(query, tenant)
    pages = (total + size - 1) // size if size else 1
    return ClienteListResponse(
        data=[ClienteResponse.from_domain(cliente) for cliente in clientes],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )


@clientes_router.get("/{cliente_id}", response_model=ClienteDataResponse)
async def obtener_cliente(
    cliente_id: int,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[ObtenerClienteUseCase, Depends(get_obtener_cliente_use_case)],
) -> ClienteDataResponse:
    cliente = await use_case.execute(cliente_id, tenant)
    return ClienteDataResponse(data=ClienteResponse.from_domain(cliente), message="Cliente obtenido")


@clientes_router.post("/", response_model=ClienteDataResponse, status_code=status.HTTP_201_CREATED)
async def crear_cliente(
    request: ClienteCreateRequest,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[CrearClienteUseCase, Depends(get_crear_cliente_use_case)],
) -> ClienteDataResponse:
    cliente = await use_case.execute(request.to_command(), tenant)
    return ClienteDataResponse(data=ClienteResponse.from_domain(cliente), message="Cliente creado exitosamente")


@clientes_router.put("/{cliente_id}", response_model=ClienteDataResponse)
async def actualizar_cliente(
    cliente_id: int,
    request: ClienteUpdateRequest,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[ActualizarClienteUseCase, Depends(get_actualizar_cliente_use_case)],
) -> ClienteDataResponse:
    cliente = await use_case.execute(request.to_command(cliente_id), tenant)
    return ClienteDataResponse(data=ClienteResponse.from_domain(cliente), message="Cliente actualizado")


@clientes_router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cliente(
    cliente_id: int,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[EliminarClienteUseCase, Depends(get_eliminar_cliente_use_case)],
) -> Response:
    await use_case.execute(cliente_id, tenant)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
