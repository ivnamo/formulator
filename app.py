import streamlit as st
from data_loader import cargar_datos
from editor import mostrar_editor_formula
from resultados import mostrar_resultados
from families import obtener_familias_parametros
import pandas as pd

def gestionar_materias_primas(df):
    st.subheader("🗞 CRUD de Materias Primas")

    if "materias_df" not in st.session_state:
        st.session_state["materias_df"] = df.copy()

    edited_df = st.data_editor(
        st.session_state["materias_df"],
        use_container_width=True,
        num_rows="dynamic",
        key="editor_crud"
    )

    if st.button("📎 Guardar cambios"):
        st.session_state["materias_df"] = edited_df
        edited_df.to_excel("materias_primas.xlsx", index=False)
        st.success("Cambios guardados correctamente.")

def main():
    st.set_page_config(layout="wide")
    st.title("Calculadora de Fórmulas - Composición + Coste")

    menu = st.sidebar.radio("Navegación", ["Formulación", "CRUD Materias Primas"])

    archivo = st.file_uploader("Sube el archivo de materias primas (.xlsx)", type=["xlsx"])
    df = cargar_datos(archivo)

    if menu == "CRUD Materias Primas":
        gestionar_materias_primas(df)
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
