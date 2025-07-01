import streamlit as st
import pandas as pd
import numpy as np
from supabase_client import supabase

def actualizar_materia_prima():
    st.subheader("✏️ Actualizar materias primas")

    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.info("No hay materias primas disponibles.")
        return

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="editor_actualizar",
        column_config={col: st.column_config.Column(disabled=(col == "id")) for col in df.columns}
    )

    if st.button("💾 Guardar cambios"):
        if "Materia Prima" not in edited_df.columns or "id" not in edited_df.columns:
            st.error("Faltan columnas obligatorias en los datos.")
            return

        cleaned_df = edited_df.replace({np.nan: None})
        try:
            supabase.table("materias_primas").upsert(
                cleaned_df.to_dict(orient="records"),
                on_conflict=["id"]
            ).execute()
            st.success("Cambios guardados correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
