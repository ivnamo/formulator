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

    # ✅ Mostrar más columnas en AgGrid (no solo %)
    columnas_vista = ["Materia Prima", "%", "Precio €/kg"] + [
        col for col in df_filtrado.columns
        if col not in ["Materia Prima", "%", "Precio €/kg", "id"]
    ]

    # 🔧 Configurar el editor visual (solo % editable)
    gb = GridOptionsBuilder.from_dataframe(df_filtrado[columnas_vista])
    gb.configure_default_column(resizable=True, filter=False, sortable=False)
    gb.configure_column("Materia Prima", editable=False, rowDrag=True, width=240, filter=False)
    gb.configure_column("%", editable=True, width=70, filter=False)
    gb.configure_grid_options(rowDragManaged=True)

    grid_response = AgGrid(
        df_filtrado[columnas_vista],
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=False,
        height=300,
        allow_unsafe_jscode=True,
        theme="streamlit",
        enable_enterprise_modules=False
    )

    # 🧩 Actualizar % en el dataframe original completo
    df_filtrado["%"] = grid_response["data"]["%"].values
    df_filtrado.reset_index(drop=True, inplace=True)

    # Tabla secundaria (por claridad)
    df_vista = df_filtrado[["Materia Prima", "%"]].rename(columns={"%": "Porcentaje"})
    st.dataframe(df_vista, use_container_width=True)

    total_pct = df_filtrado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")
    #st.code(f"Columnas devueltas: {df_filtrado.columns.tolist()}")

    return df_filtrado, total_pct


