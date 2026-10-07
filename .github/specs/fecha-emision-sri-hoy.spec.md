---
id: SPEC-013
status: IMPLEMENTED
feature: fecha-emision-sri-hoy
created: 2026-10-06
updated: 2026-10-06
author: spec-generator
version: "1.0"
related-specs: ["SPEC-009"]
---

# Spec: Fecha de emisión al día de envío al SRI

> **Estado:** `IMPLEMENTED`
> **Ciclo de vida:** DRAFT → APPROVED → IN_PROGRESS → IMPLEMENTED → DEPRECATED

---

## 1. REQUERIMIENTOS

### Descripción
Al emitir una factura al SRI, `fecha_emision` y `creado_en` se alinean al día actual en Ecuador (`America/Guayaquil`). El SRI no acepta comprobantes extemporáneos: la fecha del XML debe ser el día del envío, no la del borrador. Portar el comportamiento ya aplicado en injoe-mechanics.

### Requerimiento de Negocio
Si se creó una factura el 03/10/2026 y se emite el 06/10/2026, la factura debe salir con fecha 06/10/2026. Creación y emisión quedan iguales al momento de emitir, por nueva norma del SRI.

### Historias de Usuario

#### HU-01: Emitir con fecha de hoy

```
Como:        Usuario del taller
Quiero:      Que al enviar al SRI la factura use la fecha de hoy
Para:        Evitar rechazos por fechas extemporáneas

Prioridad:   Alta
Estimación:  S
Dependencias: SPEC-009
Capa:        Ambas
```

#### Criterios de Aceptación — HU-01

**Happy Path**
```gherkin
CRITERIO-1.1: fecha al emitir
  Dado que:  el borrador tiene fecha_emision anterior (p. ej. 03/10/2026)
  Cuando:    envío la factura al SRI el 06/10/2026
  Entonces:  fecha_emision y creado_en quedan en el día actual America/Guayaquil y el XML usa esa fecha
```

**Error Path**
```gherkin
CRITERIO-1.2: ya autorizada
  Dado que:  la factura está AUTORIZADA
  Cuando:    intento enviarla
  Entonces:  no se cambia la fecha y se rechaza el reenvío
```

**Edge Case**
```gherkin
CRITERIO-1.3: secuencial registrado
  Dado que:  el SRI ya registró el secuencial
  Cuando:    se recupera la autorización original
  Entonces:  no se altera la fecha del comprobante ya emitido
```

### Reglas de Negocio
1. Al firmar un `BORRADOR` o `RECHAZADA` se fuerza `fecha_emision = hoy (America/Guayaquil)` y `creado_en = ahora`.
2. No se cambia la fecha si se recupera un secuencial ya autorizado o si solo se consulta un `PENDIENTE`.
3. El borrador puede conservar la fecha original hasta el envío.
4. Tras el envío, el listado y el detalle muestran la fecha que devolvió la API.

---

## 2. DISEÑO

### Modelos de Datos

#### Entidades afectadas
| Entidad | Almacén | Cambios | Descripción |
|---------|---------|---------|-------------|
| `Factura` | tabla `facturas` | sin migración | Se reutilizan `fecha_emision` y `creado_en` |

#### Campos del modelo
Sin cambios de esquema.

| Campo | Tipo | Obligatorio | Validación | Descripción |
|-------|------|-------------|------------|-------------|
| `fecha_emision` | date | sí | se sobreescribe al emitir | Fecha del comprobante SRI |
| `creado_en` | timestamptz | sí | se alinea al emitir | Queda en el mismo día que la emisión |

#### Índices / Constraints
- Ninguno nuevo.

### API Endpoints
Sin cambios de contrato. `POST /api/v1/facturas/{id}/enviar-sri` persiste y devuelve la factura con `fecha_emision` y `creado_en` actualizados.

### Diseño Frontend

#### Componentes modificados
| Componente | Archivo | Cambio |
|------------|---------|--------|
| `FacturaFormDrawer` | `frontend/src/modules/facturacion/presentation/forms/factura-form-drawer.tsx` | Aviso bajo "Fecha de emisión": al enviar al SRI se usará la fecha de hoy |

#### Páginas nuevas
Ninguna.

#### Hooks y State
Ninguno nuevo. Tras `enviarSri` el listado ya refresca con la factura devuelta.

### Arquitectura y Dependencias
- Paquetes nuevos: ninguno (`zoneinfo` es stdlib).
- Helper de dominio: `hoy_sri()`, `ahora_sri()`, `alinear_fecha_emision_sri()`.
- Llamar `alinear_fecha_emision_sri` solo antes de `firmar_factura` en `BORRADOR` o `RECHAZADA`.

### Notas de Implementación
> Portar el mismo patrón de injoe-mechanics.
> El repositorio debe persistir `creado_en` si viene en el dominio (`if factura.creado_en: modelo.creado_en = factura.creado_en`).
> `construir_payload` ya usa `factura.fecha_emision`; no hace falta cambiar el XML builder si se alinea antes de firmar.
> No alterar fechas en recuperación de secuencial registrado ni en consulta de pendiente.

---

## 3. LISTA DE TAREAS

> Checklist accionable para todos los agentes. Marcar cada ítem (`[x]`) al completarlo.

### Backend

#### Implementación
- [x] Helper `hoy_sri` / `ahora_sri` / `alinear_fecha_emision_sri` en dominio (`America/Guayaquil`)
- [x] Alinear fecha al emitir `BORRADOR` o `RECHAZADA` en `EnviarSriUseCase` y reintento de rechazada
- [x] Persistir `creado_en` al guardar si viene en el dominio
- [x] No alterar fecha en recuperación de secuencial

#### Tests Backend
- [x] Helper verificado: fecha 2026-10-03 se alinea a hoy Ecuador

### Frontend

#### Implementación
- [x] Aviso en el formulario bajo fecha de emisión
- [x] El listado/detalle usan la fecha que devuelve la API tras enviar

#### Tests Frontend
- [x] No aplicar tests automatizados (restricción del agente frontend)

### QA
- [x] Helper alinea emisión y creación al día actual America/Guayaquil
- [x] Autorizada: el use case sigue rechazando el reenvío sin cambiar fecha
- [x] Actualizar estado spec: `status: IMPLEMENTED`
