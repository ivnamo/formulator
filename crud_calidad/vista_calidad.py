# crud_calidad/vista_calidad.py
import streamlit as st
import pandas as pd
from datetime import date

from crud_formulas.list_formulas import listar_formulas
from crud_calidad.create_calidad import crear_registro_calidad
from crud_calidad.list_calidad import listar_registros_calidad
from crud_calidad.update_calidad import actualizar_estado_calidad


def vista_calidad():
    st.subheader("🧪 Gestión de Calidad")

    pestañas = st.tabs(["➕ Registrar evaluación", "📋 Ver y actualizar evaluaciones"])

    # -------- TAB 1: Crear nueva evaluación de calidad --------
    with pestañas[0]:
        st.markdown("### Registrar envío de fórmula a calidad")

        formula_id = listar_formulas(seleccionar=True)
        if formula_id:
            codigo = st.text_input("Código de evaluación", placeholder="Ej. ID.2025.34")
            fecha_envio = st.date_input("Fecha de envío", value=date.today())
            observaciones = st.text_area("Observaciones iniciales", placeholder="Opcional")

            if st.button("📨 Registrar evaluación"):
                if not codigo.strip():
                    st.warning("⚠️ El código es obligatorio.")
                else:
                    crear_registro_calidad(formula_id, codigo.strip(), fecha_envio, observaciones.strip())
                    st.success("✅ Evaluación registrada correctamente.")
                    st.rerun()

    # -------- TAB 2: Ver y actualizar --------
    with pestañas[1]:
        st.markdown("### 📋 Registros de calidad")

        registros = listar_registros_calidad()
        if not registros:
            st.info("No hay registros de calidad todavía.")
            return

        df = pd.DataFrame(registros)
        df = df.sort_values("fecha_envio", ascending=False)

        # Obtener nombres de fórmulas
        formulas_df = listar_formulas(seleccionar=False)
        if isinstance(formulas_df, pd.DataFrame):
            df = df.merge(formulas_df, left_on="formula_id", right_on="id", how="left", suffixes=('', '_formula'))
            df["nombre_formula"] = df["nombre"]
        else:
            df["nombre_formula"] = df["formula_id"]

        # Crear etiquetas para el selector
        df["etiqueta_selector"] = df.apply(
            lambda row: f"{row['codigo']} – {row['nombre_formula']}", axis=1
        )

        seleccion = st.selectbox("Selecciona un registro", df["etiqueta_selector"].tolist())
        fila = df[df["etiqueta_selector"] == seleccion].iloc[0]

        st.write(f"🧪 Fórmula asociada: **{fila['nombre_formula']}**")
        st.write(f"📅 Fecha de envío: `{fila['fecha_envio']}`")
        st.write(f"📌 Estado actual: `{fila['estado']}`")
        st.write("📝 Observaciones actuales:")
        st.info(fila["observaciones"] or "Sin observaciones")

        nuevo_estado = st.selectbox(
            "Actualizar estado",
            ["Pendiente", "OK", "NOK", "Cancelado"],
            index=["Pendiente", "OK", "NOK", "Cancelado"].index(fila["estado"])
        )

        nuevas_obs = st.text_area("Actualizar observaciones", value=fila["observaciones"] or "", height=100)

        if st.button("💾 Guardar cambios"):
            actualizar_estado_calidad(fila["id"], nuevo_estado, nuevas_obs.strip())
            st.success("✅ Evaluación actualizada.")
            st.rerun()
