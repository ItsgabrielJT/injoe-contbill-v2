from __future__ import annotations

import re
from typing import Any

from app.core.config import settings
from app.modules.configuracion.domain.ambiente import codigo_ambiente

_AMBIENTE_XML = re.compile(r"<ambiente>\s*([12])\s*</ambiente>", re.IGNORECASE)


def ambiente_empresa(empresa: Any) -> str:
    return codigo_ambiente(getattr(empresa, "entorno_sri", None), settings.SRI_ENVIRONMENT)


def ambiente_comprobante(factura: Any, empresa: Any = None) -> str:
    clave = str(getattr(factura, "clave_acceso", None) or getattr(factura, "numero_autorizacion", None) or "")
    if len(clave) >= 24 and clave[23] in {"1", "2"}:
        return clave[23]
    xml = str(getattr(factura, "xml_content", None) or "")
    match = _AMBIENTE_XML.search(xml)
    if match:
        return match.group(1)
    return ambiente_empresa(empresa) if empresa is not None else "1"


def etiqueta_ambiente(codigo: str) -> str:
    return "PRODUCCIÓN" if str(codigo) == "2" else "PRUEBAS"
