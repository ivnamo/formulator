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

        # Valores por defecto fijos
        precio_min_def = float(df["Precio €/kg"].min())
        precio_max_def = float(df["Precio €/kg"].max())
        VALORES_DEFECTO = {
            "nombre_filtro": "",
            "precio_minmax": (precio_min_def, precio_max_def),
            "filtro_familias": [],
            "filtro_columnas": []
        }

        if st.button("🔄 Resetear filtros"):
            for k in VALORES_DEFECTO:
                st.session_state.pop(k, None)
            st.session_state["reset_filtros_mp"] = False
            st.rerun()

        # Inicializar valores solo si no existen
        if "nombre_filtro" not in st.session_state:
            st.session_state["nombre_filtro"] = VALORES_DEFECTO["nombre_filtro"]
        if "precio_minmax" not in st.session_state:
            st.session_state["precio_minmax"] = VALORES_DEFECTO["precio_minmax"]
        if "filtro_familias" not in st.session_state:
            st.session_state["filtro_familias"] = VALORES_DEFECTO["filtro_familias"]
        if "filtro_columnas" not in st.session_state:
            st.session_state["filtro_columnas"] = VALORES_DEFECTO["filtro_columnas"]

        # Widgets
        nombre_filtro = st.text_input(
            "Buscar por nombre",
            value=st.session_state["nombre_filtro"],
            key="nombre_filtro"
        )

        precio_min, precio_max = st.slider(
            "Rango de precio €/kg",
            min_value=precio_min_def,
            max_value=precio_max_def,
            value=st.session_state["precio_minmax"],
            step=0.1,
            key="precio_minmax"
        )

        familias = obtener_familias_parametros()
        familias_sel = st.multiselect(
            "Filtrar por familias presentes",
            options=list(familias.keys()),
            default=st.session_state["filtro_familias"],
            key="filtro_familias"
        )

        columnas_tecnicas = [col for sub in familias.values() for col in sub if col in df.columns]

        columnas_filtrar = st.multiselect(
            "Filtrar por columnas técnicas",
            options=columnas_tecnicas,
            default=st.session_state["filtro_columnas"],
            key="filtro_columnas"
        )

        # Sliders para columnas técnicas seleccionadas
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
                col for fam in familias_sel for col in familias[fam] if col in df_filtrado.columns
            ]
            if columnas_familia:
                suma_familia = df_filtrado[columnas_familia].fillna(0).sum(axis=1)
                df_filtrado = df_filtrado[suma_familia > 0]

        for col, min_v, max_v in filtros_aplicados:
            df_filtrado = df_filtrado[df_filtrado[col].between(min_v, max_v)]

    return df_filtrado
