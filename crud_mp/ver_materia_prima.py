# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.filtros_materias_primas import aplicar_filtros_materias_primas


def ver_materia_prima():
    st.subheader("🔎 Ver y filtrar materias primas")

    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("No hay materias primas registradas.")
        return

    df_filtrado = aplicar_filtros_materias_primas(df)
    df_filtrado = df_filtrado.copy()

    # Inicializar lista de seleccionadas si no existe
    if "mp_seleccionadas" not in st.session_state:
        st.session_state["mp_seleccionadas"] = []

    # Crear columna de selección basada en session_state
    df_filtrado[":Seleccionar"] = df_filtrado["Materia Prima"].isin(st.session_state["mp_seleccionadas"])

    st.markdown("### Resultados filtrados")
    seleccion_df = st.data_editor(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={":Seleccionar": st.column_config.CheckboxColumn("✅")},
        disabled=[col for col in df_filtrado.columns if col != ":Seleccionar"]
    )

    # Actualizar selección en session_state
    seleccionadas = seleccion_df.loc[seleccion_df[":Seleccionar"], "Materia Prima"].dropna().tolist()
    st.session_state["mp_seleccionadas"] = seleccionadas

    if seleccionadas:
        if st.button("🧪 Usar estas materias primas en nueva fórmula"):
            st.session_state["mp_crear"] = seleccionadas
            st.session_state["page"] = "crear_formula"
            st.rerun()
    else:
        st.info("Marca al menos una materia prima en la tabla para continuar.")

