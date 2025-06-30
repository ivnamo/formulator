import streamlit as st
import pandas as pd
from supabase_client import supabase

def gestionar_materias_primas():
    st.subheader("🧾 CRUD de Materias Primas")

    if "materias_df" not in st.session_state:
        response = supabase.table("materias_primas").select("*").execute()
        df = pd.DataFrame(response.data)
        st.session_state["materias_df"] = df

    edited_df = st.data_editor(
        st.session_state["materias_df"],
        use_container_width=True,
        num_rows="dynamic",
        key="editor_crud"
    )

    if st.button("💾 Guardar cambios"):
        st.session_state["materias_df"] = edited_df

        # Limpieza: reemplazar NaN por None
        cleaned_data = edited_df.where(pd.notnull(edited_df), None).to_dict(orient="records")

        try:
            supabase.table("materias_primas").delete().neq("id", 0).execute()
            supabase.table("materias_primas").insert(cleaned_data).execute()
            st.success("Cambios guardados correctamente en Supabase.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
