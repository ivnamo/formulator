from utils.supabase_client import supabase

def actualizar_estado_calidad(calidad_id: str, nuevo_estado: str, nuevas_observaciones: str = ""):
    assert nuevo_estado in ["Pendiente", "OK", "NOK", "Cancelado"], "Estado no válido"
    data = {
        "estado": nuevo_estado,
        "observaciones": nuevas_observaciones
    }
    supabase.table("calidad").update(data).eq("id", calidad_id).execute()
