import streamlit as st
import pandas as pd

st.title("Calculadora de Precio de Fórmulas")

archivo = st.file_uploader("Sube tu archivo Excel con materias primas y precios", type=["xlsx"])

if archivo is None:
    archivo = 'materias_primas.xlsx'  # usar archivo local si no se sube ninguno


if archivo:
    df = pd.read_excel(archivo)
    st.write("Materias primas cargadas:", df)

    if 'Materia Prima' in df.columns and 'Precio €/kg' in df.columns:
        materias_primas = df['Materia Prima'].tolist()
        precios = df.set_index('Materia Prima')['Precio €/kg'].to_dict()

        st.subheader("Construcción de la fórmula")

        porcentaje_formula = {}
        total_porcentaje = 0

        for materia in materias_primas:
            porcentaje = st.number_input(f"% de {materia}", min_value=0.0, max_value=100.0, step=0.1)
            porcentaje_formula[materia] = porcentaje
            total_porcentaje += porcentaje

        st.write(f"Suma total del porcentaje: {total_porcentaje:.2f}%")

        if st.button("Calcular precio de la fórmula"):
            if abs(total_porcentaje - 100) > 0.01:
                st.error("La suma de los porcentajes debe ser 100%")
            else:
                precio_total = sum((porcentaje_formula[mat] / 100) * precios[mat] for mat in materias_primas)
                st.success(f"Precio por kg de la fórmula: {precio_total:.2f} €")
    else:
        st.error("El archivo debe tener las columnas 'Materia Prima' y 'Precio €/kg'")
