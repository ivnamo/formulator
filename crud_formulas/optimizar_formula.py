# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------
import streamlit as st
import pandas as pd
from utils.supabase_client import supabase
from utils.families import obtener_familias_parametros
from utils.ejecutar_motor import ejecutar_motor
from utils.formula_resultados import calcular_resultado_formula
from utils.resultados import mostrar_resultados
from utils.data_loader import cargar_datos


def flujo_optimizar_formula():
    st.title("🧮 Optimización de Fórmulas")

    df = cargar_datos()

    if df.empty or "Materia Prima" not in df.columns:
        st.error("No hay materias primas disponibles o falta la columna 'Materia Prima'.")
        return

    seleccionadas = st.multiselect("Selecciona materias primas para optimizar", df["Materia Prima"].dropna().tolist())
    if not seleccionadas:
        st.info("Selecciona al menos una materia prima para empezar.")
        return

    df_seleccion = df[df["Materia Prima"].isin(seleccionadas)].copy()

    familias = obtener_familias_parametros()
    seleccionadas_familias = st.multiselect("Selecciona familias de parámetros", list(familias), default=list(familias))
    columnas_tecnicas = [col for fam in seleccionadas_familias for col in familias[fam] if col in df.columns]

    columnas_param_opt = [col for col in columnas_tecnicas if df_seleccion[col].fillna(0).gt(0).any()]
    columnas_restricciones = st.multiselect("Selecciona parámetros a restringir", columnas_param_opt)

    restricciones = {}
    for col in columnas_restricciones:
        valores = df_seleccion[col].fillna(0)
        min_val = float(valores.min())
        max_val = float(valores.max())
        val_min, val_max = st.slider(f"Rango para {col} (%)", min_value=min_val, max_value=max_val, value=(min_val, max_val), step=0.01)
        restricciones[col] = {"min": val_min, "max": val_max}

    modo = st.radio("Tipo de optimización", ["Minimizar", "Maximizar"], horizontal=True)

    opciones_objetivo = ["Precio €/kg"] + columnas_param_opt + seleccionadas
    variable_objetivo = st.selectbox("Selecciona la variable objetivo", opciones_objetivo)

    motores = st.multiselect("Selecciona motores de optimización", ["Simplex", "SLSQP", "COBYLA", "Genético"], default=["Simplex"])
    parametros_extra = {}

    if "Genético" in motores:
        with st.expander("⚙️ Parámetros del algoritmo genético", expanded=False):
            n_ind = st.slider("Número de individuos", 10, 200, value=50, step=10)
            n_gen = st.slider("Número de generaciones", 10, 300, value=100, step=10)
            cxpb = st.slider("Probabilidad de cruce (cxpb)", 0.0, 1.0, value=0.7, step=0.05)
            mutpb = st.slider("Probabilidad de mutación (mutpb)", 0.0, 1.0, value=0.2, step=0.05)
    
            parametros_extra["Genético"] = {
                "n_individuos": n_ind,
                "n_generaciones": n_gen,
                "cxpb": cxpb,
                "mutpb": mutpb
            }



    if st.button("🔧 Ejecutar optimización"):
        restricciones_min = {k: v["min"] for k, v in restricciones.items()}
        restricciones_max = {k: v["max"] for k, v in restricciones.items()}

        st.session_state.resultados_optimizacion = []
        for motor in motores:
            resultado = ejecutar_motor(
                motor=motor,
                df=df_seleccion,
                columnas_objetivo=columnas_tecnicas,
                restricciones_min=restricciones_min,
                restricciones_max=restricciones_max,
                variable_objetivo=variable_objetivo,
                modo=modo,
                parametros_extra=parametros_extra
            )
            st.session_state.resultados_optimizacion.append(resultado)

    # Si hay resultados guardados
    if "resultados_optimizacion" in st.session_state:
        resultados = st.session_state.resultados_optimizacion

        # 📊 Tabla comparativa
        tabla = []
        for r in resultados:
            unidad = "€/kg" if variable_objetivo == "Precio €/kg" else "% p/p"
            tabla.append({
                "Motor": r["motor"],
                "Resultado": round(r["valor_objetivo"], 3) if r["exito"] else None,
                "Unidad": unidad if r["exito"] else "",
                "Estado": "✅ Éxito" if r["exito"] else f"❌ {r['mensaje']}"
            })

 

        st.markdown("## 📋 Comparativa de motores")
        st.dataframe(pd.DataFrame(tabla))

        # 🔍 Mostrar resultados individuales en cajas expandibles
        st.markdown("## 🔎 Resultados detallados por motor")
        for r in resultados:
            if r["exito"]:
                with st.expander(f"🔹 {r['motor']} – Resultado: {r['valor_objetivo']:.3f}", expanded=False):
                    st.markdown(f"### 📦 Fórmula optimizada con **{r['motor']}**")
                    st.dataframe(r["df"][["Materia Prima", "%", "Precio €/kg"] + columnas_tecnicas])

                    _, composicion = calcular_resultado_formula(r["df"], columnas_tecnicas)
                    columnas_mayor_0 = composicion[composicion["Cantidad %"] > 0].index.tolist()
                    mostrar_resultados(r["df"], columnas_mayor_0)

        # 📈 Comparación visual de composiciones
        st.markdown("## 📊 Comparación visual de parámetros técnicos")
        comp_all = {}
        for r_ in resultados:
            if r_["exito"]:
                _, comp = calcular_resultado_formula(r_["df"], columnas_tecnicas)
                comp_all[r_["motor"]] = comp["Cantidad %"]
        df_comp = pd.DataFrame(comp_all).fillna(0)
        if not df_comp.empty:
            st.bar_chart(df_comp)


