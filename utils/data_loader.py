# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------


import pandas as pd
from utils.supabase_client import supabase

def cargar_datos():
    """Carga todas las materias primas ordenadas alfabéticamente por nombre."""
    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)
    df = df.sort_values("Materia Prima", ascending=True, na_position="last")
    df["%"] = 0.0
    return df

