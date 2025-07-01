
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd
import numpy as np
from supabase_client import supabase

def actualizar_materia_prima():
    st.subheader("✏️ Actualizar materias primas")

    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.info("No hay materias primas disponibles.")
        return

    # Configurar columnas
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        editable=True,
        filter=True,
        sortable=True,
        floatingFilter=True,
        minWidth=100,
        maxWidth=150  # ✅ limite superior para evitar columnas desproporcionadas
    )
    gb.configure_column("id", editable=False)
    grid_options = gb.build()

    # CSS para asegurar scroll y estilo
    st.markdown("""
        <style>
        .ag-theme-streamlit {
            overflow: auto !important;
            max-height: 600px !important;
            font-family: monospace;
        }
        </style>
    """, unsafe_allow_html=True)

    # Mostrar la tabla con scroll
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        theme="streamlit",
        fit_columns_on_grid_load=False,
        height=600,
        allow_unsafe_jscode=True
    )

    edited_df = grid_response["data"]

    if st.button("💾 Guardar cambios"):
        cleaned_df = edited_df.replace({np.nan: None})
        try:
            supabase.table("materias_primas").upsert(
                cleaned_df.to_dict(orient="records"),
                on_conflict=["id"]
            ).execute()
            st.success("Cambios guardados correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")


