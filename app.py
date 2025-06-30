import streamlit as st
import pandas as pd

from families import obtener_familias_parametros
from formula_resultados import calcular_resultado_formula

st.set_page_config(layout="wide")
st.title("Calculadora de Fórmulas - Composición + Coste")

# Carga de datos
uploaded = st.file_uploader("Sube el archivo de materias primas (.xlsx)", type=["xlsx"])
if uploaded:
    df = pd.read_excel(uploaded)
else:
    df = pd.read_excel("materias_primas.xlsx")

# Aseguramos columna de porcentaje
if "%" not in df.columns:
    df["%"] = 0.0

# Selector de materias primas
seleccionadas = st.multiselect(
    "Busca y selecciona las materias primas",
    df["Materia Prima"].dropna().tolist()
)

# Filtramos base
df_base = df[df["Materia Prima"].isin(seleccionadas)].copy()

# Session state para fórmula editable
if "formula_df" not in st.session_state or not seleccionadas:
    st.session_state.formula_df = df_base

# Botón para añadir fila manual
if st.button("➕ Añadir fila manual"):
    # Creamos una fila vacía con columnas correctas
    nuevas = pd.DataFrame([{col: (0.0 if col != "Materia Prima" else "") 
                             for col in st.session_state.formula_df.columns}])
    st.session_state.formula_df = pd.concat(
        [st.session_state.formula_df, nuevas], ignore_index=True
    )

# Mostrar editor (sin añadir filas dinámicamente)
if not st.session_state.formula_df.empty:
    st.subheader("🧪 Fórmula editable")
    df_edit = st.data_editor(
        st.session_state.formula_df,
        use_container_width=True,
        key="editor"
    )
    # Guardamos cambios
    st.session_state.formula_df = df_edit

    # Cálculo de total %
    total_pct = df_edit["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    # Selección de familias
    familias = obtener_familias_parametros()
    mostrar_no_ceros = st.checkbox("Mostrar solo parámetros con cantidad > 0%", value=True)
    familias_sel = st.multiselect(
        "Selecciona las familias de parámetros a mostrar",
        list(familias.keys()),
        default=list(familias.keys())
    )

    # Columnas de composición
    columnas_comp = []
    for fam in familias_sel:
        columnas_comp.extend(familias[fam])

    # Validación de porcentaje
    if abs(total_pct - 100) > 0.01:
        st.warning("La suma de los porcentajes debe ser 100%")
    else:
        st.subheader("📊 Resultados")
        precio, comp = calcular_resultado_formula(df_edit, columnas_comp)
        st.success(f"💰 Precio por kg de la fórmula: {precio:.2f} €")

        # Filtrar valores si se desea
        if mostrar_no_ceros:
            comp = comp[comp["Cantidad %"] > 0]

        if comp.empty:
            st.info("No hay parámetros > 0%")
        else:
            st.markdown("#### 📜 Composición técnica (kg/100kg)")
            comp_df = (
                comp
                .rename_axis("Parámetro")
                .reset_index()
                .rename(columns={"Cantidad %": "% p/p"})
            )

            # Generar HTML estilizado y centrado con zebra striping
            html = comp_df.to_html(index=False, classes="styled-table", border=0)
            css = """
            <style>
            .styled-table {
                margin-left: auto;
                margin-right: auto;
                border-collapse: collapse;
                width: 50%;
                font-size: 0.95em;
            }
            .styled-table th, .styled-table td {
                border: 1px solid #555;
                padding: 6px 12px;
                text-align: center;
            }
            .styled-table tr:nth-child(even) {
                background-color: #2e2e2e;
            }
            .styled-table tr:nth-child(odd) {
                background-color: #1e1e1e;
            }
            .styled-table th {
                background-color: #009879;
                color: #ffffff;
            }
            </style>
            """
            st.markdown(css + html, unsafe_allow_html=True)
else:
    st.info("Selecciona materias primas para comenzar.")
