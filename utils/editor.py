# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
from utils.families import obtener_familias_parametros

def mostrar_editor_formula(df, seleccionadas):
    # Filtrar en el mismo orden que fueron seleccionadas
    orden_dict = {nombre: i + 1 for i, nombre in enumerate(seleccionadas)}
    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()
    df_filtrado["Orden"] = df_filtrado["Materia Prima"].map(orden_dict)

    if df_filtrado.empty:
        return None, 0.0

    columnas_default = obtener_familias_parametros()
    columnas_composicion = [col for sub in columnas_default.values() for col in sub]

    columnas_mostrar = ["Orden", "Materia Prima", "Precio €/kg", "%"] + [
        col for col in df.columns if col in columnas_composicion
    ]

    df_filtrado = df_filtrado.sort_values("Orden")

    df_editado = st.data_editor(
        df_filtrado[columnas_mostrar],
        use_container_width=True,
        key="formula_editor"
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")
    return df_editado, total_pct


    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")
    return df_editado, total_pct
