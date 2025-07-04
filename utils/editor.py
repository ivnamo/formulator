# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
from utils.familias import obtener_familias_parametros

def mostrar_editor_formula(df, seleccionadas):
    if "orden_personalizado" not in st.session_state:
        st.session_state.orden_personalizado = {}

    # Obtener orden actual almacenado
    orden_actual = st.session_state.orden_personalizado

    # Crear df filtrado solo con seleccionadas
    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()

    # Asignar orden: preservar los existentes, asignar nuevos al final
    max_orden = max(orden_actual.values(), default=0)
    for mp in seleccionadas:
        if mp not in orden_actual:
            max_orden += 1
            orden_actual[mp] = max_orden

    # Aplicar orden a df_filtrado
    df_filtrado["Orden"] = df_filtrado["Materia Prima"].map(orden_actual)

    # Mostrar columnas relevantes
    columnas_default = obtener_familias_parametros()
    columnas_composicion = [col for sub in columnas_default.values() for col in sub]
    columnas_mostrar = ["Orden", "Materia Prima", "Precio €/kg", "%"] + [
        col for col in df.columns if col in columnas_composicion
    ]

    # Ordenar para mostrar
    df_filtrado = df_filtrado.sort_values("Orden")

    # Mostrar editor
    df_editado = st.data_editor(
        df_filtrado[columnas_mostrar],
        use_container_width=True,
        key="formula_editor"
    )

    # Guardar orden manual actualizado desde df_editado
    if "Orden" in df_editado.columns and "Materia Prima" in df_editado.columns:
        nuevo_orden = df_editado[["Materia Prima", "Orden"]].drop_duplicates()
        st.session_state.orden_personalizado = {
            row["Materia Prima"]: int(row["Orden"]) for _, row in nuevo_orden.iterrows()
        }

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")
    return df_editado, total_pct

