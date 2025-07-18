from utils.supabase_client import supabase
from utils.editor import mostrar_editor_formula
from utils.resultados import mostrar_resultados
from utils.families import obtener_familias_parametros
from utils.formula_resultados import calcular_resultado_formula
from utils.guardar_formula import guardar_formula
from streamlit_javascript import st_javascript  # lo mantenemos por ahora

import streamlit as st
import pandas as pd

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
        options=sorted(df["Materia Prima"].dropna().tolist()),
        help="Puedes escribir para buscar por nombre",
        key="mp_crear",
    )

    if not seleccionadas:
        st.info("Selecciona materias primas desde el buscador para comenzar.")
        return

    st.subheader("🧪 Fórmula editable")
    df_editado, total_pct = mostrar_editor_formula(df, seleccionadas)

    filtrar_ceros = st.checkbox("Mostrar solo parámetros con cantidad > 0%", value=True)

    familias = obtener_familias_parametros()
    seleccionadas_familias = st.multiselect(
        "Selecciona familias",
        list(familias),
        default=list(familias),
        key="familias_crear",
    )
    columnas = [col for fam in seleccionadas_familias for col in familias[fam]]

    if filtrar_ceros:
        columnas_filtradas = [
            col
            for col in columnas
            if col in df_editado.columns and (df_editado[col] * df_editado["%"] / 100).sum() > 0
        ]
    else:
        columnas_filtradas = columnas

    if abs(total_pct - 100) > 0.01:
        st.warning("⚠️ La suma de los porcentajes debe ser 100% para calcular.")
        forzar = st.checkbox(
            "🧪 Calcular de todos modos (forzar cálculo)",
            help="Activa esta opción si deseas calcular aunque la fórmula no sume exactamente 100%.",
            key="forzar_crear",
        )
        if forzar:
            st.info("Cálculo realizado con fórmula incompleta. Revisa los resultados con precaución.")
            mostrar_resultados(df_editado, columnas_filtradas)
    else:
        mostrar_resultados(df_editado, columnas_filtradas)

        st.markdown("---")
        st.subheader("📂 Guardar fórmula")

        host_url = st_javascript("window.location.origin") 

        nombre_formula = st.text_input("Nombre de la fórmula", placeholder="Ej. Bioestimulante Algas v1", key="nombre_crear")
        if st.button("Guardar fórmula"):
            if not nombre_formula.strip():
                st.warning("Debes ingresar un nombre para guardar la fórmula.")
            else:
                # 🔁 Reconstruir df con columnas completas
                df_final = df[df["Materia Prima"].isin(df_editado["Materia Prima"])].copy()
                df_final["%"] = df_editado["%"].values

                # ✅ Reordenar columnas
                columnas_base = ["Materia Prima", "%", "Precio €/kg"]
                columnas_tecnicas = [
                    col for col in df_final.columns
                    if col not in columnas_base and col != "id"
                ]
                columnas_ordenadas = columnas_base + columnas_tecnicas
                df_final = df_final[columnas_ordenadas]

                precio, _ = calcular_resultado_formula(df_final, columnas_filtradas)
                formula_id = guardar_formula(df_final, nombre_formula.strip(), precio)

                st.success("✅ Fórmula guardada correctamente.")

