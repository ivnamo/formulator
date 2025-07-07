# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import json
from utils.supabase_client import supabase
from utils.formula_resultados import calcular_resultado_formula

def cargar_formula_por_id(formula_id: str):
    """
    Carga y muestra una fórmula en modo solo lectura, a partir del ID en Supabase.

    Args:
        formula_id (str): UUID de la fórmula a cargar.
    """
    st.subheader("📄 Fórmula guardada")

    try:
        response = supabase.table("formulas").select("*").eq("id", formula_id).single().execute()
        data = response.data

        if data is None:
            st.error("❌ No se encontró ninguna fórmula con ese ID.")
            return

        nombre = data["nombre"]
        precio = data["precio_total"]
        materias_primas = pd.DataFrame(json.loads(data["materias_primas"]))

        st.markdown(f"### 🧪 **{nombre}**")
        st.markdown(f"**💰 Precio por kg:** {precio:.2f} €")

        # 🔒 Reordenar y renombrar columna % para mejor visualización
        materias_vista = materias_primas.copy()
        if "%" in materias_vista.columns:
            materias_vista.rename(columns={"%": "Porcentaje"}, inplace=True)
            cols = materias_vista.columns.tolist()
            if "Porcentaje" in cols and "Materia Prima" in cols:
                cols = [col for col in cols if col in ["Materia Prima", "Porcentaje"]]
                materias_vista = materias_vista[cols]

        st.dataframe(materias_vista, use_container_width=True)

        columnas = [col for col in materias_primas.columns if col not in ["id", "Materia Prima", "Precio €/kg", "%"]]
        precio_calc, composicion = calcular_resultado_formula(materias_primas, columnas)

        st.markdown("#### 📊 Composición estimada")
        composicion = composicion[composicion["Cantidad %"] > 0]  # ❌ Eliminar valores cero
        if not composicion.empty:
            composicion_formateada = composicion.reset_index()
            composicion_formateada.columns = ["Parámetro", "% p/p"]
            st.markdown(composicion_formateada.to_html(index=False), unsafe_allow_html=True)
        else:
            st.info("No hay parámetros significativos en la fórmula.")
    except Exception as e:
        st.error(f"⚠️ Error al cargar la fórmula: {e}")

