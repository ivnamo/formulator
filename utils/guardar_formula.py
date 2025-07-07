# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import uuid
import json
from datetime import datetime
from utils.supabase_client import supabase

def guardar_formula(df_editado, nombre_formula, precio_total):
    """
    Guarda una fórmula en la base de datos Supabase.

    Args:
        df_editado (pd.DataFrame): DataFrame con materias primas seleccionadas y cantidades.
        nombre_formula (str): Nombre de la fórmula definida por el usuario.
        precio_total (float): Precio total por kg de la fórmula.

    Returns:
        str: UUID de la fórmula guardada.
    """
    formula_id = str(uuid.uuid4())
    materias_dict = df_editado.to_dict(orient="records")

    supabase.table("formulas").insert({
        "id": formula_id,
        "nombre": nombre_formula,
        "materias_primas": json.dumps(materias_dict),
        "precio_total": round(precio_total, 2),
        "fecha_creacion": datetime.utcnow().isoformat()
    }).execute()

    return formula_id

