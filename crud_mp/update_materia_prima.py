# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

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

    # Editor nativo de Streamlit (mas estable en Cloud que componentes externos)
    disabled_columns = ["id"] if "id" in df.columns else []
    edited_df = st.data_editor(
        df,
        num_rows="fixed",
        hide_index=True,
        width="stretch",
        disabled=disabled_columns,
        key="mp_data_editor",
    )

    if st.button("💾 Guardar cambios"):
        # 🔧 Limpieza para evitar columnas fantasma y NaN → None
        cleaned_df = pd.DataFrame(edited_df).copy()

        # Columnas auxiliares de editores o índices heredados
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

