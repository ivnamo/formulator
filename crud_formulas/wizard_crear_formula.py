
# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo contiene el flujo corregido del wizard para crear fórmulas.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.families import obtener_familias_parametros
from utils.formula_resultados import calcular_resultado_formula
from utils.editor import mostrar_editor_formula
from utils.guardar_formula import guardar_formula
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def wizard_crear_formula():
    st.title("🧪 Crear nueva fórmula paso a paso")

    # Inicialización de estado
    if "wizard" not in st.session_state:
        st.session_state.wizard = {
            "paso": 1,
            "seleccionadas": [],
            "ordenadas": [],
            "df_editado": pd.DataFrame(),
            "total_pct": 0.0,
            "precio_total": 0.0,
            "columnas_finales": []
        }

    w = st.session_state.wizard

    # Cargar materias primas
    response = supabase.table("materias_primas").select("*").execute()
    df_all = pd.DataFrame(response.data)
    df_all["%"] = 0.0
    df_all.sort_values("Materia Prima", inplace=True)

    if df_all.empty:
        st.error("No hay materias primas disponibles.")
        return

    st.markdown(f"### Paso {w['paso']} de 5")

    # Paso 1 – Selección
    if w["paso"] == 1:
        st.subheader("1️⃣ Selección de materias primas")
        nuevas = st.multiselect(
            "Selecciona materias primas",
            options=df_all["Materia Prima"].tolist(),
            default=w["seleccionadas"]
        )
        if nuevas != w["seleccionadas"]:
            w["seleccionadas"] = nuevas
            w["ordenadas"] = nuevas  # sincroniza orden inicial
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➡️ Siguiente", key="s1"):
                if w["seleccionadas"]:
                    w["paso"] = 2
                else:
                    st.warning("Selecciona al menos una materia prima.")
        with col2:
            if st.button("🔄 Reiniciar", key="r1"):
                st.session_state.pop("wizard")
                st.rerun()

    # Paso 2 – Ordenar
    elif w["paso"] == 2:
        st.subheader("2️⃣ Ordenar materias primas")
        df_orden = pd.DataFrame({"Materia Prima": w["ordenadas"]})
        gb = GridOptionsBuilder.from_dataframe(df_orden)
        gb.configure_column("Materia Prima", editable=False, rowDrag=True)
        gb.configure_grid_options(rowDragManaged=True)
        grid = AgGrid(df_orden, gridOptions=gb.build(),
                      update_mode=GridUpdateMode.MODEL_CHANGED,
                      allow_unsafe_jscode=True, theme="streamlit")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior", key="b2a"):
                w["paso"] = 1
        with col2:
            if st.button("➡️ Siguiente", key="b2s"):
                ordenadas = grid["data"]["Materia Prima"].dropna().tolist()
                if ordenadas:
                    w["ordenadas"] = ordenadas
                    w["paso"] = 3
                else:
                    st.warning("El orden no puede estar vacío.")

    # Paso 3 – Editar %
    elif w["paso"] == 3:
        st.subheader("3️⃣ Asignar porcentajes")
        df_editado, total_pct = mostrar_editor_formula(df_all.copy(), w["ordenadas"])
        w["df_editado"] = df_editado
        w["total_pct"] = total_pct
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior", key="b3a"):
                w["paso"] = 2
        with col2:
            if st.button("➡️ Siguiente", key="b3s"):
                if total_pct > 0:
                    w["paso"] = 4
                else:
                    st.warning("Debe asignar porcentajes mayores a 0.")

    # Paso 4 – Revisión
    elif w["paso"] == 4:
        st.subheader("4️⃣ Revisión de resultados")
        familias = obtener_familias_parametros()
        columnas = [col for fam in familias.values() for col in fam]
        columnas_validas = [
            col for col in columnas
            if col in w["df_editado"].columns and (w["df_editado"][col] * w["df_editado"]["%"] / 100).sum() > 0
        ]
        precio, compo = calcular_resultado_formula(w["df_editado"], columnas_validas)
        w["precio_total"] = precio
        w["columnas_finales"] = columnas_validas

        st.success(f"💰 Precio estimado: {precio:.2f} €/kg")
        if not compo.empty:
            comp_df = compo.reset_index()
            comp_df.columns = ["Parámetro", "% p/p"]
            st.markdown(comp_df.to_html(index=False), unsafe_allow_html=True)
        else:
            st.info("No hay parámetros técnicos relevantes.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior", key="b4a"):
                w["paso"] = 3
        with col2:
            if st.button("➡️ Siguiente", key="b4s"):
                w["paso"] = 5

    # Paso 5 – Guardar
    elif w["paso"] == 5:
        st.subheader("5️⃣ Guardar fórmula")
        nombre = st.text_input("Nombre de la fórmula", key="nombre_formula_wizard")
        if st.button("💾 Guardar fórmula", key="guardar_final"):
            if not nombre.strip():
                st.warning("Debes introducir un nombre.")
            else:
                df_final = w["df_editado"].copy()
                columnas_base = ["Materia Prima", "%", "Precio €/kg"]
                columnas_tecnicas = [col for col in df_final.columns if col not in columnas_base and col != "id"]
                columnas_ordenadas = columnas_base + columnas_tecnicas
                df_final = df_final[columnas_ordenadas]
                guardar_formula(df_final, nombre.strip(), w["precio_total"])
                st.success("✅ Fórmula guardada correctamente.")
        if st.button("⬅️ Anterior", key="b5a"):
            w["paso"] = 4
        if st.button("🔄 Reiniciar todo", key="r5"):
            st.session_state.pop("wizard")
            st.rerun()
