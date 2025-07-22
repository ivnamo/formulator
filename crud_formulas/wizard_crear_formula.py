
# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo contiene el flujo corregido del wizard para crear fórmulas.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.editor import mostrar_editor_formula
from utils.formula_resultados import calcular_resultado_formula
from utils.families import obtener_familias_parametros
from utils.guardar_formula import guardar_formula
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def wizard_crear_formula():
    st.title("🧪 Crear fórmula (flujo controlado)")

    # Estado inicial
    if "wizard_v2" not in st.session_state:
        st.session_state.wizard_v2 = {
            "paso": 1,
            "seleccionadas": [],
            "ordenadas": [],
            "df_editado": None,
            "total_pct": 0.0,
            "precio_total": 0.0,
            "columnas_finales": []
        }

    w = st.session_state.wizard_v2

    # Paso actual
    paso = w["paso"]

    # Cargar materias primas
    response = supabase.table("materias_primas").select("*").execute()
    df_all = pd.DataFrame(response.data)
    df_all["%"] = 0.0
    df_all.sort_values("Materia Prima", inplace=True)

    if df_all.empty:
        st.error("No hay materias primas disponibles.")
        return

    st.markdown(f"### Paso {paso} de 5")

    # Paso 1: Selección
    if paso == 1:
        st.subheader("1️⃣ Selecciona las materias primas")
        seleccionadas = st.multiselect(
            "Selecciona materias primas",
            df_all["Materia Prima"].tolist(),
            default=w["seleccionadas"]
        )
        w["seleccionadas"] = seleccionadas
        if seleccionadas:
            w["ordenadas"] = seleccionadas.copy()

        col1, col2 = st.columns(2)
        with col2:
            if st.button("➡️ Siguiente"):
                if w["ordenadas"]:
                    w["paso"] = 2
                    st.rerun()

    # Paso 2: Orden
    elif paso == 2:
        st.subheader("2️⃣ Ordena las materias primas")
        df_orden = pd.DataFrame({"Materia Prima": w["ordenadas"]})
        gb = GridOptionsBuilder.from_dataframe(df_orden)
        gb.configure_column("Materia Prima", editable=False, rowDrag=True)
        gb.configure_grid_options(rowDragManaged=True)
        grid = AgGrid(df_orden, gridOptions=gb.build(),
                      update_mode=GridUpdateMode.MODEL_CHANGED,
                      allow_unsafe_jscode=True, theme="streamlit")
        nueva_orden = grid["data"]["Materia Prima"].tolist()
        w["ordenadas"] = nueva_orden

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior"):
                w["paso"] = 1
                st.rerun()
        with col2:
            if st.button("➡️ Siguiente"):
                w["paso"] = 3
                st.rerun()

    # Paso 3: Asignar %
    elif paso == 3:
        st.subheader("3️⃣ Asigna los porcentajes")
        df_editado, total_pct = mostrar_editor_formula(df_all.copy(), w["ordenadas"])
        w["df_editado"] = df_editado
        w["total_pct"] = total_pct

        st.write(f"Total: {total_pct:.2f}%")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior"):
                w["paso"] = 2
                st.rerun()
        with col2:
            if st.button("➡️ Siguiente"):
                if total_pct > 0:
                    w["paso"] = 4
                    st.rerun()
                else:
                    st.warning("Debes asignar al menos un porcentaje positivo.")

    # Paso 4: Revisión
    elif paso == 4:
        st.subheader("4️⃣ Revisión de resultados")
        familias = obtener_familias_parametros()
        columnas = [col for fam in familias.values() for col in fam]
        columnas_validas = [
            col for col in columnas
            if col in w["df_editado"].columns and (w["df_editado"][col] * w["df_editado"]["%"] / 100).sum() > 0
        ]
        precio, composicion = calcular_resultado_formula(w["df_editado"], columnas_validas)
        w["precio_total"] = precio
        w["columnas_finales"] = columnas_validas

        st.success(f"💰 Precio estimado: {precio:.2f} €/kg")
        if not composicion.empty:
            comp_df = composicion.reset_index()
            comp_df.columns = ["Parámetro", "% p/p"]
            st.dataframe(comp_df, use_container_width=True)
        else:
            st.info("No hay parámetros técnicos relevantes.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior"):
                w["paso"] = 3
                st.rerun()
        with col2:
            if st.button("➡️ Siguiente"):
                w["paso"] = 5
                st.rerun()

    # Paso 5: Guardar
    elif paso == 5:
        st.subheader("5️⃣ Guardar fórmula")
        nombre = st.text_input("Nombre de la fórmula")
        if st.button("💾 Guardar"):
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

        if st.button("⬅️ Anterior"):
            w["paso"] = 4
            st.rerun()
        if st.button("🔄 Reiniciar"):
            st.session_state.pop("wizard_v2")
            st.rerun()
