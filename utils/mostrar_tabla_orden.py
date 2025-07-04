import streamlit as st
import pandas as pd

def mostrar_tabla_orden(df_editado):
    """
    Muestra una tabla con columnas: Orden, Materia Prima y %, 
    permitiendo editar el orden y reordenar las filas.
    """
    st.markdown("### 📋 Orden de materias primas")

    # Crear DataFrame base para la tabla de orden
    tabla_orden = pd.DataFrame({
        "Orden": list(range(1, len(df_editado) + 1)),
        "Materia Prima": df_editado["Materia Prima"].values,
        "%": df_editado["%"].values
    })

    # Mostrar editor con solo "Orden" editable
    orden_editado = st.data_editor(
        tabla_orden,
        column_config={
            "Materia Prima": st.column_config.Column(disabled=True),
            "%": st.column_config.Column(disabled=True)
        },
        use_container_width=True,
        key="orden_editor"
    )

    # Reordenar si se presiona el botón
    if st.button("🔄 Reordenar materias primas según orden"):
        orden_editado = orden_editado.sort_values(by="Orden").reset_index(drop=True)
        st.dataframe(orden_editado, use_container_width=True)

    return orden_editado
