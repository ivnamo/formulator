# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd

def mostrar_editor_orden(df_editado):
    """
    Muestra una tabla independiente para ordenar las materias primas por número,
    dentro de un colapsable que se autocierra tras reordenar.
    """
    if "orden_colapsado" not in st.session_state:
        st.session_state.orden_colapsado = True

    with st.expander("📋 Orden de materias primas", expanded=st.session_state.orden_colapsado):
        orden_df = pd.DataFrame({
            "Orden": list(range(1, len(df_editado) + 1)),
            "Materia Prima": df_editado["Materia Prima"].values,
            "%": df_editado["%"].values
        })

        orden_editado = st.data_editor(
            orden_df,
            column_config={
                "Materia Prima": st.column_config.Column(disabled=True),
                "%": st.column_config.Column(disabled=True),
            },
            use_container_width=True,
            key="orden_editor",
            hide_index=True
        )

        if st.button("🔄 Reordenar materias primas según orden"):
            ordenado = orden_editado.sort_values("Orden").reset_index(drop=True)
            st.session_state.orden_colapsado = False  # autocolapsar
            st.markdown("#### 🧾 Materias primas reordenadas")
            st.dataframe(ordenado, use_container_width=True, hide_index=True)

