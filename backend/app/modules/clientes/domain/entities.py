from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class TipoCliente(str, Enum):
    PERSONA_NATURAL = "PERSONA_NATURAL"
    PERSONA_JURIDICA = "PERSONA_JURIDICA"


def identificacion_valida(valor: str) -> bool:
    limpia = valor.strip()
    return limpia.isdigit() and len(limpia) in (10, 13)


def correo_valido(valor: str) -> bool:
    texto = valor.strip()
    return "@" in texto and "." in texto.split("@")[-1] and len(texto) >= 5


@dataclass
class Cliente:
    id: int | None
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
    direcciones: list[str] = field(default_factory=list)
    telefonos: list[str] = field(default_factory=list)
    correos: list[str] = field(default_factory=list)
    indice_direccion_principal: int | None = None
    indice_telefono_principal: int | None = None
    indice_correo_principal: int | None = None
    direccion_fiscal: str | None = None
    telefono_fiscal: str | None = None
    correo_fiscal: str | None = None
    notas: str | None = None
    activo: bool = True
    creado_en: datetime | None = None
    actualizado_en: datetime | None = None

    @property
    def correo_principal(self) -> str | None:
        if not self.correos:
            return None
        idx = self.indice_correo_principal if self.indice_correo_principal is not None else 0
        if 0 <= idx < len(self.correos):
            return self.correos[idx]
        return self.correos[0]
