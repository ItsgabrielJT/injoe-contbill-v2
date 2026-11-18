from __future__ import annotations

import io
import os
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.core.config import settings

MAX_LOGO_BYTES = 5 * 1024 * 1024
ALLOWED_LOGO_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def _empresa_dir(empresa_id: int) -> Path:
    return settings.logo_storage_path / str(empresa_id)


def ruta_logo_empresa(empresa_id: int) -> Path:
    return _empresa_dir(empresa_id) / "logo.png"


def validar_y_normalizar_logo(contenido: bytes, nombre: str | None, content_type: str | None) -> bytes:
    if not contenido:
        raise ValueError("El archivo del logo está vacío")
    if len(contenido) > MAX_LOGO_BYTES:
        raise ValueError("El logo no puede superar 5 MB")
    extension = Path(nombre or "").suffix.lower()
    if extension not in ALLOWED_LOGO_EXTENSIONS:
        raise ValueError("El logo debe ser PNG, JPEG o WebP")
    if content_type and content_type.lower() not in ALLOWED_LOGO_TYPES:
        raise ValueError("El logo debe ser PNG, JPEG o WebP")

    try:
        with Image.open(io.BytesIO(contenido)) as imagen:
            imagen.verify()
        with Image.open(io.BytesIO(contenido)) as imagen:
            if imagen.width < 1 or imagen.height < 1:
                raise ValueError("La imagen del logo no tiene dimensiones válidas")
            if imagen.mode in {"RGBA", "LA"} or "transparency" in imagen.info:
                normalizada = imagen.convert("RGBA")
            else:
                normalizada = imagen.convert("RGB")
            salida = io.BytesIO()
            normalizada.save(salida, format="PNG", optimize=True)
            return salida.getvalue()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("El archivo no contiene una imagen válida") from exc


def guardar_logo_local(empresa_id: int, contenido: bytes) -> Path:
    destino = ruta_logo_empresa(empresa_id)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".tmp")
    temporal.write_bytes(contenido)
    os.replace(temporal, destino)
    return destino


def eliminar_logo_local(empresa_id: int) -> None:
    ruta = ruta_logo_empresa(empresa_id)
    if ruta.is_file():
        ruta.unlink()
