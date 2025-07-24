# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------
import pandas as pd
from utils.optimizadores import (
    optimizar_simplex,
    optimizar_slsqp,
    optimizar_cobyla,
    optimizar_genetico
)

def ejecutar_motor(
    motor: str,
    df: pd.DataFrame,
    columnas_objetivo: list,
    restricciones_min: dict,
    restricciones_max: dict,
    variable_objetivo: str,
    modo: str
) -> dict:
    try:
        if motor == "Simplex":
            df_opt, valor = optimizar_simplex(
                df, columnas_objetivo, restricciones_min, restricciones_max,
                variable_objetivo, modo
            )
        elif motor == "SLSQP":
            df_opt, valor = optimizar_slsqp(
                df, columnas_objetivo, restricciones_min, restricciones_max,
                variable_objetivo, modo
            )
        elif motor == "COBYLA":
            df_opt, valor = optimizar_cobyla(
                df, columnas_objetivo, restricciones_min, restricciones_max,
                variable_objetivo, modo
            )
        elif motor == "Genético":
            df_opt, valor = optimizar_genetico(
                df, columnas_objetivo, restricciones_min, restricciones_max,
                variable_objetivo, modo
            )
        else:
            return {
                "motor": motor,
                "exito": False,
                "mensaje": f"Motor no reconocido: {motor}"
            }

        return {
            "motor": motor,
            "exito": True,
            "df": df_opt,
            "valor_objetivo": valor,
            "mensaje": "Optimización exitosa"
        }

    except Exception as e:
        return {
            "motor": motor,
            "exito": False,
            "mensaje": str(e)
        }
