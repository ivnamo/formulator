import streamlit as st
import pandas as pd
from families import obtener_familias_parametros
from formula_resultados import calcular_resultado_formula

st.set_page_config(layout="wide")
st.title("Calculadora de Fórmulas - Composición + Coste")

# Carga de archivo
archivo = st.file_uploader("Sube el archivo de materias primas (.xlsx)", type=["xlsx"])
if archivo:
    df = pd.read_excel(archivo)
else:
    df = pd.read_excel("materias_primas.xlsx")

# Inicializamos columna de porcentaje si no está
if "%" not in df.columns:
    df["%"] = 0.0

# Buscador de materias primas
seleccionadas = st.multiselect(
    "Busca y selecciona las materias primas",
    options=df["Materia Prima"].dropna().tolist(),
    help="Puedes escribir para buscar por nombre"
)

# Filtrado
df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()

if not df_filtrado.empty:
    st.subheader("🧪 Fórmula editable")

    # Mostrar columnas de composición
    columnas_mostrar = ["Materia Prima", "Precio €/kg", "%"]
    columnas_composicion_default = obtener_familias_parametros()
    columnas_composicion = [col for sublist in columnas_composicion_default.values() for col in sublist]
    columnas_mostrar += [col for col in df.columns if col not in columnas_mostrar and col in columnas_composicion]

    df_editado = st.data_editor(
        df_filtrado[columnas_mostrar],
        use_container_width=True,
        num_rows="dynamic",
        key="formula_editor"
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    familias_disponibles = obtener_familias_parametros()

    mostrar_todo = st.checkbox("Mostrar solo parámetros con cantidad > 0%", value=True)

    if not mostrar_todo:
        familias_seleccionadas = st.multiselect(
            "Selecciona las familias de parámetros a mostrar",
            list(familias_disponibles.keys()),
            default=list(familias_disponibles.keys())
        )
    else:
        familias_seleccionadas = list(familias_disponibles.keys())

    columnas_composicion = []
    for fam in familias_seleccionadas:
        columnas_composicion.extend(familias_disponibles[fam])

    if abs(total_pct - 100) > 0.01:
        st.warning("La suma de los porcentajes debe ser 100% para calcular.")
    else:
        st.subheader("📊 Resultados")

        precio, composicion = calcular_resultado_formula(df_editado, columnas_composicion)
        st.success(f"💰 Precio por kg de la fórmula: {precio:.2f} €")

        if mostrar_todo:
            composicion = composicion[composicion["Cantidad %"] > 0]
            composicion = composicion[composicion.index != ""]

        if not composicion.empty:
            st.markdown("#### 📜 Composición técnica (kg/100kg)")

            # Formateamos tabla
            composicion_formateada = composicion.copy()
            composicion_formateada.index.name = None
            composicion_formateada.columns = ["% p/p"]
            composicion_formateada.index.name = "Parámetro"
            composicion_formateada["% p/p"] = composicion_formateada["% p/p"].map(lambda x: f"{x:.3f}")

            html_table = composicion_formateada.to_html(
                classes='compact-table zebra-table',
                border=0,
                justify='center'
            )

            style = """
            <style>
                .compact-table {
                    margin-left: auto;
                    margin-right: auto;
                    border-collapse: collapse;
                    font-size: 0.9rem;
                }
                .compact-table th, .compact-table td {
                    padding: 6px 16px;
                    text-align: center;
                }
                .zebra-table tbody tr:nth-child(odd) {
                    background-color: #2c2c2c;
                }
                .zebra-table tbody tr:nth-child(even) {
                    background-color: #1e1e1e;
                }
            </style>
            """

            st.markdown(style + html_table, unsafe_allow_html=True)

        else:
            st.info("No hay parámetros con cantidad > 0% en la fórmula.")

else:
    st.info("Selecciona materias primas desde el buscador para comenzar.")
