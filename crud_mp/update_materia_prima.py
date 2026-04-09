# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd
import numpy as np
from utils.supabase_client import supabase


def _sort_by_name_if_present(df: pd.DataFrame) -> pd.DataFrame:
    if not df.empty and "Materia Prima" in df.columns:
        return df.sort_values("Materia Prima", ascending=True).reset_index(drop=True)
    return df


def actualizar_materia_prima():
    st.subheader("✏️ Actualizar materias primas")

    # Cargar datos desde Supabase
    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    # Ordenar alfabéticamente por nombre, si existe
    df = _sort_by_name_if_present(df)

    if df.empty:
        st.info("No hay materias primas disponibles.")
        return

    # Tabla editable con AgGrid (misma estrategia que otras vistas que ya funcionan)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        editable=True,
        filter=True,
        sortable=True,
        floatingFilter=True,
        width=120,
        minWidth=100,
        resizable=True,
    )
    if "id" in df.columns:
        gb.configure_column("id", editable=False)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        fit_columns_on_grid_load=False,
        height=600,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
    )

    edited_df = grid_response["data"]

    if st.button("💾 Guardar cambios"):
        # 🔧 Limpieza para evitar columnas fantasma y NaN → None
        cleaned_df = pd.DataFrame(edited_df).copy()

        # Columnas auxiliares de AgGrid o índices heredados
        for col in ["__rowIndex__", "index", "index_level_0", "_index"]:
            if col in cleaned_df.columns:
                cleaned_df = cleaned_df.drop(columns=[col])

        cleaned_df = cleaned_df.reset_index(drop=True)
        cleaned_df = cleaned_df.replace({np.nan: None})

        try:
            supabase.table("materias_primas").upsert(
                cleaned_df.to_dict(orient="records"),
                on_conflict=["id"],
            ).execute()
            st.success("Cambios guardados correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")

