---
id: SPEC-011
status: IMPLEMENTED
feature: contbill-purga-mecanica
created: 2026-10-04
updated: 2026-10-04
author: spec-generator
version: "1.0"
related-specs: ["SPEC-001", "SPEC-002", "SPEC-003", "SPEC-005", "SPEC-007", "SPEC-009"]
---

# Spec: Purga mecánica y rebrand a ContBill

> **Estado:** `APPROVED`
> **Ciclo de vida:** DRAFT → APPROVED → IN_PROGRESS → IMPLEMENTED → DEPRECATED

---

## 1. REQUERIMIENTOS

### Descripción
Convertir el sistema de taller (INJOE MECHANICS) en un producto netamente contable-facturación (INJOE CONTBILL). Se eliminan vehículos, órdenes de trabajo y estado de vehículo; se renombra branding y base de datos; el directorio se trata como repositorio git nuevo.

### Requerimiento de Negocio
Antes de ejecutar el proyecto o Alembic: quitar seeds de taller, eliminar vehículos / OT / estado de vehículo / módulo de vehículos, cambiar el nombre de Mechanics a ContBill, colores azules, BD `contbill_db`, y borrar el historial git para nacer como proyecto nuevo. Conservar identidad (empresa injoedev + admin) y catálogo SRI de formas de pago.

### Historias de Usuario

#### HU-01: Sistema sin módulos de taller

```
Como:        Operador contable
Quiero:      Un sistema sin vehículos, órdenes de trabajo ni estado de vehículo
Para:        Facturar y gestionar clientes sin lógica de mecánica

Prioridad:   Alta
Estimación:  XL
Dependencias: Ninguna
Capa:        Ambas
```

#### Criterios de Aceptación — HU-01

**Happy Path**
```gherkin
CRITERIO-1.1: apis de taller inexistentes
  Dado que:  el backend ContBill está en marcha
  Cuando:    se llama /api/v1/vehiculos, /ordenes-trabajo o /estado-vehiculo
  Entonces:  responde 404 y no existen esas tablas en contbill_db
```

**Error Path**
```gherkin
CRITERIO-1.2: factura ya no acepta OT
  Dado que:  una factura en borrador
  Cuando:    se intenta POST /facturas/desde-orden/{id}
  Entonces:  responde 404 y facturas no tiene orden_trabajo_id
```

#### HU-02: Identidad mínima para operar

```
Como:        Administrador
Quiero:      Entrar con empresa injoedev y admin@techcorp.com / admin123
Para:        Usar el sistema sin copiar datos desde autocare_db ni seeds de taller

Prioridad:   Alta
Estimación:  M
Dependencias: HU-01
Capa:        Backend
```

#### Criterios de Aceptación — HU-02

**Happy Path**
```gherkin
CRITERIO-2.1: login contable
  Dado que:  se ejecutó Alembic sobre contbill_db y sembrar_identidad.py
  Cuando:    inicio sesión con empresa injoedev y admin@techcorp.com / admin123
  Entonces:  obtengo token y no existe rol mecanico ni filas de vehiculos/OT
```

#### HU-03: Branding ContBill azul

```
Como:        Usuario
Quiero:      Ver INJOE CONTBILL con tema azul
Para:        Distinguir el producto de Mechanics naranja

Prioridad:   Alta
Estimación:  S
Dependencias: Ninguna
Capa:        Ambas
```

#### Criterios de Aceptación — HU-03

**Happy Path**
```gherkin
CRITERIO-3.1: nombre y color
  Dado que:  abro login o el panel
  Cuando:    cargo la UI
  Entonces:  el nombre es INJOE CONTBILL y el primario es #279FF5 / #3B82F6, no #FF7F50
```

#### HU-04: Repositorio git nuevo

```
Como:        Desarrollador
Quiero:      Un repo sin historial de Mechanics
Para:        Tratar ContBill como proyecto nuevo

Prioridad:   Alta
Estimación:  XS
Dependencias: HU-01, HU-03
Capa:        Backend
```

#### Criterios de Aceptación — HU-04

**Happy Path**
```gherkin
CRITERIO-4.1: init limpio
  Dado que:  el código ya está sin módulos de taller
  Cuando:    se elimina .git y se hace git init
  Entonces:  hay un commit Initial commit: INJOE CONTBILL, sin origin y sin push
```

### Reglas de Negocio
1. No ejecutar Alembic ni el seed hasta que el SQL y el código estén limpios.
2. Base de datos nueva `contbill_db`. No migrar `mecanicos_db`.
3. Seed permitido: empresa `injoedev`, usuario `admin@techcorp.com` / `admin123`, roles `superadmin|admin|vendedor|contador`, catálogo `formas_pago_sri` y plantillas de `formas_pago` del punto.
4. Prohibido copiar desde `autocare_db`. No existe `AUTOCARE_DATABASE_URL`.
5. Cliente mantiene `identificacion` NOT NULL (SRI). No se hereda identificación opcional de alta rápida OT.
6. Factura autorizada siempre registra salida de inventario (ya no hay excepción por OT).
7. Se conservan clientes, servicios, inventario, proveedores, facturación, configuración, acceso e identidad.
8. Git: borrar historial local, `git init`, un commit. No añadir origin, no push, no force-push.
9. Specs de taller se eliminan del árbol: `clientes-vehiculos`, `transferencia-vehiculos`, `ordenes-trabajo`, `estado-vehiculo`.
10. Frontend a tocar: solo `injoe-contbill-v2/frontend`. No se modifica `injoe-contbill-front`.

