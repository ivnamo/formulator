import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.filtros_materias_primas import aplicar_filtros_materias_primas
from utils.data_loader import cargar_datos



def ver_materia_prima():
    st.subheader("🔎 Buscar materias primas")

    # Cargar desde Supabase

    df = cargar_datos()


    if df.empty:
        st.warning("No hay materias primas registradas.")
        return


    # Aplicar filtros definidos por el usuario
    df_filtrado = aplicar_filtros_materias_primas(df)

    if df_filtrado.empty:
        st.info("No hay resultados con los filtros aplicados.")
        return

    st.markdown(f"### 📋 Resultados: {len(df_filtrado)} materia(s) prima(s)")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
