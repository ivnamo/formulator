# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd
from utils.families import obtener_familias_parametros

def mostrar_editor_formula(df, seleccionadas):
    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy().reset_index(drop=True)

    if df_filtrado.empty:
        return pd.DataFrame(), 0.0

    # Solo mostrar columnas básicas: Materia Prima y %
    columnas_mostrar = ["Materia Prima", "%"]

    gb = GridOptionsBuilder.from_dataframe(df_filtrado[columnas_mostrar])
    gb.configure_default_column(resizable=True, filter=False, sortable=False)

    gb.configure_column("Materia Prima", editable=False, rowDrag=True, width=240, filter=False)
    gb.configure_column("%", editable=True, width=70, filter=False)

    gb.configure_grid_options(rowDragManaged=True)

    grid_options = gb.build()

    grid_response = AgGrid(
        df_filtrado[columnas_mostrar],
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        height=300,
        allow_unsafe_jscode=True,
        theme="streamlit",
        enable_enterprise_modules=False
    )

    df_editado = grid_response["data"].copy()

    if "__rowIndex__" in df_editado.columns:
        df_editado.sort_values("__rowIndex__", inplace=True)
        df_editado.drop(columns="__rowIndex__", inplace=True)

    if "%" not in df_editado.columns and "%" in df_filtrado.columns:
        df_editado["%"] = df_filtrado["%"]

    df_editado.reset_index(drop=True, inplace=True)

    # Reordenar columnas para mantener solo las visibles
    columnas_ordenadas = [col for col in columnas_mostrar if col in df_editado.columns]
    df_editado = df_editado[columnas_ordenadas]

    df_vista = df_editado.rename(columns={"%": "Porcentaje"}).copy()
    st.dataframe(df_vista, use_container_width=True)

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    return df_editado, total_pct


