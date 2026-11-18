import { env } from "@/config/env";
import { httpClient } from "@/shared/infrastructure/http/http-client";
import { asegurarAccessToken, renovarSesion } from "@/modules/acceso/infrastructure/renovar-sesion";
import { forzarCierreSesion } from "@/modules/acceso/infrastructure/sesion-storage";
import { ApiError } from "@/shared/infrastructure/http/http-error";
import type { CertificadoInfo, EmpresaConfig, PuntoConfig } from "@/modules/configuracion/domain/entities";

interface EmpresaDto {
  id: number;
  nombre: string;
  slug: string;
  ruc: string;
  direccion: string;
  telefono: string | null;
  correo: string | null;
  sri_id: number | null;
  entorno_sri: string;
  moneda: string;
  ruta_logo?: string | null;
}

interface PuntoDto {
  id: number;
  empresa_id: number;
  punto_emision: string;
  codigo: string;
  direccion: string;
  info: string | null;
  factura_seq: number;
  nota_credito_seq: number;
  nota_debito_seq: number;
  retencion_seq: number;
  liquidacion_compra_seq: number;
  guia_remision_seq: number;
}

function mapEmpresa(dto: EmpresaDto): EmpresaConfig {
  return {
    id: dto.id,
    nombre: dto.nombre,
    slug: dto.slug,
    ruc: dto.ruc,
    direccion: dto.direccion,
    telefono: dto.telefono,
    correo: dto.correo,
    sriId: dto.sri_id,
    entornoSri: dto.entorno_sri,
    moneda: dto.moneda,
    rutaLogo: dto.ruta_logo ?? null,
  };
}

function mapPunto(dto: PuntoDto): PuntoConfig {
  return {
    id: dto.id,
    empresaId: dto.empresa_id,
    puntoEmision: dto.punto_emision,
    codigo: dto.codigo,
    direccion: dto.direccion,
    info: dto.info,
    facturaSeq: dto.factura_seq,
    notaCreditoSeq: dto.nota_credito_seq,
    notaDebitoSeq: dto.nota_debito_seq,
    retencionSeq: dto.retencion_seq,
    liquidacionCompraSeq: dto.liquidacion_compra_seq,
    guiaRemisionSeq: dto.guia_remision_seq,
  };
}

export async function obtenerEmpresa(token: string): Promise<EmpresaConfig> {
  const resp = await httpClient<{ data: EmpresaDto }>(`/empresa/`, { token });
  return mapEmpresa(resp.data);
}

export async function actualizarEmpresa(token: string, body: Record<string, unknown>): Promise<EmpresaConfig> {
  const resp = await httpClient<{ data: EmpresaDto }>(`/empresa/`, { method: "PUT", token, body });
  return mapEmpresa(resp.data);
}

export async function guardarSriId(token: string, sriId: number): Promise<EmpresaConfig> {
  const resp = await httpClient<{ data: EmpresaDto }>(`/empresa/sri-id`, { method: "PATCH", token, body: { sri_id: sriId } });
  return mapEmpresa(resp.data);
}

async function logoFetch(token: string, init: RequestInit = {}): Promise<Response> {
  let accessToken = await asegurarAccessToken(token);
  const enviar = () => fetch(`${env.apiUrl}/empresa/logo`, {
    ...init,
    headers: { ...(init.headers ?? {}), ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}) },
  });
  let response = await enviar();
  if (response.status === 401) {
    try {
      accessToken = (await renovarSesion()).accessToken;
      response = await enviar();
    } catch {
      forzarCierreSesion();
      throw new ApiError(401, "Sesión expirada");
    }
  }
  return response;
}

async function logoError(response: Response): Promise<never> {
  const data = await response.json().catch(() => ({}));
  const detail = typeof data.detail === "string" ? data.detail : "No se pudo procesar el logo";
  throw new ApiError(response.status, detail);
}

async function blobDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error("No se pudo leer el logo"));
    reader.readAsDataURL(blob);
  });
}

export async function obtenerLogoEmpresa(token: string): Promise<string | null> {
  const response = await logoFetch(token);
  if (response.status === 404) return null;
  if (!response.ok) return logoError(response);
  return blobDataUrl(await response.blob());
}

export async function subirLogoEmpresa(token: string, archivo: File): Promise<EmpresaConfig> {
  const form = new FormData();
  form.append("archivo", archivo);
  const response = await logoFetch(token, { method: "POST", body: form });
  if (!response.ok) return logoError(response);
  const data = await response.json() as { data: EmpresaDto };
  return mapEmpresa(data.data);
}

export async function eliminarLogoEmpresa(token: string): Promise<EmpresaConfig> {
  const response = await logoFetch(token, { method: "DELETE" });
  if (!response.ok) return logoError(response);
  const data = await response.json() as { data: EmpresaDto };
  return mapEmpresa(data.data);
}

export async function listarPuntos(token: string): Promise<PuntoConfig[]> {
  const resp = await httpClient<{ data: PuntoDto[] }>(`/puntos-emision/`, { token });
  return resp.data.map(mapPunto);
}

export async function guardarPunto(token: string, body: Record<string, unknown>, id?: number): Promise<PuntoConfig> {
  const resp = await httpClient<{ data: PuntoDto }>(id ? `/puntos-emision/${id}` : `/puntos-emision/`, {
    method: id ? "PUT" : "POST",
    token,
    body,
  });
  return mapPunto(resp.data);
}

export async function eliminarPunto(token: string, id: number): Promise<void> {
  await httpClient(`/puntos-emision/${id}`, { method: "DELETE", token });
}

let apiKeyCache: string | null = null;

async function sriApiKey(): Promise<string> {
  if (apiKeyCache) return apiKeyCache;
  const resp = await fetch(`${env.sriSignUrl}/api-key/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ secret_key: env.sriSignSecret, expiration: "never" }),
  });
  if (!resp.ok) throw new Error("No se pudo generar la API key de SriSignXml");
  const data = await resp.json();
  apiKeyCache = data.api_key;
  return apiKeyCache as string;
}

async function sriFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const send = async () =>
    fetch(`${env.sriSignUrl}${path}`, { ...init, headers: { ...init.headers, "X-API-Key": await sriApiKey() } });
  const resp = await send();
  if (resp.status !== 401) return resp;
  // SriSignXml guarda las API keys en memoria: tras reiniciarse, la key cacheada deja de existir.
  apiKeyCache = null;
  return send();
}

export async function consultarCertificado(sriId: number): Promise<CertificadoInfo | null> {
  try {
    const resp = await sriFetch(`/v1/empresas/${sriId}`);
    if (!resp.ok) return null;
    const data = await resp.json();
    return {
      id: data.id,
      ruc: data.ruc,
      razonSocial: data.razon_social,
      fingerprint: data.fingerprint,
      fechaExpiracion: data.fecha_expiracion,
      creadoEn: data.created_at ?? data.creado_en ?? null,
      isActive: data.is_active,
    };
  } catch {
    return null;
  }
}

export async function subirCertificado(file: File, password: string, ruc: string, razonSocial: string): Promise<number> {
  const form = new FormData();
  form.append("certificate", file);
  form.append("password", password);
  form.append("ruc", ruc);
  form.append("razon_social", razonSocial);
  const resp = await sriFetch("/empresas/certificado", { method: "POST", body: form });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    throw new Error(data.detail || data.error || "No se pudo subir el certificado");
  }
  return Number(data.id);
}
