# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import streamlit as st
from utils.supabase_client import supabase
from crud_mp.create_materia_prima import crear_materia_prima
from crud_mp.update_materia_prima import actualizar_materia_prima
from crud_mp.delete_materia_prima import eliminar_materia_prima
from crud_formulas.crear_formula import flujo_crear_formula
from crud_formulas.list_formulas import listar_formulas
from crud_formulas.update_formula import actualizar_formula
from crud_formulas.delete_formula import eliminar_formula
from utils.cargar_formula import cargar_formula_por_id
from crud_formulas.optimizar_formula import flujo_optimizar_formula  # 🆕 nuevo flujo
from streamlit_javascript import st_javascript

# 🔐 Login simple usando Supabase email/password
def login():
    st.set_page_config(layout="centered")
    st.title("🔐 Iniciar sesión")

    # Intenta capturar los valores directamente desde el DOM con JS
    email = st_javascript("""
        const input = window.document.querySelector('input[type="text"]');
        if (input) input.value;
        """)
    password = st_javascript("""
        const input = window.document.querySelector('input[type="password"]');
        if (input) input.value;
        """)

    # Mostrar los campos (visualmente)
    st.text_input("Email", key="email_login", value=email or "")
    st.text_input("Contraseña", type="password", key="pass_login", value=password or "")

    if st.button("Entrar"):
        try:
            resp = supabase.auth.sign_in_with_password({
                "email": st.session_state.get("email_login", ""),
                "password": st.session_state.get("pass_login", "")
            })
            if resp.user:
                st.session_state.logged_in = True
                st.session_state.user_email = st.session_state.get("email_login", "")
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
        except Exception as e:
            st.error(f"Error de autenticación: {e}")

def main():
    st.set_page_config(layout="wide")

    # 🔐 Requiere login previo
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login()
        return

    # 📥 Cargar fórmula desde la URL si se accede con ?formula_id=...
    params = st.query_params
    if "formula_id" in params:
        cargar_formula_por_id(params["formula_id"])
        return

    st.title("Calculadora de Fórmulas - Composición + Coste")

    with st.sidebar:
        st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; padding: 10px 0;'>
            <img src='https://raw.githubusercontent.com/ivnamo/formulator/main/logo.png' style='width: 200px; height: auto; object-fit: contain;'>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Navegación")
        menu = st.radio("Navegación", ["Formulas", "Materias Primas"], label_visibility="collapsed")

        st.markdown("---")
        st.markdown(f"**Sesión iniciada como:** {st.session_state.get('user_email', '')}")
        if st.button("🔓 Cerrar sesión"):
            for k in ["logged_in", "user_email"]:
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown("""
        **Desarrollado por:** Iván Navarro  
        **Versión:** 1.0.0  
        **Fecha:** 01/07/2025
        """)

    if menu == "Materias Primas":
        subtarea = st.selectbox("Acción sobre materias primas", ["Crear", "Actualizar", "Eliminar"])

        if subtarea == "Crear":
            crear_materia_prima()
        elif subtarea == "Actualizar":
            actualizar_materia_prima()
        elif subtarea == "Eliminar":
            eliminar_materia_prima()
        return

    if menu == "Formulas":
        subtarea = st.selectbox("Acción sobre fórmulas", ["Crear", "Actualizar", "Eliminar", "Ver", "Optimizar"])

        if subtarea == "Crear":
            flujo_crear_formula()
        elif subtarea == "Actualizar":
            formula_id = listar_formulas(seleccionar=True)
            actualizar_formula(formula_id)
        elif subtarea == "Eliminar":
            eliminar_formula()
        elif subtarea == "Ver":
            formula_id = listar_formulas(seleccionar=True)
            if formula_id:
                cargar_formula_por_id(formula_id)
        elif subtarea == "Optimizar":
            flujo_optimizar_formula()
        return

if __name__ == "__main__":
    main()
