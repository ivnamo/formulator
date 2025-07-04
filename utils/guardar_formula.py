# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import uuid
import json
from datetime import datetime
from utils.supabase_client import supabase

from utils.formula_resultados import calcular_resultado_formula  # asegúrate de importar esto al inicio

# Guardar y generar QR
st.markdown("---")
st.subheader("💾 Guardar fórmula")

nombre_formula = st.text_input("Nombre de la fórmula", placeholder="Ej. Bioestimulante Algas v1")
if st.button("Guardar fórmula"):
    if not nombre_formula.strip():
        st.warning("Debes ingresar un nombre para guardar la fórmula.")
    else:
        # Recalcular precio y composición técnica para obtener el precio
        precio, _ = calcular_resultado_formula(df_editado, columnas_filtradas)
        formula_id = guardar_formula(df_editado, nombre_formula.strip(), precio)
        url_formula = f"https://formulator-pruebas.streamlit.app//?formula_id={formula_id}"  # reemplazar por URL real
        qr_img = generar_qr(url_formula)

        st.success("✅ Fórmula guardada correctamente.")
        st.image(qr_img, caption="Código QR para esta fórmula", use_column_width=False)
        st.code(url_formula, language="markdown")

