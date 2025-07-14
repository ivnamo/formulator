# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from .families import obtener_familias_parametros


def aplicar_filtros_materias_primas(df: pd.DataFrame) -> pd.DataFrame:
    """Muestra controles de filtro y devuelve un DataFrame filtrado."""
    df_filtrado = df.copy()

    with st.expander("🧪 Filtro avanzado para seleccionar materias primas"):
        if st.button("🔄 Resetear filtros"):
            st.experimental_rerun()

        nombre_filtro = st.text_input("Buscar por nombre")
        precio_min, precio_max = st.slider(
            "Rango de precio €/kg",
            min_value=0.0,
            max_value=float(df["Precio €/kg"].max()) if not df.empty else 100.0,
            value=(0.0, float(df["Precio €/kg"].max()) if not df.empty else 100.0),
            step=0.1
        )

        familias = obtener_familias_parametros()
        familias_sel = st.multiselect("Filtrar por familias presentes", list(familias.keys()))

        columnas_tecnicas = [col for sub in familias.values() for col in sub if col in df.columns]

        filtros_aplicados = []
        if st.checkbox("Agregar filtros técnicos personalizados"):
            num_filtros = st.number_input("Número de condiciones", min_value=1, max_value=10, value=1, step=1)

            for i in range(int(num_filtros)):
                col = st.selectbox(f"Columna #{i+1}", columnas_tecnicas, key=f"col_filtro_{i}")
                op = st.selectbox(f"Condición #{i+1}", [">", ">=", "<", "<=", "="], key=f"op_filtro_{i}")
                val = st.number_input(f"Valor #{i+1}", step=0.01, key=f"val_filtro_{i}")
                filtros_aplicados.append((col, op, val))

        # Aplicar todos los filtros
        if nombre_filtro:
            df_filtrado = df_filtrado[df_filtrado["Materia Prima"].str.contains(nombre_filtro, case=False, na=False)]

        df_filtrado = df_filtrado[df_filtrado["Precio €/kg"].between(precio_min, precio_max)]

        if familias_sel:
            columnas_familia = [
                col for fam in familias_sel for col in familias[fam] if col in df_filtrado.columns
            ]
            if columnas_familia:
                suma_familia = df_filtrado[columnas_familia].fillna(0).sum(axis=1)
                df_filtrado = df_filtrado[suma_familia > 0]

        for col, op, val in filtros_aplicados:
            if col in df_filtrado.columns:
                if op == ">":
                    df_filtrado = df_filtrado[df_filtrado[col] > val]
                elif op == ">=":
                    df_filtrado = df_filtrado[df_filtrado[col] >= val]
                elif op == "<":
                    df_filtrado = df_filtrado[df_filtrado[col] < val]
                elif op == "<=":
                    df_filtrado = df_filtrado[df_filtrado[col] <= val]
                elif op == "=":
                    df_filtrado = df_filtrado[df_filtrado[col] == val]

    return df_filtrado

