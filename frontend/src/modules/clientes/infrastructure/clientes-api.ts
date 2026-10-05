import { httpClient } from "@/shared/infrastructure/http/http-client";
import type { Cliente, ClienteInput } from "@/modules/clientes/domain/entities";

interface ClienteApiDto {
  id: number;
  empresa_id: number;
  punto_emision_id: number;
  identificacion: string;
  tipo_cliente: Cliente["tipoCliente"];
  nombres: string;
  razon_social: string | null;
  fecha_nacimiento: string | null;
  provincia: string | null;
  canton: string | null;
  parroquia: string | null;
  direcciones: string[];
  telefonos: string[];
  correos: string[];
  indice_direccion_principal: number | null;
  indice_telefono_principal: number | null;
  indice_correo_principal: number | null;
  direccion_fiscal: string | null;
  telefono_fiscal: string | null;
  correo_fiscal: string | null;
  notas: string | null;
  activo: boolean;
  correo_principal: string | null;
}

interface ListaApi<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

interface DataApi<T> {
  data: T;
  message: string;
}

export interface ListaClientes {
  data: Cliente[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

function mapCliente(dto: ClienteApiDto): Cliente {
  return {
    id: dto.id,
    empresaId: dto.empresa_id,
    puntoEmisionId: dto.punto_emision_id,
    identificacion: dto.identificacion,
    tipoCliente: dto.tipo_cliente,
    nombres: dto.nombres,
    razonSocial: dto.razon_social,
    fechaNacimiento: dto.fecha_nacimiento,
    provincia: dto.provincia,
    canton: dto.canton,
    parroquia: dto.parroquia,
    direcciones: dto.direcciones ?? [],
    telefonos: dto.telefonos ?? [],
    correos: dto.correos ?? [],
    indiceDireccionPrincipal: dto.indice_direccion_principal,
    indiceTelefonoPrincipal: dto.indice_telefono_principal,
    indiceCorreoPrincipal: dto.indice_correo_principal,
    direccionFiscal: dto.direccion_fiscal,
    telefonoFiscal: dto.telefono_fiscal,
    correoFiscal: dto.correo_fiscal,
    notas: dto.notas,
    activo: dto.activo,
    correoPrincipal: dto.correo_principal,
  };
}

export async function listarClientes(
  token: string,
  params: { page: number; size: number; search?: string; activo?: boolean },
): Promise<ListaClientes> {
  const query = new URLSearchParams({
    page: String(params.page),
    size: String(params.size),
  });
  if (params.search) {
    query.set("search", params.search);
  }
  if (params.activo !== undefined) {
    query.set("activo", String(params.activo));
  }
  const dto = await httpClient<ListaApi<ClienteApiDto>>(`/clientes/?${query.toString()}`, { token });
  return {
    data: dto.data.map(mapCliente),
    total: dto.total,
    page: dto.page,
    size: dto.size,
    pages: dto.pages,
  };
}

export async function obtenerCliente(token: string, id: number): Promise<Cliente> {
  const dto = await httpClient<DataApi<ClienteApiDto>>(`/clientes/${id}`, { token });
  return mapCliente(dto.data);
}

export async function crearCliente(token: string, body: ClienteInput): Promise<Cliente> {
  const dto = await httpClient<DataApi<ClienteApiDto>>("/clientes/", { method: "POST", token, body });
  return mapCliente(dto.data);
}

export async function actualizarCliente(token: string, id: number, body: ClienteInput): Promise<Cliente> {
  const dto = await httpClient<DataApi<ClienteApiDto>>(`/clientes/${id}`, { method: "PUT", token, body });
  return mapCliente(dto.data);
}

export async function eliminarCliente(token: string, id: number): Promise<void> {
  await httpClient<void>(`/clientes/${id}`, { method: "DELETE", token });
}
