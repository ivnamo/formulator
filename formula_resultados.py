# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------


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

    # Asegurar que solo se usen columnas que existen realmente
    columnas_existentes = [col for col in columnas_composicion if col in df_filtrado.columns]

    # Inicializar columnas faltantes con 0.0 (opcional y seguro para filas nuevas)
    for col in columnas_existentes:
        df_filtrado[col] = (df_filtrado[col] * df_filtrado["%"]) / 100

    composicion = df_filtrado[columnas_existentes].sum().to_frame(name="Cantidad %")
    return precio_total, composicion
