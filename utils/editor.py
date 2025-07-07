from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd
from utils.families import obtener_familias_parametros

def mostrar_editor_formula(df, seleccionadas):
    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy().reset_index(drop=True)

    if df_filtrado.empty:
        return pd.DataFrame(), 0.0

    # Añadir columna de orden si no existe
    if "Orden" not in df_filtrado.columns:
        df_filtrado["Orden"] = range(1, len(df_filtrado) + 1)

    columnas_default = obtener_familias_parametros()
    columnas_composicion = [col for sub in columnas_default.values() for col in sub]
    columnas_mostrar = ["Orden", "Materia Prima", "Precio €/kg", "%"] + [
        col for col in df_filtrado.columns if col in columnas_composicion
    ]

    # Configuración de AgGrid
    gb = GridOptionsBuilder.from_dataframe(df_filtrado[columnas_mostrar])
    gb.configure_default_column(editable=True, resizable=True)
    gb.configure_column("Orden", editable=False, width=80)
    gb.configure_column("Materia Prima", editable=False, rowDrag=True)
    gb.configure_grid_options(rowDragManaged=True)

    grid_options = gb.build()

    # Mostrar tabla interactiva con drag-and-drop
    grid_response = AgGrid(
        df_filtrado,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        height=500,
        allow_unsafe_jscode=True
    )

    df_ordenado = grid_response["data"].copy()

    # Reordenar según el orden visual que el usuario ha creado
    df_ordenado = df_ordenado.sort_values("Orden").reset_index(drop=True)

    total_pct = df_ordenado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    return df_ordenado, total_pct
