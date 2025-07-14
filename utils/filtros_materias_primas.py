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
        VALORES_DEFECTO = {
            "nombre_filtro": "",
            "precio_minmax": (
                float(df["Precio €/kg"].min()),
                float(df["Precio €/kg"].max())
            ),
            "filtro_familias": [],
            "filtro_columnas": []
        }

        if st.button("🔄 Resetear filtros"):
            st.session_state["reset_filtros_mp"] = True
            st.rerun()

        if st.session_state.get("reset_filtros_mp"):
            for k, v in VALORES_DEFECTO.items():
                st.session_state[k] = v
            st.session_state["reset_filtros_mp"] = False
            st.rerun()

        nombre_filtro = st.text_input(
            "Buscar por nombre",
            value=VALORES_DEFECTO["nombre_filtro"],
            key="nombre_filtro"
        )

        precio_min, precio_max = st.slider(
            "Rango de precio €/kg",
            min_value=float(df["Precio €/kg"].min()),
            max_value=float(df["Precio €/kg"].max()),
            value=VALORES_DEFECTO["precio_minmax"],
            step=0.1,
            key="precio_minmax"
        )

        familias = obtener_familias_parametros()
        familias_sel = st.multiselect(
            "Filtrar por familias presentes",
            list(familias.keys()),
            default=VALORES_DEFECTO["filtro_familias"],
            key="filtro_familias"
        )

        columnas_tecnicas = [col for sub in familias.values() for col in sub if col in df.columns]

        filtros_aplicados = []
        columnas_filtrar = st.multiselect(
            "Filtrar por columnas técnicas",
            columnas_tecnicas,
            default=VALORES_DEFECTO["filtro_columnas"],
            key="filtro_columnas"
        )

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

        # Aplicar filtros
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

