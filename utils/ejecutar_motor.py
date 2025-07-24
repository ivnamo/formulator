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
    modo: str,
    parametros_extra: dict = None
) -> dict:
    """
    Ejecuta un motor de optimización específico y devuelve un diccionario estandarizado.

    Args:
        motor: Nombre del motor a usar ("Simplex", "SLSQP", etc.)
        df: DataFrame con materias primas
        columnas_objetivo: Parámetros técnicos disponibles
        restricciones_min / max: Restricciones del problema
        variable_objetivo: Variable a minimizar o maximizar
        modo: "Minimizar" o "Maximizar"
        parametros_extra: Diccionario opcional con parámetros específicos por motor

    Returns:
        dict con claves:
            - 'motor': nombre del motor
            - 'exito': True/False
            - 'df': DataFrame resultado (si exito)
            - 'valor_objetivo': float (si exito)
            - 'mensaje': texto de error o éxito
    """
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
            params = parametros_extra.get("Genético", {}) if parametros_extra else {}
            df_opt, valor = optimizar_genetico(
                df, columnas_objetivo, restricciones_min, restricciones_max,
                variable_objetivo, modo,
                parametros=params
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

