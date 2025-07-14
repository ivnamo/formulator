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
    st.subheader("🔎 Explorador de materias primas")

    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("No hay materias primas registradas.")
        return

    # Aplicar filtros definidos por el usuario
    df_filtrado = aplicar_filtros_materias_primas(df)

    if df_filtrado.empty:
        st.info("No hay resultados con los filtros aplicados.")
        return

    # Mostrar tabla con resultados
    st.markdown(f"### 📋 Resultados: {len(df_filtrado)} materia(s) prima(s)")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

