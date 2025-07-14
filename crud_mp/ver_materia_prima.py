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

    # Inicializar lista persistente si no existe
    if "mp_seleccionadas" not in st.session_state:
        st.session_state["mp_seleccionadas"] = []

    df_filtrado = aplicar_filtros_materias_primas(df).copy()
    df_filtrado[":Seleccionar"] = False

    st.markdown("### Resultados filtrados")
    seleccion_df = st.data_editor(
        df_filtrado,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={":Seleccionar": st.column_config.CheckboxColumn("✅")},
        disabled=[col for col in df_filtrado.columns if col != ":Seleccionar"]
    )

    seleccionadas_temp = seleccion_df.loc[seleccion_df[":Seleccionar"], "Materia Prima"].dropna().tolist()

    if seleccionadas_temp:
        if st.button("➕ Añadir seleccionadas a la lista"):
            nuevas = [mp for mp in seleccionadas_temp if mp not in st.session_state["mp_seleccionadas"]]
            st.session_state["mp_seleccionadas"].extend(nuevas)
            st.rerun()

    # Mostrar lista persistente de seleccionadas
    if st.session_state["mp_seleccionadas"]:
        st.markdown("### 🧾 Lista de materias primas seleccionadas")
        st.write(st.session_state["mp_seleccionadas"])

        eliminar = st.multiselect(
            "❌ Quitar de la lista",
            options=st.session_state["mp_seleccionadas"],
            key="mp_a_eliminar"
        )

        if eliminar:
            if st.button("🗑️ Quitar seleccionadas"):
                st.session_state["mp_seleccionadas"] = [mp for mp in st.session_state["mp_seleccionadas"] if mp not in eliminar]
                st.rerun()

        if st.button("🧪 Usar estas materias primas en nueva fórmula"):
            st.session_state["mp_crear"] = st.session_state["mp_seleccionadas"]
            st.session_state["page"] = "crear_formula"
            st.rerun()
    else:
        st.info("Añade materias primas a la lista para poder continuar.")
