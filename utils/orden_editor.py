# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------
# utils/orden_editor.py

# utils/orden_editor.py

import streamlit as st
import pandas as pd

def mostrar_editor_orden(df_editado):
    """
    Tabla editable con columna 'Orden'. Al aplicar, se reordena en el mismo sitio.
    """
    st.markdown("### 📋 Orden de materias primas")

    # Inicializar solo si no existe
    if "orden_df" not in st.session_state or st.session_state.get("orden_df_len", 0) != len(df_editado):
        st.session_state.orden_df = pd.DataFrame({
            "Orden": list(range(1, len(df_editado) + 1)),
            "Materia Prima": df_editado["Materia Prima"].values,
            "%": df_editado["%"].values
        })
        st.session_state.orden_df_len = len(df_editado)

    with st.expander("🧭 Ordenar materias primas", expanded=True):
        orden_editado = st.data_editor(
            st.session_state.orden_df,
            column_config={
                "Materia Prima": st.column_config.Column(disabled=True),
                "%": st.column_config.Column(disabled=True)
            },
            use_container_width=True,
            key="orden_editor",
            hide_index=True
        )

        if st.button("🔄 Aplicar orden personalizado"):
            orden_editado = orden_editado.sort_values("Orden").reset_index(drop=True)
            st.session_state.orden_df = orden_editado
            st.success("✔ Orden actualizado.")
