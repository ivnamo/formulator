# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import json
import streamlit as st
from streamlit_javascript import st_javascript
from utils.supabase_client import supabase

# Clave de localStorage para persistir sesión (restaura tras inactividad en Streamlit Cloud)
FORMULATOR_AUTH = "FORMULATOR_AUTH"


def _try_restore_session_from_browser():
    """
    Lee localStorage (vía st_javascript), restaura la sesión de Supabase con set_session + refresh_session
    y, si todo va bien, rellena st.session_state.logged_in y user_email.
    Si st_javascript devuelve None o hay cualquier error, no modifica session_state (se mostrará login).
    """
    js_read = f'''(
        function() {{
            try {{
                return localStorage.getItem("{FORMULATOR_AUTH}");
            }} catch (e) {{
                return null;
            }}
        }}
    )()'''
    stored = st_javascript(js_read, key="auth_restore")
    if stored is None or not isinstance(stored, str) or not stored.strip():
        return
    try:
        data = json.loads(stored)
    except json.JSONDecodeError:
        _clear_auth_storage_js()
        return
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    email = data.get("email") or ""
    if not access_token or not refresh_token:
        _clear_auth_storage_js()
        return
    try:
        supabase.auth.set_session(access_token, refresh_token)
        supabase.auth.refresh_session()
        st.session_state.logged_in = True
        st.session_state.user_email = email
        # Opcional: actualizar localStorage con nuevos tokens (refresh_session puede rotar tokens)
        try:
            session = supabase.auth.get_session()
            if session and getattr(session, "session", None):
                s = session.session
                at = s.get("access_token") if isinstance(s, dict) else getattr(s, "access_token", None)
                rt = s.get("refresh_token") if isinstance(s, dict) else getattr(s, "refresh_token", None)
                if at and rt:
                    _save_auth_to_storage_js(at, rt, email)
        except Exception:
            pass
    except Exception:
        _clear_auth_storage_js()


def _clear_auth_storage_js():
    """Ejecuta JS para borrar la clave de auth en localStorage."""
    st_javascript(
        f'localStorage.removeItem("{FORMULATOR_AUTH}"); null',
        key="auth_clear",
    )


def _save_auth_to_storage_js(access_token, refresh_token, email):
    """Guarda access_token, refresh_token y email en localStorage (vía st_javascript)."""
    if not access_token or not refresh_token:
        return
    payload = json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "email": email or "",
    })
    # Escapar para uso dentro de comillas dobles en JS: \ y " y saltos de línea
    escaped = payload.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
    js_save = f'''(
        function() {{
            try {{
                localStorage.setItem("{FORMULATOR_AUTH}", "{escaped}");
            }} catch (e) {{}}
            return null;
        }}
    )()'''
    st_javascript(js_save, key="auth_save")


# Módulos materias primas
from crud_mp.create_materia_prima import crear_materia_prima
from crud_mp.update_materia_prima import actualizar_materia_prima
from crud_mp.delete_materia_prima import eliminar_materia_prima
from crud_mp.ver_materia_prima import ver_materia_prima

# Módulos fórmulas
from crud_formulas.crear_formula import flujo_crear_formula
from crud_formulas.list_formulas import listar_formulas
from crud_formulas.update_formula import actualizar_formula
from crud_formulas.delete_formula import eliminar_formula
from crud_formulas.optimizar_formula import flujo_optimizar_formula
from utils.cargar_formula import cargar_formula_por_id

# 🆕 Módulo calidad
from crud_calidad.vista_calidad import vista_calidad  # Asegúrate de que este archivo exista

# 🔐 Login simple usando Supabase email/password
def login():
    st.set_page_config(layout="centered")
    st.title("🔐 Iniciar sesión")

    with st.form("form_login"):
        email = st.text_input("Email", key="email_login")
        password = st.text_input("Contraseña", type="password", key="pass_login")
        submitted = st.form_submit_button("Entrar")

    if submitted:
        if not email or not password:
            st.warning("Completa ambos campos.")
            return

        try:
            resp = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if resp.user:
                session = getattr(resp, "session", None)
                if session:
                    at = session.get("access_token") if isinstance(session, dict) else getattr(session, "access_token", None)
                    rt = session.get("refresh_token") if isinstance(session, dict) else getattr(session, "refresh_token", None)
                    if at and rt:
                        _save_auth_to_storage_js(at, rt, email)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
        except Exception as e:
            st.error(f"Error de autenticación: {e}")


def main():
    st.set_page_config(layout="wide")

    # 🔐 Restaurar sesión desde localStorage si la conexión se perdió (p. ej. inactividad en Streamlit Cloud)
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        _try_restore_session_from_browser()

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
        menu = st.radio("Navegación", ["Formulas", "Materias Primas", "Calidad"], label_visibility="collapsed")

        st.markdown("---")
        st.markdown(f"**Sesión iniciada como:** {st.session_state.get('user_email', '')}")
        if st.button("🔓 Cerrar sesión"):
            for k in ["logged_in", "user_email"]:
                st.session_state.pop(k, None)
            _clear_auth_storage_js()
            st.rerun()

        st.markdown("""
        **Desarrollado por:** Iván Navarro  
        **Versión:** 1.0.0  
        **Fecha:** 01/07/2025
        """)

    # --- Materias Primas ---
    if menu == "Materias Primas":
        subtarea = st.selectbox("Acción sobre materias primas", ["Ver", "Crear", "Actualizar", "Eliminar"])

        if subtarea == "Ver":
            ver_materia_prima()
        elif subtarea == "Crear":
            crear_materia_prima()
        elif subtarea == "Actualizar":
            actualizar_materia_prima()
        elif subtarea == "Eliminar":
            eliminar_materia_prima()
        return

    # --- Formulas ---

    if menu == "Formulas":
        subtarea = st.selectbox("Acción sobre fórmulas", ["Crear", "Ver", "Actualizar", "Eliminar", "Optimizar"])



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

    # --- Calidad ---
    if menu == "Calidad":
        vista_calidad()
        return


if __name__ == "__main__":
    main()
