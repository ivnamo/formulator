# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.families import obtener_familias_parametros
from utils.optimizador_simplex import optimizar_simplex
from utils.formula_resultados import calcular_resultado_formula
from utils.resultados import mostrar_resultados

def flujo_optimizar_formula():
    st.title("🧮 Optimización de Fórmulas")

    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)
    df["%"] = 0.0

    if df.empty or "Materia Prima" not in df.columns:
        st.error("No hay materias primas disponibles o falta la columna 'Materia Prima'.")
        return

    seleccionadas = st.multiselect("Selecciona materias primas para optimizar", df["Materia Prima"].dropna().tolist())
    if not seleccionadas:
        st.info("Selecciona al menos una materia prima para empezar.")
        return

    df_seleccion = df[df["Materia Prima"].isin(seleccionadas)].copy()

    familias = obtener_familias_parametros()
    seleccionadas_familias = st.multiselect("Selecciona familias de parámetros", list(familias), default=list(familias))
    columnas_tecnicas = [col for fam in seleccionadas_familias for col in familias[fam] if col in df.columns]

    columnas_param_opt = [col for col in columnas_tecnicas if df_seleccion[col].fillna(0).gt(0).any()]
    columnas_restricciones = st.multiselect("Selecciona parámetros a restringir", columnas_param_opt)

    restricciones = {}
    for col in columnas_restricciones:
        valores = df_seleccion[col].fillna(0)
        min_val = float(valores.min())
        max_val = float(valores.max())
        val_min, val_max = st.slider(f"Rango para {col} (%)", min_value=min_val, max_value=max_val, value=(min_val, max_val), step=0.01)
        restricciones[col] = {"min": val_min, "max": val_max}

    if st.button("🔧 Ejecutar optimización"):
        try:
            restricciones_min = {k: v["min"] for k, v in restricciones.items()}
            restricciones_max = {k: v["max"] for k, v in restricciones.items()}
            df_opt, costo = optimizar_simplex(df_seleccion, columnas_tecnicas, restricciones_min, restricciones_max)

            st.success(f"✅ Fórmula optimizada. Costo total: {costo:.2f} €/kg")
            st.dataframe(df_opt[["Materia Prima", "%", "Precio €/kg"] + columnas_tecnicas])

            st.markdown("### 📊 Composición de la fórmula optimizada")
            _, composicion = calcular_resultado_formula(df_opt, columnas_tecnicas)
            mostrar_resultados(df_opt, columnas_tecnicas)

        except Exception as e:
            st.error(f"❌ Error en la optimización: {e}")
