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
    Muestra una única tabla editable con columnas: Orden, Materia Prima y %.
    Permite modificar el orden y reordenar la tabla en el mismo lugar.

    Args:
        df_editado (pd.DataFrame): DataFrame con las columnas 'Materia Prima' y '%'.

    Returns:
        pd.DataFrame: df_editado reordenado según la columna 'Orden'.
    """
    st.markdown("### 📋 Orden de materias primas")

    # Crear tabla editable con Orden inicial
    if "orden_editor_df" not in st.session_state:
        st.session_state.orden_editor_df = pd.DataFrame({
            "Orden": list(range(1, len(df_editado) + 1)),
            "Materia Prima": df_editado["Materia Prima"].values,
            "%": df_editado["%"].values
        })

    # Mostrar editor con solo Orden editable
    st.session_state.orden_editor_df = st.data_editor(
        st.session_state.orden_editor_df,
        column_config={
            "Materia Prima": st.column_config.Column(disabled=True),
            "%": st.column_config.Column(disabled=True)
        },
        use_container_width=True,
        key="orden_editor"
    )

    # Botón para aplicar el reordenamiento
    if st.button("🔄 Reordenar materias primas según orden"):
        st.session_state.orden_editor_df = st.session_state.orden_editor_df.sort_values("Orden").reset_index(drop=True)

    return st.session_state.orden_editor_df
