from sqlalchemy import String, cast, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clientes.application.dto import ListarClientesQuery
from app.modules.clientes.domain.entities import Cliente
from app.modules.clientes.infrastructure.persistence.models import ClienteModel


def _as_list(valor: object) -> list[str]:
    if isinstance(valor, list):
        return [str(item) for item in valor]
    return []


def _cliente_desde_modelo(model: ClienteModel) -> Cliente:
    return Cliente(
        id=model.id,
        empresa_id=model.empresa_id,
        punto_emision_id=model.punto_emision_id,
        identificacion=model.identificacion,
        tipo_cliente=model.tipo_cliente,
        nombres=model.nombres,
        razon_social=model.razon_social,
        fecha_nacimiento=model.fecha_nacimiento,
        provincia=model.provincia,
        canton=model.canton,
        parroquia=model.parroquia,
        direcciones=_as_list(model.direcciones),
        telefonos=_as_list(model.telefonos),
        correos=_as_list(model.correos),
        indice_direccion_principal=model.indice_direccion_principal,
        indice_telefono_principal=model.indice_telefono_principal,
        indice_correo_principal=model.indice_correo_principal,
        direccion_fiscal=model.direccion_fiscal,
        telefono_fiscal=model.telefono_fiscal,
        correo_fiscal=model.correo_fiscal,
        notas=model.notas,
        activo=model.activo,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


class SqlAlchemyClienteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _alcance(self, empresa_id: int, punto_emision_id: int):
        return (
            ClienteModel.empresa_id == empresa_id,
            ClienteModel.punto_emision_id == punto_emision_id,
        )

    async def obtener_por_id(
        self,
        cliente_id: int,
        empresa_id: int,
        punto_emision_id: int,
    ) -> Cliente | None:
        result = await self.session.execute(
            select(ClienteModel).where(
                ClienteModel.id == cliente_id,
                *self._alcance(empresa_id, punto_emision_id),
            )
        )
        model = result.scalar_one_or_none()
        return _cliente_desde_modelo(model) if model else None

    async def obtener_por_identificacion(
        self,
        identificacion: str,
        empresa_id: int,
        punto_emision_id: int,
    ) -> Cliente | None:
        result = await self.session.execute(
            select(ClienteModel).where(
                ClienteModel.identificacion == identificacion,
                *self._alcance(empresa_id, punto_emision_id),
            )
        )
        model = result.scalar_one_or_none()
        return _cliente_desde_modelo(model) if model else None

    async def listar(
        self,
        empresa_id: int,
        punto_emision_id: int,
        query: ListarClientesQuery,
    ) -> tuple[list[Cliente], int]:
        stmt = select(ClienteModel).where(*self._alcance(empresa_id, punto_emision_id))
        if query.search:
            termino = f"%{query.search.strip()}%"
            stmt = stmt.where(
                or_(
                    ClienteModel.nombres.ilike(termino),
                    ClienteModel.razon_social.ilike(termino),
                    ClienteModel.identificacion.ilike(termino),
                    cast(ClienteModel.correos, String).ilike(termino),
                )
            )
        if query.tipo_cliente:
            stmt = stmt.where(ClienteModel.tipo_cliente == query.tipo_cliente)
        if query.activo is not None:
            stmt = stmt.where(ClienteModel.activo == query.activo)

        total = (await self.session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
        stmt = stmt.order_by(func.lower(ClienteModel.nombres), ClienteModel.id)
        stmt = stmt.offset((query.page - 1) * query.size).limit(query.size)
        models = list((await self.session.execute(stmt)).scalars().all())
        return [_cliente_desde_modelo(model) for model in models], total

    async def guardar(self, cliente: Cliente) -> Cliente:
        if cliente.id is None:
            model = ClienteModel(
                empresa_id=cliente.empresa_id,
                punto_emision_id=cliente.punto_emision_id,
            )
            self.session.add(model)
        else:
            result = await self.session.execute(select(ClienteModel).where(ClienteModel.id == cliente.id))
            model = result.scalar_one()

        model.identificacion = cliente.identificacion
        model.tipo_cliente = cliente.tipo_cliente
        model.nombres = cliente.nombres
        model.razon_social = cliente.razon_social
        model.fecha_nacimiento = cliente.fecha_nacimiento
        model.provincia = cliente.provincia
        model.canton = cliente.canton
        model.parroquia = cliente.parroquia
        model.direcciones = cliente.direcciones
        model.telefonos = cliente.telefonos
        model.correos = cliente.correos
        model.indice_direccion_principal = cliente.indice_direccion_principal
        model.indice_telefono_principal = cliente.indice_telefono_principal
        model.indice_correo_principal = cliente.indice_correo_principal
        model.direccion_fiscal = cliente.direccion_fiscal
        model.telefono_fiscal = cliente.telefono_fiscal
        model.correo_fiscal = cliente.correo_fiscal
        model.notas = cliente.notas
        model.activo = cliente.activo
        await self.session.commit()
        await self.session.refresh(model)
        return _cliente_desde_modelo(model)

    async def eliminar(self, cliente_id: int, empresa_id: int, punto_emision_id: int) -> bool:
        result = await self.session.execute(
            delete(ClienteModel).where(
                ClienteModel.id == cliente_id,
                *self._alcance(empresa_id, punto_emision_id),
            )
        )
        await self.session.commit()
        return result.rowcount > 0
