# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.filtros_materias_primas import aplicar_filtros_materias_primas


def ver_materia_prima():
    st.subheader("🔎 Ver y filtrar materias primas")

    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("No hay materias primas registradas.")
        return

    df_filtrado = aplicar_filtros_materias_primas(df)

    st.markdown("### Resultados filtrados")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

    if not df_filtrado.empty:
        if st.button("🧪 Usar estas materias primas en nueva fórmula"):
            st.session_state["mp_crear"] = df_filtrado["Materia Prima"].dropna().tolist()
            st.session_state["page"] = "crear_formula"
            st.rerun()
