from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.modules.clientes.domain.entities import TipoCliente


class ClienteModel(Base):
    __tablename__ = "clientes"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id"), index=True, nullable=False)
    punto_emision_id: Mapped[int] = mapped_column(ForeignKey("puntos_emision.id"), index=True, nullable=False)
    identificacion: Mapped[str] = mapped_column(String(13), index=True, nullable=False)
    tipo_cliente: Mapped[TipoCliente] = mapped_column(
        Enum(TipoCliente, name="tipo_cliente", native_enum=True, create_type=False, values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=TipoCliente.PERSONA_NATURAL,
    )
    nombres: Mapped[str] = mapped_column(String(255), nullable=False)
    razon_social: Mapped[str | None] = mapped_column(String(255))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    provincia: Mapped[str | None] = mapped_column(String(100))
    canton: Mapped[str | None] = mapped_column(String(100))
    parroquia: Mapped[str | None] = mapped_column(String(100))
    direcciones: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    telefonos: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    correos: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    indice_direccion_principal: Mapped[int | None] = mapped_column(Integer)
    indice_telefono_principal: Mapped[int | None] = mapped_column(Integer)
    indice_correo_principal: Mapped[int | None] = mapped_column(Integer)
    direccion_fiscal: Mapped[str | None] = mapped_column(Text)
    telefono_fiscal: Mapped[str | None] = mapped_column(String(20))
    correo_fiscal: Mapped[str | None] = mapped_column(String(255))
    notas: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    actualizado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())
