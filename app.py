import streamlit as st
import pandas as pd

st.title("Calculadora de Fórmulas - Buscador Avanzado")

# Simulamos la carga del archivo Excel
df = pd.read_excel("materias_primas.xlsx")
df['%'] = 0.0

# 🔍 Multiselect con búsqueda
seleccionadas = st.multiselect(
    "Busca y selecciona las materias primas",
    options=df["Materia Prima"].tolist(),
    help="Puedes escribir para buscar por nombre"
)

# 📋 Filtramos las seleccionadas
df_filtrado = df[df["Materia Prima"].isin(seleccionadas)].copy()

if not df_filtrado.empty:
    st.markdown("### Materias primas seleccionadas")
    df_editado = st.data_editor(
        df_filtrado[["Materia Prima", "Precio €/kg", "%"]],
        use_container_width=True,
        num_rows="dynamic",
        key="formula_editor"
    )

    total_pct = df_editado["%"].sum()
    st.write(f"**Suma total del porcentaje:** {total_pct:.2f}%")

    if abs(total_pct - 100) > 0.01:
        st.warning("La suma debe ser 100% para calcular el precio.")
    else:
        df_editado["Subtotal"] = (df_editado["Precio €/kg"] * df_editado["%"]) / 100
        total_precio = df_editado["Subtotal"].sum()
        st.success(f"💰 Precio por kg de la fórmula: {total_precio:.2f} €")
else:
    st.info("Selecciona materias primas desde el buscador para comenzar.")
