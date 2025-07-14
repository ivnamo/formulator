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

    if "mp_seleccionadas" not in st.session_state:
        st.session_state["mp_seleccionadas"] = []

    if "mp_checkbox_estado" not in st.session_state:
        st.session_state["mp_checkbox_estado"] = {}

    df_filtrado = aplicar_filtros_materias_primas(df).copy()

    st.markdown("### ✅ Materias primas filtradas")
    for _, row in df_filtrado.iterrows():
        nombre_mp = row["Materia Prima"]
        unique_key = f"chk_{nombre_mp}"

        # Checkbox individual
        marcado = st.checkbox(f"{nombre_mp} – {row.get('Precio €/kg', 'N/A')} €/kg", key=unique_key)
        st.session_state["mp_checkbox_estado"][nombre_mp] = marcado

    # Obtener todas las seleccionadas desde el estado
    seleccionadas_temp = [
        mp for mp, marcado in st.session_state["mp_checkbox_estado"].items() if marcado
    ]

    st.markdown("### 🧪 Depuración")
    st.write("📋 Marcadas ahora:", seleccionadas_temp)
    st.write("📦 Lista persistente:", st.session_state["mp_seleccionadas"])

    if st.button("➕ Añadir seleccionadas a la lista"):
        nuevas = [mp for mp in seleccionadas_temp if mp not in st.session_state["mp_seleccionadas"]]
        st.session_state["mp_seleccionadas"].extend(nuevas)
        st.success(f"{len(nuevas)} añadidas.")
        # Opcional: limpiar checkboxes
        for mp in nuevas:
            st.session_state["mp_checkbox_estado"][mp] = False
        st.rerun()

    st.markdown("### 📌 Lista acumulada")
    if st.session_state["mp_seleccionadas"]:
        st.write(st.session_state["mp_seleccionadas"])
        eliminar = st.multiselect("❌ Quitar", st.session_state["mp_seleccionadas"])
        if st.button("🗑️ Quitar seleccionadas"):
            st.session_state["mp_seleccionadas"] = [mp for mp in st.session_state["mp_seleccionadas"] if mp not in eliminar]
            st.rerun()
    else:
        st.info("Aún no has añadido ninguna materia prima.")

