# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
from utils.supabase_client import supabase
from crud_formulas.list_formulas import listar_formulas


def eliminar_formula():
    st.subheader("🗑️ Eliminar fórmula")
    formula_id = listar_formulas(seleccionar=True)
    if not formula_id:
        return

    confirmar = st.checkbox("Confirmo que deseo eliminar esta fórmula")
    if st.button("Eliminar"):
        if confirmar:
            try:
                supabase.table("formulas").delete().eq("id", formula_id).execute()
                st.success("Fórmula eliminada correctamente.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Error al eliminar: {e}")
        else:
            st.warning("Debes confirmar antes de eliminar.")
