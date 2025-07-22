# ------------------------------------------------------------------------------
# FORMULATOR – Flujo tipo "wizard" para crear fórmulas paso a paso
# Uso exclusivo de Iván Navarro – © 2025
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.families import obtener_familias_parametros
from utils.formula_resultados import calcular_resultado_formula
from utils.editor import mostrar_editor_formula
from utils.guardar_formula import guardar_formula
from utils.generar_qr import generar_qr
from utils.exportar_formula import exportar_formula_excel
from streamlit_javascript import st_javascript


def wizard_crear_formula():
    st.title("🧪 Crear nueva fórmula paso a paso")

    # Inicializar estado
    if "paso_formula" not in st.session_state:
        st.session_state.paso_formula = 1
        st.session_state.datos_formula = {}

    paso = st.session_state.paso_formula
    datos = st.session_state.datos_formula

    # Cargar materias primas
    response = supabase.table("materias_primas").select("*").execute()
    df_all = pd.DataFrame(response.data)
    df_all["%"] = 0.0

    if df_all.empty:
        st.error("No hay materias primas disponibles.")
        return

    st.markdown(f"### Paso {paso} de 5")

    if paso == 1:
        st.subheader("1️⃣ Selección de materias primas")
        seleccionadas = st.multiselect(
            "Selecciona materias primas",
            df_all["Materia Prima"].dropna().tolist(),
            key="wizard_sel_mp"
        )
        if seleccionadas:
            datos["seleccionadas"] = seleccionadas
            if st.button("➡️ Siguiente"):
                st.session_state.paso_formula = 2
        else:
            st.info("Selecciona al menos una materia prima para continuar.")

    elif paso == 2:
        st.subheader("2️⃣ Ordenar materias primas")
        if "seleccionadas" not in datos:
            st.warning("⚠️ No hay materias primas seleccionadas.")
            return

        seleccionadas = datos["seleccionadas"]
        ordenadas = st.data_editor(pd.DataFrame({"Materia Prima": seleccionadas}), num_rows="dynamic")
        orden_final = ordenadas["Materia Prima"].dropna().tolist()
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

    elif paso == 5:
        st.subheader("5️⃣ Guardar y exportar")
        df_final = datos.get("df_editado")
        precio = datos.get("precio_total", 0)
        columnas = datos.get("columnas_finales", [])

        nombre = st.text_input("Nombre de la fórmula", key="wizard_nombre_formula")

        if st.button("💾 Guardar fórmula"):
            if not nombre.strip():
                st.warning("Debes ingresar un nombre.")
            else:
                columnas_base = ["Materia Prima", "%", "Precio €/kg"]
                columnas_tecnicas = [col for col in df_final.columns if col not in columnas_base and col != "id"]
                columnas_ordenadas = columnas_base + columnas_tecnicas
                df_final = df_final[columnas_ordenadas]

                formula_id = guardar_formula(df_final, nombre.strip(), precio)
                url = st_javascript("window.location.origin")
                qr = generar_qr(f"{url}/?formula_id={formula_id}")

                st.success("✅ Fórmula guardada correctamente.")
                st.image(qr, caption="Código QR", use_container_width=False)
                st.code(f"{url}/?formula_id={formula_id}")

                st.subheader("⬇️ Exportar fórmula")
                excel = exportar_formula_excel(df_final, nombre.strip())
                st.download_button(
                    label="Descargar Excel",
                    data=excel,
                    file_name=f"{nombre.strip()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        st.divider()
        if st.button("🔄 Reiniciar flujo"):
            st.session_state.paso_formula = 1
            st.session_state.datos_formula = {}
