# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.families import obtener_familias_parametros

def mostrar_editor_formula(df, seleccionadas):
    if "orden_personalizado" not in st.session_state:
        st.session_state.orden_personalizado = {}
    if "formula_editada" not in st.session_state:
        st.session_state.formula_editada = pd.DataFrame()

    orden_actual = st.session_state.orden_personalizado
    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()

    # Si no hay materias primas seleccionadas, limpiar valores guardados
    if not seleccionadas:
        st.session_state.formula_editada = pd.DataFrame()
        return pd.DataFrame(), 0.0

    # Detectar nuevas materias primas y asignarles orden nuevo
    max_orden = max(orden_actual.values(), default=0)
    for mp in seleccionadas:
        if mp not in orden_actual:
            max_orden += 1
            orden_actual[mp] = max_orden

    df_filtrado["Orden"] = df_filtrado["Materia Prima"].map(orden_actual)

    # Recuperar valores previos fila a fila, solo si no está ya editando
    if st.session_state.formula_editada.empty is False and st.session_state.get("editando_formula") is not True:
        df_guardado = st.session_state.formula_editada
        columnas_a_copiar = [
            col for col in df_guardado.columns
            if col in df_filtrado.columns and col not in ["Orden", "Materia Prima"]
        ]
        for mp in seleccionadas:
            if mp in df_guardado["Materia Prima"].values:
                fila_guardada = df_guardado[df_guardado["Materia Prima"] == mp].iloc[0]
                for col in columnas_a_copiar:
                    df_filtrado.loc[df_filtrado["Materia Prima"] == mp, col] = fila_guardada[col]

    columnas_default = obtener_familias_parametros()
    columnas_composicion = [col for sub in columnas_default.values() for col in sub]
    columnas_mostrar = ["Orden", "Materia Prima", "Precio €/kg", "%"] + [
        col for col in df.columns if col in columnas_composicion
    ]

    df_filtrado = df_filtrado.sort_values("Orden").reset_index(drop=True)

    # Mostrar editor
    df_editado = st.data_editor(
        df_filtrado[columnas_mostrar],
        use_container_width=True,
        key="formula_editor",
        hide_index=True
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    # Guardar si el usuario pulsa botón
    if st.button("✅ Aplicar nuevo orden manual"):
        if "Orden" in df_editado.columns and "Materia Prima" in df_editado.columns:
            nuevo_orden_df = df_editado[["Materia Prima", "Orden"]].drop_duplicates()
            nuevo_orden_df = nuevo_orden_df.dropna(subset=["Orden"]).copy()
            nuevo_orden_df["Orden"] = nuevo_orden_df["Orden"].astype(int)
            nuevo_orden_df = nuevo_orden_df.sort_values("Orden").reset_index(drop=True)
            nuevo_orden_df["Orden"] = range(1, len(nuevo_orden_df) + 1)

            st.session_state.orden_personalizado = {
                row["Materia Prima"]: row["Orden"] for _, row in nuevo_orden_df.iterrows()
            }

            st.session_state.formula_editada = df_editado.copy()
            st.session_state.editando_formula = False
            st.rerun()
    else:
        # Si no se pulsa el botón, asumimos que está editando y no sobrescribimos nada
        st.session_state.editando_formula = True

    return df_editado, total_pct
