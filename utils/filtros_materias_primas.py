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

        # Valores por defecto
        precio_min_def = float(df["Precio €/kg"].min())
        precio_max_def = float(df["Precio €/kg"].max())
        columnas_familias = obtener_familias_parametros()

        # Reset seguro
        if st.button("🔄 Resetear filtros"):
            for k in list(st.session_state.keys()):
                if k.startswith(("nombre_filtro", "precio_minmax", "filtro_")) or k.startswith("slider_"):
                    st.session_state.pop(k, None)
            st.rerun()

        # Filtros
        nombre_filtro = st.text_input("Buscar por nombre", key="nombre_filtro")

        precio_min, precio_max = st.slider(
            "Rango de precio €/kg",
            min_value=precio_min_def,
            max_value=precio_max_def,
            value=(precio_min_def, precio_max_def),
            step=0.1,
            key="precio_minmax"
        )

        familias_sel = st.multiselect(
            "Filtrar por familias presentes",
            options=list(columnas_familias.keys()),
            key="filtro_familias"
        )

        columnas_tecnicas = [col for sub in columnas_familias.values() for col in sub if col in df.columns]

        columnas_filtrar = st.multiselect(
            "Filtrar por columnas técnicas",
            options=columnas_tecnicas,
            key="filtro_columnas"
        )

        # Filtros por columnas seleccionadas
        filtros_aplicados = []
        for col in columnas_filtrar:
            if col in df.columns:
                min_val = float(df[col].min(skipna=True))
                max_val = float(df[col].max(skipna=True))
                val_min, val_max = st.slider(
                    f"Rango para {col}",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    step=0.01,
                    key=f"slider_{col}"
                )
                filtros_aplicados.append((col, val_min, val_max))

        # Aplicar filtros al DataFrame
        if nombre_filtro:
            df_filtrado = df_filtrado[df_filtrado["Materia Prima"].str.contains(nombre_filtro, case=False, na=False)]

        df_filtrado = df_filtrado[df_filtrado["Precio €/kg"].between(precio_min, precio_max)]

        if familias_sel:
            columnas_familia = [
                col for fam in familias_sel for col in columnas_familias[fam] if col in df_filtrado.columns
            ]
            if columnas_familia:
                suma_familia = df_filtrado[columnas_familia].fillna(0).sum(axis=1)
                df_filtrado = df_filtrado[suma_familia > 0]

        for col, min_v, max_v in filtros_aplicados:
            df_filtrado = df_filtrado[df_filtrado[col].between(min_v, max_v)]

    return df_filtrado
