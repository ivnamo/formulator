# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import json
import pandas as pd
import streamlit as st
from utils.supabase_client import supabase
from utils.editor import mostrar_editor_formula
from utils.families import obtener_familias_parametros
from utils.formula_resultados import calcular_resultado_formula


def actualizar_formula(formula_id: str):
    """Carga una fórmula existente y permite editarla."""
    if not formula_id:
        st.info("Selecciona una fórmula para actualizar.")
        return

    try:
        resp = (
            supabase.table("formulas")
            .select("*")
            .eq("id", formula_id)
            .single()
            .execute()
        )
        data = resp.data
    except Exception as e:
        st.error(f"❌ Error al cargar la fórmula: {e}")
        return

    if not data:
        st.error("No se encontró la fórmula solicitada.")
        return

    nombre = st.text_input("Nombre de la fórmula", value=data.get("nombre", ""))

    try:
        response_mp = supabase.table("materias_primas").select("*").execute()
        df_mp = pd.DataFrame(response_mp.data)
        df_mp["%"] = 0.0
    except Exception as e:
        st.error(f"❌ Error al cargar materias primas: {e}")
        return

    actuales = pd.DataFrame(json.loads(data["materias_primas"]))
    for _, row in actuales.iterrows():
        mask = df_mp["Materia Prima"] == row["Materia Prima"]
        if mask.any():
            df_mp.loc[mask, "%"] = row["%"]

    seleccionadas = st.multiselect(
        "Materias primas",
        df_mp["Materia Prima"].tolist(),
        default=actuales["Materia Prima"].tolist(),
        key="mp_actualizar",
    )

    if not seleccionadas:
        st.warning("Selecciona al menos una materia prima.")
        return

    df_editado, total_pct = mostrar_editor_formula(df_mp, seleccionadas)

    if df_editado is None:
        return

    familias = obtener_familias_parametros()
    columnas = [col for fam in familias.values() for col in fam]

    if st.button("Guardar cambios"):
        try:
            precio, _ = calcular_resultado_formula(df_editado, columnas)
            supabase.table("formulas").update({
                "nombre": nombre,
                "materias_primas": json.dumps(df_editado.to_dict(orient="records")),
                "precio_total": round(precio, 2),
            }).eq("id", formula_id).execute()
            st.success("Fórmula actualizada correctamente.")
        except Exception as e:
            st.error(f"❌ Error al actualizar: {e}")
