"""Siembra identidad mínima de ContBill: empresa injoedev, admin y formas de pago."""

from __future__ import annotations

from pathlib import Path
import sys

import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.core.security import hashear_contrasena  # noqa: E402

ROLES = [
    ("superadmin", "Superadministrador", "Acceso total de plataforma"),
    ("admin", "Administrador", "Administra la empresa y sus puntos"),
    ("vendedor", "Vendedor", "Opera ventas en su punto"),
    ("contador", "Contador", "Opera facturación y reportes en su punto"),
]

PERMISOS = [
    ("auth:me", "Ver sesión", "Consultar el perfil autenticado"),
    ("auth:cambiar-punto", "Cambiar punto", "Cambiar el punto de emisión activo"),
    ("dashboard:ver", "Ver panel", "Acceder al dashboard"),
]

PLANTILLAS_FORMAS_PAGO = [
    ("EFE001", "Efectivo", "01", True, True),
    ("CHE001", "Cheque", "20", True, True),
    ("TRA001", "Transferencia", "20", True, True),
    ("TDE001", "Tarjeta de Débito", "16", True, False),
    ("TCR001", "Tarjeta de crédito", "19", True, True),
    ("NCR001", "Nota de Crédito", "20", True, True),
    ("DEP001", "Depósito", "20", True, True),
    ("TCP001", "Tarjeta De Credito Por Pagar", "20", False, True),
    ("DEC001", "Descuento En Compras", "20", False, True),
    ("GND001", "Gastos No Deducible", "20", False, True),
    ("DCL001", "Devolucion Clientes", "20", True, False),
]


def upsert_roles(cur) -> dict[str, int]:
    ids: dict[str, int] = {}
    for codigo, nombre, descripcion in ROLES:
        cur.execute(
            """
            INSERT INTO roles (codigo, nombre, descripcion, es_sistema)
            VALUES (%s, %s, %s, TRUE)
            ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre, descripcion = EXCLUDED.descripcion
            RETURNING id
            """,
            (codigo, nombre, descripcion),
        )
        ids[codigo] = cur.fetchone()["id"]
    return ids


def upsert_permisos(cur, roles_ids: dict[str, int]) -> None:
    permisos_ids: dict[str, int] = {}
    for codigo, nombre, descripcion in PERMISOS:
        cur.execute(
            """
            INSERT INTO permisos (codigo, nombre, descripcion, es_sistema)
            VALUES (%s, %s, %s, TRUE)
            ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre
            RETURNING id
            """,
            (codigo, nombre, descripcion),
        )
        permisos_ids[codigo] = cur.fetchone()["id"]

    for rol_id in roles_ids.values():
        for permiso_id in permisos_ids.values():
            cur.execute(
                """
                INSERT INTO roles_permisos (rol_id, permiso_id)
                VALUES (%s, %s)
                ON CONFLICT (rol_id, permiso_id) DO NOTHING
                """,
                (rol_id, permiso_id),
            )


def upsert_empresa(cur) -> int:
    cur.execute(
        """
        INSERT INTO empresas (
            nombre, slug, ruc, direccion, telefono, correo, sri_id, moneda,
            idioma, zona_horaria, entorno_sri, activa, verificada, plan_suscripcion
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, TRUE, %s)
        ON CONFLICT (slug) DO UPDATE SET
            nombre = EXCLUDED.nombre,
            ruc = EXCLUDED.ruc,
            direccion = EXCLUDED.direccion,
            telefono = EXCLUDED.telefono,
            correo = EXCLUDED.correo,
            sri_id = EXCLUDED.sri_id
        RETURNING id
        """,
        (
            "INJOE DEV",
            "injoedev",
            "1790012345001",
            "Av. Amazonas y Naciones Unidas, Quito",
            "022555555",
            "admin@techcorp.com",
            1,
            "USD",
            "es",
            "America/Guayaquil",
            "1",
            "basic",
        ),
    )
    return cur.fetchone()["id"]


def upsert_punto(cur, empresa_id: int) -> int:
    cur.execute(
        """
        SELECT id FROM puntos_emision
        WHERE empresa_id = %s AND codigo = %s AND punto_emision = %s
        """,
        (empresa_id, "001", "001"),
    )
    existente = cur.fetchone()
    if existente:
        return existente["id"]
    cur.execute(
        """
        INSERT INTO puntos_emision (
            empresa_id, punto_emision, codigo, direccion, info
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (empresa_id, "001", "001", "Matriz INJOE DEV", "Punto de emisión principal"),
    )
    return cur.fetchone()["id"]


def upsert_admin(cur, empresa_id: int, roles_ids: dict[str, int]) -> int:
    hash_pwd = hashear_contrasena("admin123")
    cur.execute(
        """
        INSERT INTO usuarios (
            empresa_id, correo, nombre_usuario, nombre_completo,
            contrasena_hash, activo, verificado
        )
        VALUES (%s, %s, %s, %s, %s, TRUE, TRUE)
        ON CONFLICT (correo, empresa_id) DO UPDATE SET
            nombre_usuario = EXCLUDED.nombre_usuario,
            nombre_completo = EXCLUDED.nombre_completo,
            contrasena_hash = EXCLUDED.contrasena_hash,
            activo = TRUE
        RETURNING id
        """,
        (empresa_id, "admin@techcorp.com", "admin", "Administrador ContBill", hash_pwd),
    )
    usuario_id = cur.fetchone()["id"]
    for codigo in ("admin", "superadmin", "contador"):
        cur.execute(
            """
            INSERT INTO usuarios_roles (usuario_id, rol_id)
            VALUES (%s, %s)
            ON CONFLICT (usuario_id, rol_id) DO NOTHING
            """,
            (usuario_id, roles_ids[codigo]),
        )
    return usuario_id


def asignar_punto(cur, usuario_id: int, punto_id: int) -> None:
    cur.execute(
        """
        INSERT INTO usuarios_puntos_emision (usuario_id, punto_emision_id)
        VALUES (%s, %s)
        ON CONFLICT (usuario_id, punto_emision_id) DO NOTHING
        """,
        (usuario_id, punto_id),
    )


def sembrar_formas_pago(cur, empresa_id: int, punto_id: int) -> None:
    cur.execute("SELECT id, codigo FROM formas_pago_sri")
    sri_ids = {fila["codigo"]: fila["id"] for fila in cur.fetchall()}
    for codigo, nombre, codigo_sri, venta, compra in PLANTILLAS_FORMAS_PAGO:
        cur.execute(
            """
            INSERT INTO formas_pago (
                empresa_id, punto_emision_id, codigo, nombre, forma_pago_sri_id,
                aplica_venta, aplica_compra, activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (empresa_id, punto_emision_id, codigo) DO NOTHING
            """,
            (empresa_id, punto_id, codigo, nombre, sri_ids.get(codigo_sri), venta, compra),
        )


def main() -> None:
    conn = psycopg2.connect(settings.DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            roles_ids = upsert_roles(cur)
            upsert_permisos(cur, roles_ids)
            empresa_id = upsert_empresa(cur)
            punto_id = upsert_punto(cur, empresa_id)
            usuario_id = upsert_admin(cur, empresa_id, roles_ids)
            asignar_punto(cur, usuario_id, punto_id)
            sembrar_formas_pago(cur, empresa_id, punto_id)
            conn.commit()
            print("Identidad sembrada en contbill_db")
            print("Empresa: injoedev | Usuario: admin@techcorp.com")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
