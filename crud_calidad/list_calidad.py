# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

from utils.supabase_client import supabase

def listar_registros_calidad():
    response = supabase.table("calidad").select("*").order("fecha_envio", desc=True).execute()
    return response.data if response.data else []

def obtener_calidad_por_formula(formula_id: str):
    response = supabase.table("calidad").select("*").eq("formula_id", formula_id).execute()
    return response.data if response.data else []
