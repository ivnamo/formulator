# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import numpy as np
import pandas as pd
from scipy.optimize import linprog

def optimizar_simplex(df: pd.DataFrame, columnas_objetivo: list, restricciones_min: dict = None):
    """
    Optimiza los % de materias primas para minimizar el costo total usando Simplex (linprog).

    Args:
        df: DataFrame con columnas ['Materia Prima', 'Precio €/kg', columnas_objetivo...]
        columnas_objetivo: Lista de parámetros técnicos a optimizar.
        restricciones_min: Dict con mínimos. Ej: {"Ntotal": 3.0}

    Returns:
        df_resultado: DataFrame con columna "%" optimizada.
        costo_total: Costo mínimo logrado.
    """
    precios = df["Precio €/kg"].values
    n = len(precios)

    # Objetivo: minimizar suma(precio_i * x_i)
    c = precios.copy()

    # Restricción: suma de porcentajes = 100
    A_eq = [np.ones(n)]
    b_eq = [100]

    # Restricciones técnicas mínimas
    A_ub = []
    b_ub = []

    if restricciones_min:
        for param, valor in restricciones_min.items():
            if param in columnas_objetivo:
                coef = df[param].fillna(0).values / 100  # convertir a coeficiente
                A_ub.append(-coef)  # se convierte en -Ax ≤ -b para linprog
                b_ub.append(-valor)

    bounds = [(0, 100) for _ in range(n)]

    res = linprog(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")

    if not res.success:
        raise ValueError("Error en optimización Simplex: " + res.message)

    df_resultado = df.copy()
    df_resultado["%"] = res.x
    return df_resultado, res.fun
