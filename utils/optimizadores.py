# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import pandas as pd
import numpy as np
from scipy.optimize import linprog, minimize


def optimizar_simplex(
    df: pd.DataFrame,
    columnas_objetivo: list,
    restricciones_min: dict = None,
    restricciones_max: dict = None,
    variable_objetivo: str = "Precio €/kg",
    modo: str = "Minimizar"
):
    """
    Optimiza usando método Simplex moderno (HiGHS).
    """
    n = len(df)

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

    A_eq = [np.ones(n)]
    b_eq = [100]

    A_ub = []
    b_ub = []

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
        raise ValueError("Simplex: " + res.message)

    df_resultado = df.copy()
    df_resultado["%"] = res.x.round(4)

    valor_objetivo = np.dot(c, res.x) / 100
    if modo == "Maximizar":
        valor_objetivo *= -1

    return df_resultado, valor_objetivo


def optimizar_slsqp(
    df: pd.DataFrame,
    columnas_objetivo: list,
    restricciones_min: dict = None,
    restricciones_max: dict = None,
    variable_objetivo: str = "Precio €/kg",
    modo: str = "Minimizar"
):
    """
    Optimiza usando SLSQP (Sequential Least Squares Programming).
    """
    n = len(df)

    if variable_objetivo == "Precio €/kg":
        coef_obj = df["Precio €/kg"].fillna(0).values
    elif variable_objetivo in columnas_objetivo:
        coef_obj = df[variable_objetivo].fillna(0).values
    elif variable_objetivo in df["Materia Prima"].values:
        coef_obj = (df["Materia Prima"] == variable_objetivo).astype(float).values
    else:
        raise ValueError(f"Variable objetivo no reconocida: {variable_objetivo}")

    if modo == "Maximizar":
        coef_obj = -coef_obj

    def fun_obj(x):
        return np.dot(coef_obj, x)

    constraints = [{
        "type": "eq",
        "fun": lambda x: np.sum(x) - 100
    }]

    if restricciones_min:
        for param, val in restricciones_min.items():
            if param in df.columns:
                coef = df[param].fillna(0).values / 100
                constraints.append({
                    "type": "ineq",
                    "fun": lambda x, c=coef, v=val: np.dot(c, x) - v
                })

    if restricciones_max:
        for param, val in restricciones_max.items():
            if param in df.columns:
                coef = df[param].fillna(0).values / 100
                constraints.append({
                    "type": "ineq",
                    "fun": lambda x, c=coef, v=val: v - np.dot(c, x)
                })

    bounds = [(0, 100) for _ in range(n)]
    x0 = np.full(n, 100 / n)

    res = minimize(fun_obj, x0, method='SLSQP', bounds=bounds, constraints=constraints)

    if not res.success:
        raise ValueError("SLSQP: " + res.message)

    df_resultado = df.copy()
    df_resultado["%"] = res.x.round(4)

    valor_objetivo = np.dot(coef_obj, res.x) / 100
    if modo == "Maximizar":
        valor_objetivo *= -1

    return df_resultado, valor_objetivo
