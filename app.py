import streamlit as st
import pandas as pd
import numpy as np
from supabase_client import supabase
from editor import mostrar_editor_formula
from resultados import mostrar_resultados
from families import obtener_familias_parametros
from create_materia_prima import crear_materia_prima
from update_materia_prima import actualizar_materia_prima
from delete_materia_prima import eliminar_materia_prima

def main():
    st.set_page_config(layout="wide")
    st.title("Calculadora de Fórmulas - Composición + Coste")

    with st.sidebar:
        st.image("logo.png", width=180)  # Logo personalizado
        st.markdown("### Navegación")
        menu = st.radio("", ["FORMULATE", "CREATE", "UPDATE", "DELETE"])

        st.markdown("---")
        st.markdown("""
        **Desarrollado por:** Iván Navarro  
        **Versión:** 1.0.0  
        **Fecha:** 01/07/2005
        """)

    if menu == "CREATE":
        crear_materia_prima()
        return
    elif menu == "UPDATE":
        actualizar_materia_prima()
        return
    elif menu == "DELETE":
        eliminar_materia_prima()
        return

    # Formulación
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
            st.warning("La suma de los porcentajes debe ser 100% para calcular.")
        else:
            mostrar_resultados(df_editado, columnas_filtradas)

if __name__ == "__main__":
    main()

