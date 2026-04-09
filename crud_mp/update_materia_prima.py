# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import st_aggrid
import streamlit as st
import pandas as pd
import numpy as np
import json
import time
import platform
from utils.supabase_client import supabase


def _debug_log(run_id, hypothesis_id, location, message, data):
    payload = {
        "sessionId": "47a1e8",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with open("debug-47a1e8.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def actualizar_materia_prima():
    st.subheader("✏️ Actualizar materias primas")

    # region agent log
    _debug_log("baseline", "H1", "crud_mp/update_materia_prima.py:31", "enter actualizar_materia_prima", {})
    # endregion
    # region agent log
    _debug_log(
        "baseline",
        "H5",
        "crud_mp/update_materia_prima.py:40",
        "runtime versions",
        {
            "python_version": platform.python_version(),
            "streamlit_version": getattr(st, "__version__", "unknown"),
            "st_aggrid_version": getattr(st_aggrid, "__version__", "unknown"),
        },
    )
    # endregion

    # Cargar datos desde Supabase
    response = supabase.table("materias_primas").select("*").execute()
    # region agent log
    _debug_log(
        "baseline",
        "H1",
        "crud_mp/update_materia_prima.py:37",
        "supabase response received",
        {"has_data_attr": hasattr(response, "data"), "data_len": len(response.data) if getattr(response, "data", None) else 0},
    )
    # endregion
    df = pd.DataFrame(response.data)
    # region agent log
    _debug_log(
        "baseline",
        "H2",
        "crud_mp/update_materia_prima.py:46",
        "dataframe built",
        {
            "shape": [int(df.shape[0]), int(df.shape[1])],
            "columns": [str(c) for c in df.columns.tolist()],
            "object_columns": [str(c) for c in df.select_dtypes(include=["object"]).columns.tolist()],
        },
    )
    # endregion

    # Ordenar alfabéticamente por nombre, si existe
    if not df.empty and "Materia Prima" in df.columns:
        df = df.sort_values("Materia Prima", ascending=True).reset_index(drop=True)

    if df.empty:
        # region agent log
        _debug_log("baseline", "H1", "crud_mp/update_materia_prima.py:62", "empty dataframe branch", {})
        # endregion
        st.info("No hay materias primas disponibles.")
        return

    # Configurar grid editable
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        editable=True,
        filter=True,
        sortable=True,
        floatingFilter=True,
        width=120,       # ✅ fuerza ancho base
        minWidth=100,
        resizable=True,
    )
    gb.configure_column("id", editable=False)
    grid_options = gb.build()

    # CSS para asegurar scroll y estilo
    st.markdown(
        """
        <style>
        .ag-theme-streamlit {
            overflow: auto !important;
            max-height: 600px !important;
            font-family: monospace;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Mostrar la tabla con scroll
    try:
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.VALUE_CHANGED,
            theme="streamlit",
            fit_columns_on_grid_load=False,
            height=600,
            allow_unsafe_jscode=True,
        )
        # region agent log
        _debug_log(
            "baseline",
            "H3",
            "crud_mp/update_materia_prima.py:92",
            "aggrid rendered",
            {
                "grid_response_type": str(type(grid_response)),
                "is_dict": isinstance(grid_response, dict),
                "has_data_attr": hasattr(grid_response, "data"),
                "dict_keys": [str(k) for k in grid_response.keys()] if isinstance(grid_response, dict) else [],
                "rows_in_attr_data": len(getattr(grid_response, "data", [])) if hasattr(grid_response, "data") else -1,
            },
        )
        # endregion
    except Exception as e:
        # region agent log
        _debug_log(
            "baseline",
            "H4",
            "crud_mp/update_materia_prima.py:104",
            "aggrid exception",
            {"error_type": type(e).__name__, "error_message": str(e)},
        )
        # endregion
        st.error(f"❌ Error al renderizar la tabla editable: {e}")
        return

    edited_df = grid_response["data"]
    # region agent log
    _debug_log(
        "baseline",
        "H6",
        "crud_mp/update_materia_prima.py:122",
        "edited_df extracted",
        {
            "edited_df_type": str(type(edited_df)),
            "edited_df_len": len(edited_df) if hasattr(edited_df, "__len__") else -1,
        },
    )
    # endregion

    with st.expander("Debug runtime (temporal)"):
        st.write(
            {
                "python": platform.python_version(),
                "streamlit": getattr(st, "__version__", "unknown"),
                "st_aggrid": getattr(st_aggrid, "__version__", "unknown"),
                "rows_df": int(df.shape[0]),
                "cols_df": int(df.shape[1]),
                "grid_response_type": str(type(grid_response)),
            }
        )
        st.dataframe(df.head(10), width="stretch", hide_index=True)

    if st.button("💾 Guardar cambios"):
        # 🔧 Limpieza para evitar columnas fantasma y NaN → None
        cleaned_df = pd.DataFrame(edited_df).copy()

        # Columnas auxiliares de AgGrid o índices heredados
        for col in ["__rowIndex__", "index", "index_level_0"]:
            if col in cleaned_df.columns:
                cleaned_df = cleaned_df.drop(columns=[col])

        cleaned_df = cleaned_df.reset_index(drop=True)
        cleaned_df = cleaned_df.replace({np.nan: None})

        try:
            supabase.table("materias_primas").upsert(
                cleaned_df.to_dict(orient="records"),
                on_conflict=["id"],
            ).execute()
            st.success("Cambios guardados correctamente.")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")

