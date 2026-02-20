# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase

def listar_formulas_dataframe():
    """Devuelve un DataFrame con todas las fórmulas sin renderizar nada en pantalla."""
    try:
        response = supabase.table("formulas").select("id,nombre").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"❌ Error al cargar las fórmulas: {e}")
        return pd.DataFrame()


def listar_formulas(seleccionar: bool = True):
    """Muestra las fórmulas guardadas y opcionalmente permite seleccionar una."""
    st.subheader("📂 Fórmulas disponibles")
    try:
        response = supabase.table("formulas").select("id,nombre").execute()
        df = pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"❌ Error al cargar las fórmulas: {e}")
        return None

    if df.empty:
        st.info("No hay fórmulas guardadas.")
        return None

    if seleccionar:
        opciones = [""] + df["nombre"].tolist()
        seleccion = st.selectbox(
            "Selecciona una fórmula",
            opciones,
            index=0,
            key="seleccionar_formula",
        )
        if seleccion:
            formula_id = df[df["nombre"] == seleccion]["id"].iloc[0]
            return formula_id
        return None
    else:
        st.dataframe(df)
        return None
