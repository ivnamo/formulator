# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
from utils.supabase_client import supabase
from utils.families import obtener_familias_parametros  # ✅ Importar familias

def crear_materia_prima():
    st.subheader("➕ Crear nueva materia prima")

    with st.form("form_crear_materia_prima", clear_on_submit=True):
        nombre = st.text_input("Nombre de la Materia Prima")
        precio = st.number_input("Precio €/kg", min_value=0.0, step=0.01)
        enviado = st.form_submit_button("Crear")

        if enviado:
            if not nombre:
                st.warning("Debes ingresar un nombre.")
            else:
                try:
                    # ✅ Inicializar todos los parámetros técnicos a 0.0
                    familias = obtener_familias_parametros()
                    columnas_tecnicas = [col for sub in familias.values() for col in sub]
                    campos = {col: 0.0 for col in columnas_tecnicas}
                    campos.update({
                        "Materia Prima": nombre.upper(),
                        "Precio €/kg": precio
                    })

                    supabase.table("materias_primas").insert(campos).execute()
                    st.success("Materia prima creada correctamente.")
                except Exception as e:
                    st.error(f"❌ Error al crear: {e}")
