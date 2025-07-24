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

    #response = supabase.table("materias_primas").select("*").execute()
    #df = pd.DataFrame(response.data)
    #df["%"] = 0.0
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

    motores = st.multiselect("Selecciona motores de optimización", ["Simplex", "SLSQP"], default=["Simplex"])

    if st.button("🔧 Ejecutar optimización"):
        restricciones_min = {k: v["min"] for k, v in restricciones.items()}
        restricciones_max = {k: v["max"] for k, v in restricciones.items()}

        resultados = []
        for motor in motores:
            resultado = ejecutar_motor(
                motor=motor,
                df=df_seleccion,
                columnas_objetivo=columnas_tecnicas,
                restricciones_min=restricciones_min,
                restricciones_max=restricciones_max,
                variable_objetivo=variable_objetivo,
                modo=modo
            )
            resultados.append(resultado)

        # 📊 Tabla comparativa
        tabla = []
        for r in resultados:
            if r["exito"]:
                unidad = "€/kg" if variable_objetivo == "Precio €/kg" else "% p/p"
                tabla.append({
                    "Motor": r["motor"],
                    "Resultado": round(r["valor_objetivo"], 3),
                    "Unidad": unidad,
                    "Estado": "✅ Éxito"
                })
            else:
                tabla.append({
                    "Motor": r["motor"],
                    "Resultado": "-",
                    "Unidad": "",
                    "Estado": f"❌ {r['mensaje']}"
                })

        st.markdown("## 📋 Comparativa de motores")
        st.dataframe(pd.DataFrame(tabla))

        # 📌 Selector para ver detalle de cada motor
        motores_ok = [r["motor"] for r in resultados if r["exito"]]
        if motores_ok:
            seleccionado = st.selectbox("🔍 Ver resultado de un motor", motores_ok)
            r = next(x for x in resultados if x["motor"] == seleccionado)

            st.markdown(f"### 🔹 Fórmula optimizada con **{r['motor']}**")
            st.dataframe(r["df"][["Materia Prima", "%", "Precio €/kg"] + columnas_tecnicas])

            _, composicion = calcular_resultado_formula(r["df"], columnas_tecnicas)
            columnas_mayor_0 = composicion[composicion["Cantidad %"] > 0].index.tolist()

            mostrar_resultados(r["df"], columnas_mayor_0)

            # 📈 Comparativa de composiciones (opcional)
            st.markdown("## 📊 Comparación visual de parámetros técnicos")
            comp_all = {}
            for r_ in resultados:
                if r_["exito"]:
                    _, comp = calcular_resultado_formula(r_["df"], columnas_tecnicas)
                    comp_all[r_["motor"]] = comp["Cantidad %"]
            df_comp = pd.DataFrame(comp_all).fillna(0)
            if not df_comp.empty:
                st.bar_chart(df_comp)

