# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import pandas as pd
import numpy as np
from scipy.optimize import linprog


def optimizar_simplex(
    df: pd.DataFrame,
    columnas_objetivo: list,
    restricciones_min: dict = None,
    restricciones_max: dict = None,
    variable_objetivo: str = "Precio €/kg",
    modo: str = "Minimizar"
):
    """
    Optimiza los % de materias primas para minimizar o maximizar un objetivo
    usando Simplex moderno (HiGHS).

    Args:
        df: DataFrame con columnas ['Materia Prima', 'Precio €/kg', columnas_objetivo...]
        columnas_objetivo: Lista de parámetros técnicos disponibles.
        restricciones_min: Dict con mínimos. Ej: {"Ntotal": 3.0}
        restricciones_max: Dict con máximos. Ej: {"K2O": 5.0}
        variable_objetivo: Columna objetivo: 'Precio €/kg', nombre de parámetro técnico o materia prima.
        modo: 'Minimizar' o 'Maximizar'

    Returns:
        df_resultado: DataFrame con columna "%" optimizada.
        valor_objetivo: Valor obtenido para la función objetivo.
    """
    n = len(df)

    # Construcción de función objetivo
    if variable_objetivo == "Precio €/kg":
        c = df["Precio €/kg"].fillna(0).values
    elif variable_objetivo in columnas_objetivo:
        c = df[variable_objetivo].fillna(0).values
    elif variable_objetivo in df["Materia Prima"].values:
        c = (df["Materia Prima"] == variable_objetivo).astype(float).values
    else:
        raise ValueError(f"Variable objetivo no reconocida: {variable_objetivo}")

    if modo == "Maximizar":
        c = -c

    # Igualdad: suma de % debe ser 100
    A_eq = [np.ones(n)]
    b_eq = [100]

    # Desigualdades
    A_ub, b_ub = [], []

    if restricciones_min:
        for param, val in restricciones_min.items():
            if param in df.columns:
                coef = df[param].fillna(0).values / 100
                A_ub.append(-coef)
                b_ub.append(-val)

    if restricciones_max:
        for param, val in restricciones_max.items():
            if param in df.columns:
                coef = df[param].fillna(0).values / 100
                A_ub.append(coef)
                b_ub.append(val)

    bounds = [(0, 100) for _ in range(n)]

    res = linprog(
        c=c,
        A_eq=A_eq,
        b_eq=b_eq,
        A_ub=A_ub or None,
        b_ub=b_ub or None,
        bounds=bounds,
        method="highs"
    )

    if not res.success:
        raise ValueError("Error en optimización Simplex: " + res.message)

    df_resultado = df.copy()
    df_resultado["%"] = res.x.round(4)

    valor_objetivo = np.dot(c, res.x) / 100
    if modo == "Maximizar":
        valor_objetivo *= -1

    return df_resultado, valor_objetivo
