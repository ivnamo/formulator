from utils.supabase_client import supabase
from datetime import date
import uuid

def crear_registro_calidad(formula_id: str, codigo: str, fecha_envio: date, observaciones: str = "") -> str:
    calidad_id = str(uuid.uuid4())
    data = {
        "id": calidad_id,
        "formula_id": formula_id,
        "codigo": codigo,
        "fecha_envio": fecha_envio.isoformat(),
        "estado": "Pendiente",
        "observaciones": observaciones
    }
    supabase.table("calidad").insert(data).execute()
    return calidad_id
