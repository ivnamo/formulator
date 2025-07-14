import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.filtros_materias_primas import aplicar_filtros_materias_primas


def ver_materia_prima():
    st.subheader("🔎 Materias primas (vista tabla)")

    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("No hay materias primas registradas.")
        return

    if "mp_seleccionadas" not in st.session_state:
        st.session_state["mp_seleccionadas"] = []

    if "mp_checkbox_estado" not in st.session_state:
        st.session_state["mp_checkbox_estado"] = {}

    df_filtrado = aplicar_filtros_materias_primas(df).copy()
    columnas_tabla = ["Materia Prima", "Precio €/kg", "Ntotal", "K2O", "CaO", "MgO"]  # puedes ajustar
    df_tabla = df_filtrado[columnas_tabla].fillna("–")

    st.markdown("### 🧾 Tabla con selección")

    with st.form("tabla_materias"):
        tabla_data = []
        for i, row in df_tabla.iterrows():
            nombre = row["Materia Prima"]
            key = f"chk_row_{nombre}"
            marcado = st.checkbox("", key=key)
            st.session_state["mp_checkbox_estado"][nombre] = marcado
            tabla_data.append([marcado] + list(row.values))

        df_visual = pd.DataFrame(tabla_data, columns=["✅"] + list(df_tabla.columns))
        st.dataframe(df_visual, use_container_width=True)

        if st.form_submit_button("➕ Añadir seleccionadas"):
            seleccionadas = [mp for mp, sel in st.session_state["mp_checkbox_estado"].items() if sel]
            nuevas = [mp for mp in seleccionadas if mp not in st.session_state["mp_seleccionadas"]]
            st.session_state["mp_seleccionadas"].extend(nuevas)
            for mp in nuevas:
                st.session_state["mp_checkbox_estado"][mp] = False
            st.success(f"{len(nuevas)} añadidas a la lista")
            st.rerun()

    st.markdown("### 📌 Lista acumulada")
    if st.session_state["mp_seleccionadas"]:
        st.write(st.session_state["mp_seleccionadas"])
        eliminar = st.multiselect("❌ Quitar", st.session_state["mp_seleccionadas"])
        if st.button("🗑️ Quitar seleccionadas"):
            st.session_state["mp_seleccionadas"] = [
                mp for mp in st.session_state["mp_seleccionadas"] if mp not in eliminar
            ]
            st.rerun()
    else:
        st.info("No hay materias primas en la lista.")


