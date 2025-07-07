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

    columnas_default = obtener_familias_parametros()
    columnas_composicion = [col for sub in columnas_default.values() for col in sub]
    columnas_mostrar = ["Materia Prima", "Precio €/kg", "%"] + [
        col for col in df_filtrado.columns if col in columnas_composicion
    ]

    # Configuración sin filtros ni orden, con anchos controlados
    gb = GridOptionsBuilder.from_dataframe(df_filtrado[columnas_mostrar])
    gb.configure_default_column(editable=True, resizable=True, filter=False, sortable=False)

    # Columnas principales
    gb.configure_column("Materia Prima", editable=False, rowDrag=True, width=240, filter=False)
    gb.configure_column("Precio €/kg", width=100, filter=False)
    gb.configure_column("%", width=70, filter=False)

    # Columnas técnicas compactas sin filtro
    columnas_tecnicas = [col for col in columnas_mostrar if col not in ["Materia Prima", "Precio €/kg", "%"]]
    for col in columnas_tecnicas:
        gb.configure_column(col, width=70, filter=False)

    gb.configure_grid_options(rowDragManaged=True)

    grid_options = gb.build()

    grid_response = AgGrid(
        df_filtrado,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        height=300,
        allow_unsafe_jscode=True,
        theme="streamlit"
    )

    df_editado = grid_response["data"].copy()
    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    return df_editado, total_pct