---

## 2. DISEÑO

### Modelos de Datos

#### Entidades afectadas
| Entidad | Almacén | Cambios | Descripción |
|---------|---------|---------|-------------|
| `Vehiculo` | `vehiculos` | eliminada | Taller |
| `OrdenTrabajo` | `ordenes_trabajo` | eliminada | Taller |
| `OrdenTrabajoItem` | `ordenes_trabajo_items` | eliminada | Taller |
| `Cliente` | `clientes` | recortada | Sin vehículos; identificación obligatoria |
| `Factura` | `facturas` | modificada | Sin `orden_trabajo_id` |
| `Empresa` | `empresas` | seed | `injoedev` + `sri_id` vía seed, no migración |
| `Rol` | `roles` | seed | `contador` reemplaza `mecanico` |

#### Campos del modelo
Factura pierde `orden_trabajo_id`. Cliente no cambia campos de negocio salvo dejar de exponer `total_vehiculos`.

#### Índices / Constraints
- Se elimina `uq_facturas_orden_activa`.
- Se eliminan unique de placa y FKs de OT.
- `uq_clientes_identificacion_punto` permanece UNIQUE NOT NULL.

### API Endpoints

Endpoints **eliminados**:
- `/api/v1/vehiculos` y anidados de cliente
- `POST /api/v1/clientes/alta-rapida`
- `/api/v1/ordenes-trabajo`
- `/api/v1/estado-vehiculo`
- `POST /api/v1/facturas/desde-orden/{orden_id}`

Endpoints conservados: auth, usuarios, empresa, puntos, clientes (CRUD), servicios, inventario, proveedores, facturas (CRUD/SRI), formas de pago.

### Diseño Frontend

#### Componentes eliminados
| Componente | Archivo |
|------------|---------|
| Órdenes | `modules/ordenes-trabajo/**` |
| Estado vehículo | `modules/estado-vehiculo/**` |
| Vehículos dialog | `modules/clientes/presentation/modals/vehiculos-dialog.tsx` |
| Rutas OT/estado | `app/(protegido)/ordenes-trabajo`, `estado-vehiculo` |

#### Componentes modificados
| Componente | Cambio |
|------------|--------|
| `app-shell.tsx` | Quitar Órdenes y Estado de vehículo |
| `brand.ts` | `INJOE CONTBILL` + facturación/contabilidad |
| Login / selector / MuiDataTable | Primario `#279FF5` / `#3B82F6` |
| `clientes-api.ts` | Sin vehículos ni alta rápida |
| `facturacion-api.ts` | Sin `desde-orden` |

### Arquitectura y Dependencias
- Paquetes nuevos: ninguno
- Quitar dependencia de `autocare_db`
- Alembic: reescribir cadena 0002, borrar 0006/0007, `0008` revisa `0005`, 0009 sin FK OT
- Git: repo nuevo local

### Notas de Implementación
> No correr `migrar.py` ni `sembrar_identidad.py` hasta terminar SQL y código.
> Seed de identidad es standalone (no copia Autocare).
> `0008` conserva INSERT de `formas_pago_sri`; plantillas de `formas_pago` se siembran al crear el punto.
> Reset git solo después del código limpio. No commitear `.env`.

---

## 3. LISTA DE TAREAS

### Backend

#### Implementación
- [ ] Reescribir `0002` solo clientes
- [ ] Eliminar SQL/Alembic 0006 y 0007; reencadenar 0008 → 0005
- [ ] Quitar `orden_trabajo_id` de 0009
- [ ] Borrar módulos `ordenes_trabajo` y `estado_vehiculo`
- [ ] Recortar clientes (sin vehículos)
- [ ] Recortar facturación (sin OT); salida inventario siempre al autorizar
- [ ] Rebrand config + PDF; `DATABASE_URL` → `contbill_db`; quitar `AUTOCARE_DATABASE_URL`
- [ ] Reescribir `sembrar_identidad.py` standalone (injoedev + admin + rol contador)

#### Tests Backend
- [ ] Arranque + login injoedev (verificación manual/API)

### Frontend

#### Implementación
- [ ] Borrar módulos y rutas de taller
- [ ] Recortar clientes y facturación
- [ ] Menú, brand, colores azules, `storageKey` contbill.*

#### Tests Frontend
- [ ] Login y navegación sin ítems de taller (verificación en navegador)

### QA
- [ ] Specs de taller eliminadas del árbol
- [ ] `git init` + commit inicial sin origin
- [ ] `contbill_db` migrada y sembrada
- [ ] Actualizar estado spec: `status: IMPLEMENTED`
