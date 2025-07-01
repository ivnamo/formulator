import streamlit as st
import pandas as pd
from supabase_client import supabase

def eliminar_materia_prima():
    st.subheader("🗑️ Eliminar materia prima")

    response = supabase.table("materias_primas").select('id, "Materia Prima"').execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.info("No hay materias primas para eliminar.")
        return

    opciones = df["Materia Prima"].tolist()
    seleccion = st.selectbox("Selecciona una materia prima para eliminar", opciones)
    fila = df[df["Materia Prima"] == seleccion].iloc[0]

    confirmar = st.checkbox("Confirmo que deseo eliminar esta materia prima")
    if st.button("Eliminar"):
        if confirmar:
            try:
                supabase.table("materias_primas").delete().eq("id", int(fila["id"])).execute()
                st.success("Materia prima eliminada correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al eliminar: {e}")
        else:
            st.warning("Debes confirmar antes de eliminar.")
