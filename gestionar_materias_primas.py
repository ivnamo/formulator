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
        supabase.table("materias_primas").delete().neq("id", 0).execute()
        supabase.table("materias_primas").insert(edited_df.to_dict(orient="records")).execute()
        st.success("Cambios guardados correctamente en Supabase.")
