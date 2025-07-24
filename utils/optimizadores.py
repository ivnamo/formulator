# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import pandas as pd
import numpy as np
from scipy.optimize import linprog, minimize
from deap import base, creator, tools, algorithms
import random

def optimizar_genetico(
    df,
    columnas_objetivo,
    restricciones_min,
    restricciones_max,
    variable_objetivo,
    modo,
    parametros: dict = None
):
    n = len(df)

    # Coeficiente de la función objetivo
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

    # Leer parámetros con valores por defecto
    n_ind = parametros.get("n_individuos", 50) if parametros else 50
    n_gen = parametros.get("n_generaciones", 100) if parametros else 100
    cxpb = parametros.get("cxpb", 0.7) if parametros else 0.7
    mutpb = parametros.get("mutpb", 0.2) if parametros else 0.2

    # Evaluación con penalización
    def eval_ind(ind):
        x = np.array(ind)
        penalty = abs(np.sum(x) - 100) * 1000

        for param, val in (restricciones_min or {}).items():
            if param in df.columns:
                c = df[param].fillna(0).values / 100
                penalty += max(0, val - np.dot(c, x)) * 1000

        for param, val in (restricciones_max or {}).items():
            if param in df.columns:
                c = df[param].fillna(0).values / 100
                penalty += max(0, np.dot(c, x) - val) * 1000

        score = np.dot(coef_obj, x) / 100 + penalty
        return (score,)

    # Evitar error si ya existe el creator
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attr", lambda: random.uniform(0, 100))
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr, n)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", eval_ind)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=10, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=n_ind)
    algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=n_gen, verbose=False)

    best = tools.selBest(pop, 1)[0]
    df_resultado = df.copy()
    df_resultado["%"] = np.array(best).round(4)

    valor = np.dot(coef_obj, best) / 100
    if modo == "Maximizar":
        valor *= -1

    return df_resultado, valor



def optimizar_cobyla(df, columnas_objetivo, restricciones_min, restricciones_max, variable_objetivo, modo):
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

    constraints = []

    # Aproximar suma 100% como doble desigualdad
    constraints.append({"type": "ineq", "fun": lambda x: 100.1 - np.sum(x)})
    constraints.append({"type": "ineq", "fun": lambda x: np.sum(x) - 99.9})

    if restricciones_min:
        for param, val in restricciones_min.items():
            if param in df.columns:
                coef = df[param].fillna(0).values / 100
                constraints.append({"type": "ineq", "fun": lambda x, c=coef, v=val: np.dot(c, x) - v})

    if restricciones_max:
        for param, val in restricciones_max.items():
            if param in df.columns:
                coef = df[param].fillna(0).values / 100
                constraints.append({"type": "ineq", "fun": lambda x, c=coef, v=val: v - np.dot(c, x)})

    x0 = np.full(n, 100 / n)
    bounds = [(0, 100)] * n

    res = minimize(fun_obj, x0, method="COBYLA", constraints=constraints)

    if not res.success:
        raise ValueError("COBYLA: " + res.message)

    df_resultado = df.copy()
    df_resultado["%"] = res.x.round(4)
    valor = np.dot(coef_obj, res.x) / 100
    if modo == "Maximizar":
        valor *= -1

    return df_resultado, valor

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
