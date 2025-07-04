# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------


import streamlit as st
from formula_resultados import calcular_resultado_formula

def mostrar_resultados(df_editado, columnas_composicion):
    st.subheader("📊 Resultados")

    precio, composicion = calcular_resultado_formula(df_editado, columnas_composicion)
    st.success(f"💰 Precio por kg de la fórmula: {precio:.2f} €")

    composicion = composicion[composicion.index != ""]

    if not composicion.empty:
        composicion_formateada = composicion.reset_index()
        composicion_formateada.columns = ["Parámetro", "% p/p"]
        st.markdown(composicion_formateada.to_html(index=False), unsafe_allow_html=True)
    else:
        st.info("No hay parámetros con cantidad > 0% en la fórmula.")
