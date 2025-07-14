# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.editor import mostrar_editor_formula
from utils.resultados import mostrar_resultados
from utils.families import obtener_familias_parametros
from utils.formula_resultados import calcular_resultado_formula
from utils.guardar_formula import guardar_formula
from utils.generar_qr import generar_qr
from utils.exportar_formula import exportar_formula_excel
from utils.optimizador_simplex import optimizar_simplex
from streamlit_javascript import st_javascript

def flujo_crear_formula():
    """Interfaz para crear y guardar nuevas fórmulas."""
    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)
    df["%"] = 0.0

    if "Materia Prima" not in df.columns:
        st.error("La columna 'Materia Prima' no está disponible en los datos.")
        return

    seleccionadas = st.multiselect(
        "Busca y selecciona las materias primas",
        options=df["Materia Prima"].dropna().tolist(),
        help="Puedes escribir para buscar por nombre",
        key="mp_crear",
    )

    if not seleccionadas:
        st.info("Selecciona materias primas desde el buscador para comenzar.")
        return

    st.subheader("🧪 Fórmula editable")
    df_editado, total_pct = mostrar_editor_formula(df, seleccionadas)

    familias = obtener_familias_parametros()
    seleccionadas_familias = st.multiselect(
        "Selecciona familias",
        list(familias),
        default=list(familias),
        key="familias_crear",
    )
    columnas = [col for fam in seleccionadas_familias for col in familias[fam]]

    columnas_filtradas = [col for col in columnas if col in df_editado.columns]

    # ⚡️ OPTIMIZADOR SIMPLEX
    st.markdown("### ⚙️ Optimización Simplex")

    with st.expander("🧮 Optimizar fórmula automáticamente (Simplex)"):
        if columnas_filtradas:
            col1, col2 = st.columns(2)
            param = col1.selectbox("Parámetro técnico a cumplir", columnas_filtradas)
            minimo = col2.number_input("Valor mínimo requerido (%)", min_value=0.0, value=1.0, step=0.1)

            if st.button("🔧 Ejecutar optimización Simplex"):
                try:
                    restric = {param: minimo}
                    df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()
                    df_opt, costo = optimizar_simplex(df_filtrado, columnas_filtradas, restricciones_min=restric)
                    st.success(f"Fórmula optimizada. Coste total: {costo:.2f} €/kg")
                    st.dataframe(df_opt[["Materia Prima", "%", "Precio €/kg"] + columnas_filtradas])
                    df_editado = df_opt.copy()
                    total_pct = df_editado["%"].sum()
                except Exception as e:
                    st.error(f"❌ Error durante la optimización: {e}")
        else:
            st.info("Selecciona al menos una familia con parámetros técnicos para optimizar.")

    st.subheader("📊 Resultados")
    precio, composicion = calcular_resultado_formula(df_editado, columnas_filtradas)
    st.success(f"💰 Precio por kg de la fórmula: {precio:.2f} €")
    mostrar_resultados(df_editado, columnas_filtradas)

    st.markdown("---")
    st.subheader("📂 Guardar fórmula")

    host_url = st_javascript("window.location.origin") 

    nombre_formula = st.text_input("Nombre de la fórmula", placeholder="Ej. Bioestimulante Algas v1", key="nombre_crear")
    if st.button("Guardar fórmula"):
        if not nombre_formula.strip():
            st.warning("Debes ingresar un nombre para guardar la fórmula.")
        else:
            columnas_base = ["Materia Prima", "%", "Precio €/kg"]
            columnas_tecnicas = [
                col for col in df_editado.columns
                if col not in columnas_base and col != "id"
            ]
            columnas_ordenadas = columnas_base + columnas_tecnicas
            df_editado = df_editado[columnas_ordenadas]

            precio, _ = calcular_resultado_formula(df_editado, columnas_filtradas)
            formula_id = guardar_formula(df_editado, nombre_formula.strip(), precio)
            url_formula = f"{host_url}/?formula_id={formula_id}"

            qr_img = generar_qr(url_formula)

            st.success("✅ Fórmula guardada correctamente.")
            st.image(qr_img, caption="Código QR para esta fórmula", use_container_width=False)
            st.code(url_formula, language="markdown")

            st.markdown("---")
            st.subheader("📤 Exportar fórmula a Excel")
            excel_bytes = exportar_formula_excel(df_editado, nombre_formula.strip())
            st.download_button(
                label="⬇️ Descargar Excel",
                data=excel_bytes,
                file_name=f"{nombre_formula.strip()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

