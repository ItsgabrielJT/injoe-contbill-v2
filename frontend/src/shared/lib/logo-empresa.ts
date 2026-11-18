import { obtenerLogoEmpresa } from "@/modules/configuracion/infrastructure/configuracion-api";
import { LOGO_SISTEMA } from "@/shared/lib/brand";

export async function cargarLogoEmpresa(token: string): Promise<string> {
  try {
    return (await obtenerLogoEmpresa(token)) ?? LOGO_SISTEMA;
  } catch {
    return LOGO_SISTEMA;
  }
}
