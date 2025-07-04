import streamlit as st
import pandas as pd
from utils.families import obtener_familias_parametros

def mostrar_editor_formula(df, seleccionadas):
    if "formula_editada" not in st.session_state or not isinstance(st.session_state.formula_editada, pd.DataFrame):
        st.session_state.formula_editada = pd.DataFrame()

    # Detectar cambio de selección
    seleccionadas_previas = st.session_state.get("seleccionadas_previas", [])
    cambio_en_seleccion = seleccionadas != seleccionadas_previas
    st.session_state["seleccionadas_previas"] = seleccionadas.copy()

    if cambio_en_seleccion and "formula_editor" in st.session_state:
        try:
            st.session_state.formula_editada = pd.DataFrame(st.session_state["formula_editor"]).copy()
        except Exception:
            pass

    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()

    if not seleccionadas:
        st.session_state.formula_editada = pd.DataFrame()
        return pd.DataFrame(), 0.0

    # Cargar datos anteriores si existen
    nuevas = (
        [mp for mp in seleccionadas if mp not in st.session_state.formula_editada["Materia Prima"].values]
        if not st.session_state.formula_editada.empty
        else seleccionadas
    )

    if not st.session_state.formula_editada.empty and (not st.session_state.get("editando_formula") or nuevas):
        df_guardado = st.session_state.formula_editada
        columnas_a_copiar = [
            col for col in df_guardado.columns
            if col in df_filtrado.columns and col not in ["Materia Prima"]
        ]
        for mp in seleccionadas:
            if mp in df_guardado["Materia Prima"].values:
                fila_guardada = df_guardado[df_guardado["Materia Prima"] == mp].iloc[0]
                for col in columnas_a_copiar:
                    df_filtrado.loc[df_filtrado["Materia Prima"] == mp, col] = fila_guardada[col]

    # Columnas visibles
    columnas_default = obtener_familias_parametros()
    columnas_composicion = [col for sub in columnas_default.values() for col in sub]
    columnas_mostrar = ["Materia Prima", "Precio €/kg", "%"] + [
        col for col in df.columns if col in columnas_composicion
    ]

    df_filtrado = df_filtrado.reset_index(drop=True)

    df_editado = st.data_editor(
        df_filtrado[columnas_mostrar],
        use_container_width=True,
        key="formula_editor",
        hide_index=True
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    # Botón para calcular fórmula (guardar estado actual)
    if st.button("⚙️ Calcular fórmula"):
        prev = st.session_state.formula_editada
        if prev.empty:
            st.session_state.formula_editada = df_editado.copy()
        else:
            columnas_actualizables = [col for col in df_editado.columns if col not in ["Materia Prima"]]
            df_editado_indexed = df_editado.set_index("Materia Prima")
            prev_indexed = prev.set_index("Materia Prima")
            prev_indexed.update(df_editado_indexed[columnas_actualizables])
            df_fusionado = pd.concat([
                prev_indexed,
                df_editado_indexed[~df_editado_indexed.index.isin(prev_indexed.index)]
            ])
            st.session_state.formula_editada = df_fusionado.reset_index()

        st.session_state.editando_formula = False
        st.success("✅ Fórmula calculada")

    else:
        st.session_state.editando_formula = True

    return df_editado, total_pct

