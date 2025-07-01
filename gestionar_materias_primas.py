import streamlit as st
import pandas as pd
import numpy as np
from supabase_client import supabase

def gestionar_materias_primas(menu):
    if menu != "CRUD Materias Primas":
        return

    st.subheader("🧾 CRUD de Materias Primas")

    def cargar_materias():
        response = supabase.table("materias_primas").select("*").execute()
        return pd.DataFrame(response.data)

    df = cargar_materias()
    st.session_state["materias_df"] = df.copy()

    st.markdown("---")
    st.subheader("✏️ Editor de materias primas")

    edited_df = st.data_editor(
        st.session_state["materias_df"],
        use_container_width=True,
        num_rows="dynamic",
        key="editor_crud",
        column_config={col: st.column_config.Column(disabled=(col == "id")) for col in df.columns}
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("➕ Añadir fila vacía"):
            nueva_fila = {col: None for col in df.columns}
            nueva_fila["id"] = df["id"].max() + 1 if not df.empty else 1
            st.session_state["materias_df"] = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.rerun()

    with col2:
        if st.button("🗑️ Eliminar fila seleccionada"):
            seleccion = edited_df.get("_selected_row", None)
            if seleccion is None or isinstance(seleccion, pd.Series):
                st.warning("Primero selecciona una fila para eliminar.")
            else:
                fila = edited_df.iloc[seleccion]
                try:
                    supabase.table("materias_primas").delete().eq("id", int(fila["id"])).execute()
                    st.success("Fila eliminada correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al eliminar: {e}")

    with col3:
        if st.button("💾 Guardar cambios"):
            if "Materia Prima" not in edited_df.columns:
                st.error("❌ La columna obligatoria 'Materia Prima' no está presente en los datos.")
                return
            if "id" not in edited_df.columns:
                st.error("❌ No se encuentra la columna 'id', necesaria para el upsert.")
                return
            cleaned_df = edited_df.replace({np.nan: None})
            try:
                supabase.table("materias_primas").upsert(
                    cleaned_df.to_dict(orient="records"),
                    on_conflict=["id"]
                ).execute()
                st.success("Cambios guardados correctamente en Supabase.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")



