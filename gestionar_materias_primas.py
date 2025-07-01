import streamlit as st
import pandas as pd
import numpy as np
from supabase_client import supabase

def gestionar_materias_primas(menu):
    if menu != "CRUD Materias Primas":
        return

    st.subheader("🧾 CRUD de Materias Primas")

    if "materias_df" not in st.session_state:
        response = supabase.table("materias_primas").select("*").execute()
        df = pd.DataFrame(response.data)
        st.session_state["materias_df"] = df

    edited_df = st.data_editor(
        st.session_state["materias_df"],
        use_container_width=True,
        num_rows="dynamic",
        key="editor_crud"
    )

    if st.button("💾 Guardar cambios"):
        st.session_state["materias_df"] = edited_df

        # Validar columna obligatoria "Materia Prima"
        if "Materia Prima" not in edited_df.columns:
            st.error("❌ La columna obligatoria 'Materia Prima' no está presente en los datos.")
            return

        if "id" not in edited_df.columns:
            st.error("❌ No se encuentra la columna 'id', necesaria para el upsert.")
            return

        # Limpieza segura para JSON
        cleaned_df = edited_df.copy()
        cleaned_df = cleaned_df.replace({np.nan: None})
        cleaned_data = cleaned_df.to_dict(orient="records")

        try:
            supabase.table("materias_primas").upsert(
                cleaned_data,
                on_conflict=["id"]
            ).execute()
            st.success("Cambios guardados correctamente en Supabase.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")

    st.markdown("---")
    st.subheader("➕ Añadir nueva materia prima")

    with st.form("form_nueva_mp"):
        nueva_nombre = st.text_input("Nombre de la Materia Prima")
        nuevo_precio = st.number_input("Precio €/kg", min_value=0.0, step=0.01)
        submitted = st.form_submit_button("Agregar")

        if submitted:
            if not nueva_nombre:
                st.warning("Debes introducir un nombre.")
            else:
                try:
                    supabase.table("materias_primas").insert([{
                        "Materia Prima": nueva_nombre,
                        "Precio €/kg": nuevo_precio,
                        "%": 0.0
                    }]).execute()
                    st.success("Materia prima añadida correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al añadir: {e}")

    st.markdown("---")
    st.subheader("🗑️ Eliminar materia prima")
    materias_disponibles = st.session_state["materias_df"][["id", "Materia Prima"]]

    if not materias_disponibles.empty:
        seleccion_id = st.selectbox("Selecciona una materia prima para eliminar", materias_disponibles["Materia Prima"])
        fila = materias_disponibles[materias_disponibles["Materia Prima"] == seleccion_id]

        if st.button("Eliminar"):
            if not fila.empty:
                try:
                    supabase.table("materias_primas").delete().eq("id", int(fila.iloc[0]["id"])).execute()
                    st.success("Materia prima eliminada.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al eliminar: {e}")


