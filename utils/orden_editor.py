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
    Muestra una tabla independiente para ordenar las materias primas por número.

    Args:
        df_editado (pd.DataFrame): El dataframe principal (con todas las columnas).

    Returns:
        None. Solo muestra la tabla ordenada visualmente.
    """
    st.markdown("### 📋 Orden de materias primas")

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
        hide_index=True  # Oculta la columna gris de índice
    )

    if st.button("🔄 Reordenar materias primas según orden"):
        ordenado = orden_editado.sort_values("Orden").reset_index(drop=True)
        st.markdown("#### 🧾 Materias primas reordenadas")
        st.dataframe(ordenado, use_container_width=True, hide_index=True)
