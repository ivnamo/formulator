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
    Muestra una tabla editable para ordenar materias primas, y reordena en el mismo sitio.
    """
    st.markdown("### 📋 Orden de materias primas")

    # Inicializar tabla de orden si no existe aún en sesión
    if "orden_df" not in st.session_state:
        st.session_state.orden_df = pd.DataFrame({
            "Orden": list(range(1, len(df_editado) + 1)),
            "Materia Prima": df_editado["Materia Prima"].values,
            "%": df_editado["%"].values
        })

    # Mostrar editor con columna Orden editable
    st.session_state.orden_df = st.data_editor(
        st.session_state.orden_df,
        column_config={
            "Materia Prima": st.column_config.Column(disabled=True),
            "%": st.column_config.Column(disabled=True)
        },
        use_container_width=True,
        key="orden_editor",
        hide_index=True
    )

    # Reordenar al pulsar botón
    if st.button("🔄 Reordenar según número de orden"):
        st.session_state.orden_df = st.session_state.orden_df.sort_values("Orden").reset_index(drop=True)

