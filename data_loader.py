import pandas as pd
from supabase_client import supabase

def cargar_datos(archivo):
    if archivo is not None:
        df = pd.read_excel(archivo)
    else:
        response = supabase.table("materias_primas").select("*").execute()
        df = pd.DataFrame(response.data)

    df["%"] = 0.0
    return df
