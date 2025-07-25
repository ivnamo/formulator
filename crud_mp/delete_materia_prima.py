# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------


import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.data_loader import cargar_datos


def eliminar_materia_prima():
    st.subheader("🗑️ Eliminar materia prima")

    #response = supabase.table("materias_primas").select('id, "Materia Prima"').execute()
    #df = pd.DataFrame(response.data)
    df = cargar_datos()


    if df.empty:
        st.info("No hay materias primas para eliminar.")
        return

    if "confirmacion" not in st.session_state:
        st.session_state.confirmacion = False

    opciones = [""] + df["Materia Prima"].tolist()
    seleccion = st.selectbox("Selecciona una materia prima para eliminar", opciones, index=0, key="seleccion_combo")

    if seleccion:
        fila = df[df["Materia Prima"] == seleccion].iloc[0]
        st.session_state.confirmacion = st.checkbox("Confirmo que deseo eliminar esta materia prima", key="confirmar_checkbox")

        if st.button("Eliminar"):
            if st.session_state.confirmacion:
                try:
                    supabase.table("materias_primas").delete().eq("id", int(fila["id"])).execute()
                    st.success("Materia prima eliminada correctamente.")
                    st.session_state.confirmacion = False
                    del st.session_state["seleccion_combo"]
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al eliminar: {e}")
            else:
                st.warning("Debes confirmar antes de eliminar.")

