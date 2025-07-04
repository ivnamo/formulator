# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
from utils.families import obtener_familias_parametros

def mostrar_editor_formula(df, seleccionadas):
    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()
    if df_filtrado.empty:
        return None, 0.0

    # Asegurar columna 'Orden'
    if "Orden" not in df.columns:
        df["Orden"] = 0  # Inicializar en el df original para evitar que se pierda al filtrar
    if "Orden" not in df_filtrado.columns or (df_filtrado["Orden"] == 0).all():
        df_filtrado["Orden"] = list(range(1, len(df_filtrado) + 1))

    # Obtener columnas técnicas por familia
    columnas_default = obtener_familias_parametros()
    columnas_composicion = [col for sub in columnas_default.values() for col in sub]

    # Mostrar columnas
    columnas_mostrar = ["Orden", "Materia Prima", "Precio €/kg", "%"] + [
        col for col in df.columns if col in columnas_composicion
    ]

    # Ordenar por 'Orden'
    df_filtrado = df_filtrado.sort_values("Orden")

    # Mostrar editor
    df_editado = st.data_editor(
        df_filtrado[columnas_mostrar],
        use_container_width=True,
        key="formula_editor"
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")
    return df_editado, total_pct

