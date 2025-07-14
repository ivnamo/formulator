import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.filtros_materias_primas import aplicar_filtros_materias_primas


def ver_materia_prima():
    st.subheader("🔎 Materias primas (estilo tabla interactiva)")

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
    columnas_mostrar = ["Materia Prima", "Precio €/kg", "Ntotal", "K2O", "CaO"]

    st.markdown("### 📋 Selección de materias primas")

    # Cabecera de tabla
    cols = st.columns([0.1, 0.3, 0.2, 0.1, 0.1, 0.1])
    cols[0].markdown("**✅**")
    for i, col in enumerate(columnas_mostrar):
        cols[i + 1].markdown(f"**{col}**")

    # Filas de datos con checkbox
    for i, row in df_filtrado.iterrows():
        nombre = row["Materia Prima"]
        key = f"chk_{nombre}"

        marcado = st.session_state["mp_checkbox_estado"].get(nombre, False)
        cols = st.columns([0.1, 0.3, 0.2, 0.1, 0.1, 0.1])
        marcado = cols[0].checkbox("", value=marcado, key=key)
        st.session_state["mp_checkbox_estado"][nombre] = marcado

        for j, col in enumerate(columnas_mostrar):
            valor = row.get(col, "–")
            if pd.isna(valor):
                valor = "–"
            cols[j + 1].write(valor)

    # Obtener los seleccionados
    seleccionadas_temp = [
        mp for mp, marcado in st.session_state["mp_checkbox_estado"].items() if marcado
    ]

    # DEBUG
    st.markdown("### 🔍 DEBUG")
    st.write("📌 Marcadas ahora:", seleccionadas_temp)
    st.write("📦 Lista persistente:", st.session_state["mp_seleccionadas"])

    # Botón para añadir
    if st.button("➕ Añadir seleccionadas"):
        nuevas = [mp for mp in seleccionadas_temp if mp not in st.session_state["mp_seleccionadas"]]
        st.session_state["mp_seleccionadas"].extend(nuevas)
        st.success(f"✅ Añadidas {len(nuevas)} materias primas.")
        for mp in nuevas:
            st.session_state["mp_checkbox_estado"][mp] = False
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
