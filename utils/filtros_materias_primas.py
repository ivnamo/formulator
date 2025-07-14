import streamlit as st
import pandas as pd
from .families import obtener_familias_parametros

def aplicar_filtros_materias_primas(df: pd.DataFrame) -> pd.DataFrame:
    """Muestra controles de filtro y devuelve un DataFrame filtrado."""
    df_filtrado = df.copy()

    with st.expander("🧪 Filtro avanzado para seleccionar materias primas"):
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

        columnas_tecnicas = [col for sublist in familias.values() for col in sublist if col in df.columns]

        filtros_aplicados = []
        if st.checkbox("Agregar filtros técnicos personalizados"):
            for col in columnas_tecnicas:
                usar = st.checkbox(f"{col}", value=False, key=f"usar_filtro_{col}")
                if usar:
                    operador = st.selectbox(f"Condición para {col}", [">", ">=", "<", "<=", "="], key=f"op_filtro_{col}")
                    valor = st.number_input(f"Valor para {col}", step=0.01, key=f"val_filtro_{col}")
                    filtros_aplicados.append((col, operador, valor))

        # Aplicar todos los filtros
        if nombre_filtro:
            df_filtrado = df_filtrado[df_filtrado["Materia Prima"].str.contains(nombre_filtro, case=False, na=False)]

        df_filtrado = df_filtrado[df_filtrado["Precio €/kg"].between(precio_min, precio_max)]

        if familias_sel:
            columnas_familia = [col for f in familias_sel for col in familias[f] if col in df_filtrado.columns]
            df_filtrado = df_filtrado[df_filtrado[columnas_familia].notna().any(axis=1)]

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
