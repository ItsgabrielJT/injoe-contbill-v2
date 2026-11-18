from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, Response, status
from fastapi.responses import FileResponse

from app.modules.configuracion.application.dto import ActualizarSriIdCommand, ContextoTenant
from app.modules.configuracion.application.use_cases.gestionar_empresa import (
    ActualizarEmpresaUseCase,
    ActualizarSriIdUseCase,
    ObtenerEmpresaUseCase,
)
from app.modules.configuracion.application.use_cases.gestionar_puntos import (
    EliminarPuntoUseCase,
    GuardarPuntoUseCase,
    ListarPuntosUseCase,
)
from app.modules.configuracion.presentation.api.dependencies import (
    get_actualizar_empresa,
    get_actualizar_sri_id,
    get_eliminar_punto,
    get_eliminar_logo,
    get_guardar_punto,
    get_listar_puntos,
    get_obtener_empresa,
    get_subir_logo,
    get_tenant,
)
from app.modules.configuracion.presentation.api.schemas import (
    EmpresaDataResponse,
    EmpresaResponse,
    EmpresaUpdateRequest,
    PuntoDataResponse,
    PuntoListResponse,
    PuntoRequest,
    PuntoResponse,
    SriIdRequest,
)
from app.modules.configuracion.application.use_cases.gestionar_empresa import EliminarLogoUseCase, SubirLogoUseCase
from app.modules.configuracion.infrastructure.logo_storage import ruta_logo_empresa
from app.modules.configuracion.domain.exceptions import EmpresaNoEncontrada

empresa_router = APIRouter(prefix="/empresa", tags=["configuración"])
puntos_router = APIRouter(prefix="/puntos-emision", tags=["configuración"])


@empresa_router.get("/", response_model=EmpresaDataResponse)
async def obtener_empresa(
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[ObtenerEmpresaUseCase, Depends(get_obtener_empresa)],
) -> EmpresaDataResponse:
    empresa = await use_case.execute(tenant.empresa_id)
    return EmpresaDataResponse(data=EmpresaResponse.from_domain(empresa), message="Empresa obtenida")


@empresa_router.put("/", response_model=EmpresaDataResponse)
async def actualizar_empresa(
    request: EmpresaUpdateRequest,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[ActualizarEmpresaUseCase, Depends(get_actualizar_empresa)],
) -> EmpresaDataResponse:
    empresa = await use_case.execute(request.to_command(), tenant.empresa_id)
    return EmpresaDataResponse(data=EmpresaResponse.from_domain(empresa), message="Empresa actualizada")


@empresa_router.patch("/sri-id", response_model=EmpresaDataResponse)
async def actualizar_sri_id(
    request: SriIdRequest,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[ActualizarSriIdUseCase, Depends(get_actualizar_sri_id)],
) -> EmpresaDataResponse:
    empresa = await use_case.execute(ActualizarSriIdCommand(sri_id=request.sri_id), tenant.empresa_id)
    return EmpresaDataResponse(data=EmpresaResponse.from_domain(empresa), message="Certificado vinculado")


@empresa_router.post("/logo", response_model=EmpresaDataResponse)
async def subir_logo(
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[SubirLogoUseCase, Depends(get_subir_logo)],
    archivo: UploadFile = File(...),
) -> EmpresaDataResponse:
    contenido = await archivo.read()
    empresa = await use_case.execute(tenant.empresa_id, contenido, archivo.filename, archivo.content_type)
    return EmpresaDataResponse(data=EmpresaResponse.from_domain(empresa), message="Logo guardado")


@empresa_router.get("/logo")
async def obtener_logo(
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
):
    ruta = ruta_logo_empresa(tenant.empresa_id)
    if not ruta.is_file():
        raise EmpresaNoEncontrada("La empresa no tiene un logo cargado")
    return FileResponse(ruta, media_type="image/png", filename="logo.png")


@empresa_router.delete("/logo", response_model=EmpresaDataResponse)
async def eliminar_logo(
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[EliminarLogoUseCase, Depends(get_eliminar_logo)],
) -> EmpresaDataResponse:
    empresa = await use_case.execute(tenant.empresa_id)
    return EmpresaDataResponse(data=EmpresaResponse.from_domain(empresa), message="Logo eliminado")


@puntos_router.get("/", response_model=PuntoListResponse)
async def listar_puntos(
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[ListarPuntosUseCase, Depends(get_listar_puntos)],
) -> PuntoListResponse:
    puntos = await use_case.execute(tenant.empresa_id)
    return PuntoListResponse(data=[PuntoResponse.from_domain(punto) for punto in puntos])


@puntos_router.post("/", response_model=PuntoDataResponse, status_code=status.HTTP_201_CREATED)
async def crear_punto(
    request: PuntoRequest,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[GuardarPuntoUseCase, Depends(get_guardar_punto)],
) -> PuntoDataResponse:
    punto = await use_case.execute(request.to_command(), tenant)
    return PuntoDataResponse(data=PuntoResponse.from_domain(punto), message="Punto de emisión creado")


@puntos_router.put("/{punto_id}", response_model=PuntoDataResponse)
async def actualizar_punto(
    punto_id: int,
    request: PuntoRequest,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[GuardarPuntoUseCase, Depends(get_guardar_punto)],
) -> PuntoDataResponse:
    punto = await use_case.execute(request.to_command(punto_id), tenant)
    return PuntoDataResponse(data=PuntoResponse.from_domain(punto), message="Punto de emisión actualizado")


@puntos_router.delete("/{punto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_punto(
    punto_id: int,
    tenant: Annotated[ContextoTenant, Depends(get_tenant)],
    use_case: Annotated[EliminarPuntoUseCase, Depends(get_eliminar_punto)],
) -> Response:
    await use_case.execute(punto_id, tenant.empresa_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
