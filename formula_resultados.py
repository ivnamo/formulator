# formula_resultados.py

import pandas as pd

def calcular_resultado_formula(df_editado, columnas_composicion):
    """
    Calcula el precio y la composición técnica de la fórmula.

    Args:
        df_editado (pd.DataFrame): Materias primas con columnas 'Precio €/kg', '%', y parámetros técnicos.
        columnas_composicion (list): Columnas técnicas a considerar (N, P, MO...).

    Returns:
        float: Precio total de la fórmula
        pd.DataFrame: Composición total (solo columnas seleccionadas)
    """
    df_filtrado = df_editado[df_editado["%"] > 0].copy()
    df_filtrado["Subtotal"] = (df_filtrado["Precio €/kg"] * df_filtrado["%"]) / 100
    precio_total = df_filtrado["Subtotal"].sum()

    for col in columnas_composicion:
        if col in df_filtrado.columns:
            df_filtrado[col] = (df_filtrado[col] * df_filtrado["%"]) / 100

    composicion = df_filtrado[columnas_composicion].sum().to_frame(name="Cantidad %")
    return precio_total, composicion
