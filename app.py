# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
from utils.supabase_client import supabase
from utils.editor import mostrar_editor_formula
from utils.resultados import mostrar_resultados
from utils.families import obtener_familias_parametros
from crud_mp.create_materia_prima import crear_materia_prima
from crud_mp.update_materia_prima import actualizar_materia_prima
from crud_mp.delete_materia_prima import eliminar_materia_prima
from utils.guardar_formula import guardar_formula
from utils.generar_qr import generar_qr
from utils.formula_resultados import calcular_resultado_formula
from utils.cargar_formula import cargar_formula_por_id

def main():
    st.set_page_config(layout="wide")

    # 📥 Cargar fórmula desde la URL si se ha accedido con ?formula_id=...
    params = st.query_params
    if "formula_id" in params:
        cargar_formula_por_id(params["formula_id"])
        return

    st.title("Calculadora de Fórmulas - Composición + Coste")

    with st.sidebar:
        st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; padding: 10px 0;'>
            <img src='https://raw.githubusercontent.com/ivnamo/formulator/main/logo.png' style='width: 200px; height: auto; object-fit: contain;'>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Navegación")
        menu = st.radio("Navegación", ["Formular", "Materias Primas"], label_visibility="collapsed")

        st.markdown("---")
        st.markdown("""
        **Desarrollado por:** Iván Navarro  
        **Versión:** 1.0.0  
        **Fecha:** 01/07/2005
        """)

    if menu == "Materias Primas":
        subtarea = st.selectbox("Acción sobre materias primas", ["Crear", "Actualizar", "Eliminar"])

        if subtarea == "Crear":
            crear_materia_prima()
        elif subtarea == "Actualizar":
            actualizar_materia_prima()
        elif subtarea == "Eliminar":
            eliminar_materia_prima()
        return

    # FORMULATE
    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)
    df["%"] = 0.0

    if "Materia Prima" not in df.columns:
        st.error("La columna 'Materia Prima' no está disponible en los datos.")
        return

    seleccionadas = st.multiselect(
        "Busca y selecciona las materias primas",
        options=df["Materia Prima"].dropna().tolist(),
        help="Puedes escribir para buscar por nombre"
    )

    if not seleccionadas:
        st.info("Selecciona materias primas desde el buscador para comenzar.")
        return

    st.subheader("🧪 Fórmula editable")
    df_editado, total_pct = mostrar_editor_formula(df, seleccionadas)

    if df_editado is not None:
        filtrar_ceros = st.checkbox("Mostrar solo parámetros con cantidad > 0%", value=True)

        familias = obtener_familias_parametros()
        seleccionadas_familias = st.multiselect("Selecciona familias", list(familias), default=list(familias))
        columnas = [col for fam in seleccionadas_familias for col in familias[fam]]

        if filtrar_ceros:
            columnas_filtradas = [
                col for col in columnas
                if col in df_editado.columns and (df_editado[col] * df_editado["%"] / 100).sum() > 0
            ]
        else:
            columnas_filtradas = columnas

        if abs(total_pct - 100) > 0.01:
            st.warning("⚠️ La suma de los porcentajes debe ser 100% para calcular.")
            forzar = st.checkbox(
                "🧪 Calcular de todos modos (forzar cálculo)",
                help="Activa esta opción si deseas calcular aunque la fórmula no sume exactamente 100%."
            )
            if forzar:
                st.info("Cálculo realizado con fórmula incompleta. Revisa los resultados con precaución.")
                mostrar_resultados(df_editado, columnas_filtradas)
        else:
            mostrar_resultados(df_editado, columnas_filtradas)

            # Guardar y generar QR
            st.markdown("---")
            st.subheader("📂 Guardar fórmula")

            nombre_formula = st.text_input("Nombre de la fórmula", placeholder="Ej. Bioestimulante Algas v1")
            if st.button("Guardar fórmula"):
                if not nombre_formula.strip():
                    st.warning("Debes ingresar un nombre para guardar la fórmula.")
                else:
                    precio, _ = calcular_resultado_formula(df_editado, columnas_filtradas)
                    formula_id = guardar_formula(df_editado, nombre_formula.strip(), precio)
                    url_formula = f"https://formulator-pruebas2.streamlit.app/?formula_id={formula_id}"
                    qr_img = generar_qr(url_formula)

                    st.success("✅ Fórmula guardada correctamente.")
                    st.image(qr_img, caption="Código QR para esta fórmula", use_container_width=True)
                    st.code(url_formula, language="markdown")

if __name__ == "__main__":
    main()

