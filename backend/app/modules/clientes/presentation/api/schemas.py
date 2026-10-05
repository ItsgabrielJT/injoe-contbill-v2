from datetime import date, datetime

from pydantic import BaseModel, Field

from app.modules.clientes.application.dto import ActualizarClienteCommand, CrearClienteCommand, ListarClientesQuery
from app.modules.clientes.domain.entities import Cliente, TipoCliente


class ClienteCreateRequest(BaseModel):
    identificacion: str = Field(..., min_length=10, max_length=13)
    nombres: str = Field(..., min_length=2, max_length=255)
    correos: list[str] = Field(..., min_length=1)
    tipo_cliente: TipoCliente = TipoCliente.PERSONA_NATURAL
    razon_social: str | None = None
    fecha_nacimiento: date | None = None
    provincia: str | None = None
    canton: str | None = None
    parroquia: str | None = None
    direcciones: list[str] = Field(default_factory=list)
    telefonos: list[str] = Field(default_factory=list)
    indice_direccion_principal: int | None = None
    indice_telefono_principal: int | None = None
    indice_correo_principal: int | None = 0
    direccion_fiscal: str | None = None
    telefono_fiscal: str | None = None
    correo_fiscal: str | None = None
    notas: str | None = None
    activo: bool = True

    def to_command(self) -> CrearClienteCommand:
        return CrearClienteCommand(**self.model_dump())


class ClienteUpdateRequest(BaseModel):
    identificacion: str | None = Field(None, min_length=10, max_length=13)
    nombres: str | None = Field(None, min_length=2, max_length=255)
    correos: list[str] | None = None
    tipo_cliente: TipoCliente | None = None
    razon_social: str | None = None
    fecha_nacimiento: date | None = None
    provincia: str | None = None
    canton: str | None = None
    parroquia: str | None = None
    direcciones: list[str] | None = None
    telefonos: list[str] | None = None
    indice_direccion_principal: int | None = None
    indice_telefono_principal: int | None = None
    indice_correo_principal: int | None = None
    direccion_fiscal: str | None = None
    telefono_fiscal: str | None = None
    correo_fiscal: str | None = None
    notas: str | None = None
    activo: bool | None = None

    def to_command(self, cliente_id: int) -> ActualizarClienteCommand:
        return ActualizarClienteCommand(cliente_id=cliente_id, **self.model_dump())


class ClienteResponse(BaseModel):
    id: int
    empresa_id: int
    punto_emision_id: int
    identificacion: str
    tipo_cliente: TipoCliente
    nombres: str
    razon_social: str | None = None
    fecha_nacimiento: date | None = None
    provincia: str | None = None
    canton: str | None = None
    parroquia: str | None = None
    direcciones: list[str] = []
    telefonos: list[str] = []
    correos: list[str] = []
    indice_direccion_principal: int | None = None
    indice_telefono_principal: int | None = None
    indice_correo_principal: int | None = None
    direccion_fiscal: str | None = None
    telefono_fiscal: str | None = None
    correo_fiscal: str | None = None
    notas: str | None = None
    activo: bool
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None
    correo_principal: str | None = None

    @classmethod
    def from_domain(cls, cliente: Cliente) -> "ClienteResponse":
        return cls(
            id=cliente.id or 0,
            empresa_id=cliente.empresa_id,
            punto_emision_id=cliente.punto_emision_id,
            identificacion=cliente.identificacion,
            tipo_cliente=cliente.tipo_cliente,
            nombres=cliente.nombres,
            razon_social=cliente.razon_social,
            fecha_nacimiento=cliente.fecha_nacimiento,
            provincia=cliente.provincia,
            canton=cliente.canton,
            parroquia=cliente.parroquia,
            direcciones=cliente.direcciones,
            telefonos=cliente.telefonos,
            correos=cliente.correos,
            indice_direccion_principal=cliente.indice_direccion_principal,
            indice_telefono_principal=cliente.indice_telefono_principal,
            indice_correo_principal=cliente.indice_correo_principal,
            direccion_fiscal=cliente.direccion_fiscal,
            telefono_fiscal=cliente.telefono_fiscal,
            correo_fiscal=cliente.correo_fiscal,
            notas=cliente.notas,
            activo=cliente.activo,
            creado_en=cliente.creado_en,
            actualizado_en=cliente.actualizado_en,
            correo_principal=cliente.correo_principal,
        )


class ClienteListResponse(BaseModel):
    data: list[ClienteResponse]
    total: int
    page: int
    size: int
    pages: int
    message: str = "Lista de clientes obtenida"


class ClienteDataResponse(BaseModel):
    data: ClienteResponse
    message: str


def listar_clientes_query(
    page: int,
    size: int,
    search: str | None,
    tipo_cliente: TipoCliente | None,
    activo: bool | None,
) -> ListarClientesQuery:
    return ListarClientesQuery(
        page=page,
        size=size,
        search=search,
        tipo_cliente=tipo_cliente,
        activo=activo,
    )
