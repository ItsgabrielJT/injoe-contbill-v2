---
id: SPEC-012
status: IMPLEMENTED
feature: factura-numero-autorizacion
created: 2026-10-06
updated: 2026-10-06
author: spec-generator
version: "1.0"
related-specs: ["SPEC-009", "SPEC-010"]
---

# Spec: Número de autorización SRI en detalle de factura

> **Estado:** `IMPLEMENTED`
> **Ciclo de vida:** DRAFT → APPROVED → IN_PROGRESS → IMPLEMENTED → DEPRECATED

---

## 1. REQUERIMIENTOS

### Descripción
En el modal de detalle de factura, mostrar el número de autorización SRI cuando la factura ya fue emitida y autorizada, con un control para copiarlo al portapapeles. El backend ya persiste y expone `numero_autorizacion` y `clave_acceso`; este cambio es de presentación.

### Requerimiento de Negocio
En el modal de detalles de facturación debería poder verse el número de autorización una vez emitida al SRI, y que sea fácil de copiar.

### Historias de Usuario

#### HU-01: Ver y copiar número de autorización SRI

```
Como:        Usuario del taller
Quiero:      Ver el número de autorización SRI en el detalle de una factura emitida
Para:        Consultarlo o copiarlo sin abrir el XML ni el PDF

Prioridad:   Alta
Estimación:  XS
Dependencias: Ninguna
Capa:        Frontend
```

#### Criterios de Aceptación — HU-01

**Happy Path**
```gherkin
CRITERIO-1.1: mostrar numero autorizado
  Dado que:  la factura está AUTORIZADA y tiene numero_autorizacion o clave_acceso
  Cuando:    abro el modal de detalle
  Entonces:  veo el bloque "N.° autorización SRI" con el número en monoespaciado y un botón Copiar
```

```gherkin
CRITERIO-1.2: copiar al portapapeles
  Dado que:  el número de autorización es visible
  Cuando:    pulso Copiar
  Entonces:  el número queda en el portapapeles y el botón confirma "Copiado" unos 2 segundos
```

**Error Path**
```gherkin
CRITERIO-1.3: clipboard no disponible
  Dado que:  navigator.clipboard falla o no existe
  Cuando:    pulso Copiar
  Entonces:  el número permanece seleccionable a mano y no se rompe el modal
```

**Edge Case**
```gherkin
CRITERIO-1.4: sin autorizacion
  Dado que:  la factura está en BORRADOR, RECHAZADA o sin número de autorización
  Cuando:    abro el modal de detalle
  Entonces:  no se muestra el bloque de número de autorización
```

### Reglas de Negocio
1. El número visible es `numeroAutorizacion`; si está vacío y la factura está `AUTORIZADA`, se usa `claveAcceso` (en SRI ambos coinciden al autorizar).
2. El bloque solo aparece si hay un valor no vacío.
3. La fecha de autorización se etiqueta "Fecha de autorización" para no confundirla con el número.
4. Copiar no altera el estado de la factura ni llama al backend.

---

## 2. DISEÑO

### Modelos de Datos

#### Entidades afectadas
| Entidad | Almacén | Cambios | Descripción |
|---------|---------|---------|-------------|
| `Factura` | tabla `facturas` | sin cambios | Ya tiene `numero_autorizacion` y `clave_acceso` |

#### Campos del modelo
Sin cambios de esquema. Campos ya existentes:

| Campo | Tipo | Obligatorio | Validación | Descripción |
|-------|------|-------------|------------|-------------|
| `numero_autorizacion` | string(60) nullable | no | — | Número de autorización SRI (igual a clave de acceso al autorizar) |
| `clave_acceso` | string nullable | no | — | Clave de acceso de 49 dígitos |
| `fecha_autorizacion` | datetime tz | no | — | Fecha/hora de autorización |
| `estado` | enum | sí | — | Incluye `AUTORIZADA` |

#### Índices / Constraints
- Ninguno nuevo.

### API Endpoints

Sin endpoints nuevos. `FacturaResponse` ya incluye `numero_autorizacion` y `clave_acceso` en listado y detalle.

### Diseño Frontend

#### Componentes nuevos
Ninguno. Se reutiliza `FacturaDetalleDialog`.

#### Componentes modificados
| Componente | Archivo | Cambio |
|------------|---------|--------|
| `FacturaDetalleDialog` | `frontend/src/modules/facturacion/presentation/modals/factura-detalle-dialog.tsx` | Mostrar número + botón copiar; renombrar etiqueta de fecha |

#### Páginas nuevas
Ninguna.

#### Hooks y State
Estado local en el diálogo: `copiado: boolean` para feedback del botón. Sin store ni hook de módulo.

#### Services (llamadas API)
Ninguno nuevo. `facturacion-api.ts` ya mapea `numero_autorizacion` → `numeroAutorizacion`.

### Arquitectura y Dependencias
- Paquetes nuevos: ninguno (`lucide-react` ya está; usar `Copy` y `Check`).
- Clipboard: `navigator.clipboard.writeText`.
- Sin impacto en rutas.

### Notas de Implementación
> El backend no requiere cambios: `FacturaResponse.numero_autorizacion` y el mapper frontend ya existen.
> Ubicar el número en la sección "Detalle de pago", debajo de ambiente SRI, con el valor en `font-mono` y `break-all` para los 49 dígitos.
> El botón Copiar debe tener `title`/`aria-label` "Copiar número de autorización".
> Si `clipboard.writeText` rechaza, capturar el error y dejar el texto seleccionable (`select-all` o selección nativa).
> No hay sistema de toast en el frontend; el feedback es el propio botón ("Copiado" + icono Check).

---

## 3. LISTA DE TAREAS

> Checklist accionable para todos los agentes. Marcar cada ítem (`[x]`) al completarlo.
> El Orchestrator monitorea este checklist para determinar el progreso.

### Backend

#### Implementación
- [x] Campo `numero_autorizacion` ya existe en modelo, entidad y `FacturaResponse` — sin trabajo adicional

#### Tests Backend
- [x] No aplica — sin cambios de API ni persistencia

### Frontend

#### Implementación
- [x] En `FacturaDetalleDialog`, derivar el número con `numeroAutorizacionSri`
- [x] Mostrar bloque "N.° autorización SRI" solo si hay valor, en monoespaciado y seleccionable
- [x] Botón Copiar con clipboard + fallback; feedback "Copiado" ~2 s; no romper si clipboard falla
- [x] Renombrar la etiqueta de fecha de "Autorización" a "Fecha de autorización"

#### Tests Frontend
- [x] No aplicar tests automatizados (restricción del agente frontend)

### QA
- [x] Verificar CRITERIO-1.1 a 1.4 en el modal con factura autorizada y con borrador
- [x] Copiar el número: botón Copiar visible; el número también se copia al hacer clic sobre él
- [x] Actualizar estado spec: `status: IMPLEMENTED`
