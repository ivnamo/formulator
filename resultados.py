import streamlit as st
from formula_resultados import calcular_resultado_formula

def mostrar_resultados(df_editado, columnas_composicion, mostrar_todo):
    st.subheader("📊 Resultados")

    precio, composicion = calcular_resultado_formula(df_editado, columnas_composicion)
    st.success(f"💰 Precio por kg de la fórmula: {precio:.2f} €")

    if mostrar_todo:
        composicion = composicion[composicion["Cantidad %"] > 0]
        composicion = composicion[composicion.index != ""]

    if not composicion.empty:
        composicion_formateada = composicion.reset_index()
        composicion_formateada.columns = ["Parámetro", "% p/p"]
        st.markdown(composicion_formateada.to_html(index=False), unsafe_allow_html=True)
    else:
        st.info("No hay parámetros con cantidad > 0% en la fórmula.")
