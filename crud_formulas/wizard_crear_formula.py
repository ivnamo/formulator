# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.families import obtener_familias_parametros
from utils.formula_resultados import calcular_resultado_formula
from utils.editor import mostrar_editor_formula
from utils.guardar_formula import guardar_formula
from utils.exportar_formula import exportar_formula_excel
from streamlit_javascript import st_javascript
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def wizard_crear_formula():
    st.title("🧪 Crear nueva fórmula paso a paso")

    if "paso_formula" not in st.session_state:
        st.session_state.paso_formula = 1
        st.session_state.datos_formula = {}

    paso = st.session_state.paso_formula
    datos = st.session_state.datos_formula

    # Cargar materias primas ordenadas alfabéticamente
    response = supabase.table("materias_primas").select("*").execute()
    df_all = pd.DataFrame(response.data)
    df_all["%"] = 0.0
    df_all.sort_values("Materia Prima", inplace=True)

    if df_all.empty:
        st.error("No hay materias primas disponibles.")
        return

    st.markdown(f"### Paso {paso} de 5")

    # Paso 1 – Selección de materias primas con persistencia
    if paso == 1:
        st.subheader("1️⃣ Selección de materias primas")

        seleccionadas = st.multiselect(
            "Selecciona materias primas",
            df_all["Materia Prima"].dropna().tolist(),
            default=datos.get("seleccionadas", []),
            key="wizard_sel_mp"
        )
        datos["seleccionadas"] = seleccionadas

        if seleccionadas:
            if st.button("➡️ Siguiente"):
                st.session_state.paso_formula = 2
        else:
            st.info("Selecciona al menos una materia prima para continuar.")

    # Paso 2 – Ordenar con AgGrid
    elif paso == 2:
        st.subheader("2️⃣ Ordenar materias primas")

        if "seleccionadas" not in datos or not datos["seleccionadas"]:
            st.warning("⚠️ No hay materias primas seleccionadas.")
            return

        seleccionadas = datos["seleccionadas"]
        df_orden = pd.DataFrame({"Materia Prima": seleccionadas})

        gb = GridOptionsBuilder.from_dataframe(df_orden)
        gb.configure_column("Materia Prima", editable=False, rowDrag=True)
        gb.configure_grid_options(rowDragManaged=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            df_orden,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            height=300,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
            theme="streamlit"
        )

        orden_final = grid_response["data"]["Materia Prima"].tolist()
        datos["ordenadas"] = orden_final

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior"):
                st.session_state.paso_formula = 1
        with col2:
            if orden_final:
                if st.button("➡️ Siguiente"):
                    st.session_state.paso_formula = 3
            else:
                st.warning("Debes mantener al menos una materia prima ordenada.")

    # Paso 3 – Asignar %
    elif paso == 3:
        st.subheader("3️⃣ Asignar porcentajes")
        ordenadas = datos.get("ordenadas", [])
        df_editado, total_pct = mostrar_editor_formula(df_all, ordenadas)
        datos["df_editado"] = df_editado
        datos["total_pct"] = total_pct

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior"):
                st.session_state.paso_formula = 2
        with col2:
            if total_pct > 0:
                if st.button("➡️ Siguiente"):
                    st.session_state.paso_formula = 4
            else:
                st.warning("Asigna porcentajes antes de continuar.")

    # Paso 4 – Revisión
    elif paso == 4:
        st.subheader("4️⃣ Revisión de resultados")
        df_editado = datos.get("df_editado")
        total_pct = datos.get("total_pct", 0)

        familias = obtener_familias_parametros()
        columnas = [col for fam in familias.values() for col in fam]
        columnas_validas = [
            col for col in columnas
            if col in df_editado.columns and (df_editado[col] * df_editado["%"] / 100).sum() > 0
        ]

        precio, composicion = calcular_resultado_formula(df_editado, columnas_validas)
        datos["precio_total"] = precio
        datos["columnas_finales"] = columnas_validas

        st.success(f"💰 Precio estimado: {precio:.2f} €/kg")
        if not composicion.empty:
            comp_df = composicion.reset_index()
            comp_df.columns = ["Parámetro", "% p/p"]
            st.markdown(comp_df.to_html(index=False), unsafe_allow_html=True)
        else:
            st.info("No hay parámetros técnicos significativos.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior"):
                st.session_state.paso_formula = 3
        with col2:
            if st.button("➡️ Siguiente"):
                st.session_state.paso_formula = 5

    # Paso 5 – Guardar fórmula (sin exportar ni QR)
    elif paso == 5:
        st.subheader("5️⃣ Guardar fórmula")
        df_final = datos.get("df_editado")
        precio = datos.get("precio_total", 0)

        nombre = st.text_input("Nombre de la fórmula", key="wizard_nombre_formula")

        if st.button("💾 Guardar fórmula"):
            if not nombre.strip():
                st.warning("Debes ingresar un nombre.")
            else:
                columnas_base = ["Materia Prima", "%", "Precio €/kg"]
                columnas_tecnicas = [col for col in df_final.columns if col not in columnas_base and col != "id"]
                columnas_ordenadas = columnas_base + columnas_tecnicas
                df_final = df_final[columnas_ordenadas]

                guardar_formula(df_final, nombre.strip(), precio)
                st.success("✅ Fórmula guardada correctamente.")

        st.divider()
        if st.button("🔄 Reiniciar flujo"):
            st.session_state.paso_formula = 1
            st.session_state.datos_formula = {}

