from __future__ import annotations

from typing import Any

_PRODUCCION = {"2", "produccion", "producción", "prod", "production"}
_PRUEBAS = {"1", "pruebas", "prueba", "test"}


def codigo_ambiente(valor: Any, fallback: Any = "1") -> str:
    texto = str(valor or "").strip().lower()
    if texto in _PRODUCCION:
        return "2"
    if texto in _PRUEBAS:
        return "1"
    extra = str(fallback or "").strip().lower()
    return "2" if extra in _PRODUCCION else "1"
