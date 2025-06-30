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

    columnas_editables = ["Materia Prima", "Precio €/kg", "%"]
    df_editable = df_filtrado[columnas_editables].reset_index(drop=True)

    df_editado = st.data_editor(
        df_editable,
        use_container_width=True,
        num_rows="dynamic",
        key="formula_editor"
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    familias_disponibles = obtener_familias_parametros()

    # ✅ Checkbox para filtrar por parámetros > 0
    filtrar_no_ceros = st.checkbox("Mostrar solo parámetros con cantidad > 0%", value=True)

    # 🧲 Estado sincronizado de familias
    if "familias_seleccionadas" not in st.session_state:
        st.session_state.familias_seleccionadas = list(familias_disponibles.keys())

    if not filtrar_no_ceros:
        st.session_state.familias_seleccionadas = list(familias_disponibles.keys())

    familias_seleccionadas = st.multiselect(
        "Selecciona las familias de parámetros a mostrar",
        list(familias_disponibles.keys()),
        default=st.session_state.familias_seleccionadas,
        key="familias_seleccionadas"
    )

    columnas_composicion = []
    for fam in familias_seleccionadas:
        columnas_composicion.extend(familias_disponibles[fam])

    if abs(total_pct - 100) > 0.01:
        st.warning("La suma de los porcentajes debe ser 100% para calcular.")
    else:
        st.subheader("📊 Resultados")

        df_completo = pd.merge(
            df_editado,
            df,
            on="Materia Prima",
            how="left",
            suffixes=("", "_original")
        )

        df_completo = df_completo.drop(columns=[col for col in df_completo.columns if col.endswith("_original")])

        precio, composicion = calcular_resultado_formula(df_completo, columnas_composicion)
        st.success(f"💰 Precio por kg de la fórmula: {precio:.2f} €")

        if filtrar_no_ceros:
            composicion = composicion[composicion["Cantidad %"] > 0]

        if composicion.empty:
            st.info("No hay parámetros con cantidad > 0% en la fórmula.")
        else:
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
