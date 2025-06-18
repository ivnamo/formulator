
import streamlit as st
import pandas as pd

st.title("🧪 Formulador de Fertilizantes")

@st.cache_data
def cargar_materias():
    return pd.read_excel("materias_primas.xlsx")

materias = cargar_materias()
st.dataframe(materias)

seleccion = st.multiselect("Selecciona materias primas", materias["Nombre"])
if seleccion:
    df_sel = materias[materias["Nombre"].isin(seleccion)].copy()
    cantidades = []
    for i, row in df_sel.iterrows():
        cantidad = st.number_input(f"{row['Nombre']}:", min_value=0.0, step=0.1, key=row['Nombre'])
        cantidades.append(cantidad)
    df_sel["Cantidad"] = cantidades
    # ... aquí continuarían los cálculos y exportación ...
