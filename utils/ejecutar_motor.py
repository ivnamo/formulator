# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------
import pandas as pd
from utils.optimizadores import optimizar_simplex, optimizar_slsqp

def ejecutar_motor(
    motor: str,
    df: pd.DataFrame,
    columnas_objetivo: list,
    restricciones_min: dict,
    restricciones_max: dict,
    variable_objetivo: str,
    modo: str
) -> dict:
    """
    Ejecuta un motor de optimización específico y devuelve un diccionario estandarizado.

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
