export type TipoCliente = "PERSONA_NATURAL" | "PERSONA_JURIDICA";

export interface Cliente {
  id: number;
  empresaId: number;
  puntoEmisionId: number;
  identificacion: string;
  tipoCliente: TipoCliente;
  nombres: string;
  razonSocial: string | null;
  fechaNacimiento: string | null;
  provincia: string | null;
  canton: string | null;
  parroquia: string | null;
  direcciones: string[];
  telefonos: string[];
  correos: string[];
  indiceDireccionPrincipal: number | null;
  indiceTelefonoPrincipal: number | null;
  indiceCorreoPrincipal: number | null;
  direccionFiscal: string | null;
  telefonoFiscal: string | null;
  correoFiscal: string | null;
  notas: string | null;
  activo: boolean;
  correoPrincipal: string | null;
}

export interface ClienteInput {
  identificacion: string;
  nombres: string;
  correos: string[];
  tipo_cliente: TipoCliente;
  razon_social?: string | null;
  fecha_nacimiento?: string | null;
  provincia?: string | null;
  canton?: string | null;
  parroquia?: string | null;
  direcciones: string[];
  telefonos: string[];
  indice_direccion_principal?: number | null;
  indice_telefono_principal?: number | null;
  indice_correo_principal?: number | null;
  direccion_fiscal?: string | null;
  telefono_fiscal?: string | null;
  correo_fiscal?: string | null;
  notas?: string | null;
  activo: boolean;
}
