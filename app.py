import streamlit as st
import pandas as pd

from families import obtener_familias_parametros
from formula_resultados import calcular_resultado_formula

st.set_page_config(layout="wide")
st.title("Calculadora de Fórmulas - Composición + Coste")

# 📥 Carga del archivo Excel
archivo = st.file_uploader("Sube el archivo de materias primas (.xlsx)", type=["xlsx"])
if archivo:
    df = pd.read_excel(archivo)
else:
    df = pd.read_excel("materias_primas.xlsx")

# Inicializamos columna %
df["%"] = 0.0

# 🔍 Buscador de materias primas
seleccionadas = st.multiselect(
    "Busca y selecciona las materias primas",
    options=df["Materia Prima"].dropna().tolist(),
    help="Puedes escribir para buscar por nombre"
)

# Filtrar materias primas seleccionadas
df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()

if not df_filtrado.empty:
    st.subheader("🧪 Fórmula editable")

    # Editor con columnas básicas para poder seleccionar y editar % y añadir filas
    columnas_basicas = ["Materia Prima", "Precio €/kg", "%"]
    df_editado = st.data_editor(
        df_filtrado[columnas_basicas],
        use_container_width=True,
        num_rows="dynamic",  # Permite añadir y borrar filas
        key="formula_editor"
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    # Selección de familias de parámetros
    familias_disponibles = obtener_familias_parametros()
    familias_seleccionadas = st.multiselect(
        "Selecciona las familias de parámetros a mostrar",
        list(familias_disponibles.keys()),
        default=["Macronutriente", "Fracción Orgánica"]
    )

    # Construcción de columnas técnicas a mostrar
    columnas_composicion = []
    for fam in familias_seleccionadas:
        columnas_composicion.extend(familias_disponibles[fam])

    # Cálculo solo si el total es 100%
    if abs(total_pct - 100) > 0.01:
        st.warning("La suma de los porcentajes debe ser 100% para calcular.")
    else:
        st.subheader("📊 Resultados")

        precio, composicion = calcular_resultado_formula(df_editado, columnas_composicion)
        st.success(f"💰 Precio por kg de la fórmula: {precio:.2f} €")

        # Checkbox para mostrar solo parámetros > 0
        filtrar_no_ceros = st.checkbox("Mostrar solo parámetros con cantidad > 0%", value=True)

        if filtrar_no_ceros:
            composicion = composicion[composicion["Cantidad %"] > 0]

        # Mostrar tabla centrada y con autosize de columnas
        with st.container():
            st.markdown("<div style='max-width: 700px; margin: auto;'>", unsafe_allow_html=True)

            st.dataframe(
                composicion,
                use_container_width=True,
                hide_index=False,
                column_config={
                    col: st.column_config.Column(width="auto") for col in composicion.columns
                }
            )

            st.markdown("</div>", unsafe_allow_html=True)



else:
    st.info("Selecciona materias primas desde el buscador para comenzar.")
