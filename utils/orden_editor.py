# utils/orden_editor.py

import streamlit as st
import pandas as pd

def mostrar_editor_orden(df_editado):
    """
    Muestra una tabla con columnas Orden, Materia Prima y %, permitiendo
    modificar el orden y reordenar la tabla con un botón.

    Args:
        df_editado (pd.DataFrame): DataFrame con las columnas 'Materia Prima' y '%'

    Returns:
        pd.DataFrame: DataFrame ordenado según el nuevo orden indicado, o None si no se reordenó.
    """
    st.markdown("### 📋 Orden de materias primas")

    tabla_orden = pd.DataFrame({
        "Orden": list(range(1, len(df_editado) + 1)),
        "Materia Prima": df_editado["Materia Prima"].values,
        "%": df_editado["%"].values
    })

    orden_editado = st.data_editor(
        tabla_orden,
        column_config={
            "Materia Prima": st.column_config.Column(disabled=True),
            "%": st.column_config.Column(disabled=True)
        },
        use_container_width=True,
        key="orden_editor"
    )

    if st.button("🔄 Reordenar materias primas según orden"):
        orden_ordenado = orden_editado.sort_values(by="Orden").reset_index(drop=True)
        st.dataframe(orden_ordenado, use_container_width=True)
        return orden_ordenado

    return None
