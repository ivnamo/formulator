# utils/orden_editor.py

import streamlit as st
import pandas as pd

def mostrar_editor_orden(df_editado):
    """
    Muestra una única tabla editable para ordenar materias primas.

    Args:
        df_editado (pd.DataFrame): El DataFrame base con 'Materia Prima' y '%'.

    Returns:
        pd.DataFrame: DataFrame visualmente reordenado (para mostrar al usuario).
    """
    st.markdown("### 📋 Orden de materias primas")

    # Crear tabla de orden visual
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

    # Botón para reordenar en sitio
    if st.button("🔄 Reordenar según número de orden"):
        orden_editado = orden_editado.sort_values("Orden").reset_index(drop=True)

    # Mostramos la tabla ordenada (ya se muestra directamente al editar)
    return None  # ya se muestra, no se necesita devolver nada


