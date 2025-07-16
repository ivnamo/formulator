# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import json
from io import BytesIO
from datetime import datetime
from utils.supabase_client import supabase
from utils.formula_resultados import calcular_resultado_formula
from utils.exportar_formula import exportar_formula_excel
from utils.generar_etiqueta import generar_etiqueta
from utils.generar_qr import generar_qr
from streamlit_javascript import st_javascript  # ✅ para URL dinámica

def cargar_formula_por_id(formula_id: str):
    """
    Carga y muestra una fórmula en modo solo lectura, a partir del ID en Supabase.

    Args:
        formula_id (str): UUID de la fórmula a cargar.
    """
    st.subheader("📄 Fórmula guardada")

    try:
        response = supabase.table("formulas").select("*").eq("id", formula_id).single().execute()
        data = response.data

        if data is None:
            st.error("❌ No se encontró ninguna fórmula con ese ID.")
            return

        nombre = data["nombre"]
        precio = data["precio_total"]
        fecha_iso = data.get("fecha_creacion", "")[:10]
        fecha_formateada = datetime.strptime(fecha_iso, "%Y-%m-%d").strftime("%d/%m/%Y") if fecha_iso else ""
        materias_primas = pd.DataFrame(json.loads(data["materias_primas"]))

        # 🔁 Obtener código desde tabla "calidad"
        codigo = ""
        try:
            calidad_resp = supabase.table("calidad").select("codigo").eq("formula_id", formula_id).limit(1).execute()
            if calidad_resp.data and len(calidad_resp.data) > 0:
                codigo = calidad_resp.data[0].get("codigo", "")
        except Exception as e:
            st.warning(f"No se pudo cargar el código de calidad: {e}")

        st.markdown(f"### 🧪 **{nombre}**")
        st.markdown(f"#### 🏷️ **{codigo}**")
        st.markdown(f"**💰 Precio por kg:** {precio:.2f} €")

        # 👁 Vista previa (ocultar columnas, no eliminarlas)
        columnas_visibles = ["Materia Prima", "%"]
        if all(col in materias_primas.columns for col in columnas_visibles):
            materias_vista = materias_primas[columnas_visibles].rename(columns={"%": "Porcentaje"}).copy()
            st.markdown(materias_vista.to_html(index=False), unsafe_allow_html=True)
        else:
            st.warning("No se pueden mostrar columnas visibles esperadas.")

        # 📊 Composición
        st.markdown("#### 📊 Composición estimada")
        columnas_tecnicas = [
            col for col in materias_primas.columns
            if col not in ["Materia Prima", "%", "Precio €/kg", "id"]
        ]
        precio_calc, composicion = calcular_resultado_formula(materias_primas, columnas_tecnicas)
        composicion = composicion[composicion["Cantidad %"] > 0] if not composicion.empty else pd.DataFrame()

        if not composicion.empty:
            composicion_formateada = composicion.reset_index()
            composicion_formateada.columns = ["Parámetro", "% p/p"]
            st.markdown(composicion_formateada.to_html(index=False), unsafe_allow_html=True)
        else:
            st.info("No hay parámetros significativos en la fórmula.")

        # 📄 Descargar Excel directamente
        st.markdown("---")
        st.subheader("📄 Exportar esta fórmula")
        excel_bytes = exportar_formula_excel(materias_primas, nombre)
        st.download_button(
            label="📃 Descargar archivo Excel",
            data=excel_bytes,
            file_name=f"{nombre}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # 🏷️ Generar etiqueta PDF
        st.markdown("---")
        st.subheader("🏷️ Generar etiqueta PDF")
        # ✅ Captura segura del host actual con fallback
        host_url = st_javascript("window.location.origin")
        url_formula = f"{host_url}/?formula_id={formula_id}"
        # 🔄 Generar automáticamente el QR y el PDF sin esperar botón
        qr_img = generar_qr(url_formula)
        etiqueta_pdf = generar_etiqueta(nombre=nombre, fecha=fecha_formateada, qr_img=qr_img, codigo=codigo)
        # ⬇️ Botón de descarga directo
        st.download_button(
            label="📅 Descargar etiqueta PDF",
            data=etiqueta_pdf,
            file_name=f"Etiqueta_{nombre}.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"⚠️ Error al cargar la fórmula: {e}")
