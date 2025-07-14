# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

def optimizar_simplex(df: pd.DataFrame, columnas_objetivo: list, restricciones_min: dict = None, restricciones_max: dict = None):
    """
    Optimiza los % de materias primas para minimizar el costo total usando Simplex moderno (linprog con highs).

    Args:
        df: DataFrame con columnas ['Materia Prima', 'Precio €/kg', columnas_objetivo...]
        columnas_objetivo: Lista de parámetros técnicos a optimizar.
        restricciones_min: Dict con mínimos. Ej: {"Ntotal": 3.0}
        restricciones_max: Dict con máximos. Ej: {"K2O": 5.0}

    Returns:
        df_resultado: DataFrame con columna "%" optimizada.
        costo_total: Costo mínimo logrado (€/kg).
    """
    precios = df["Precio €/kg"].fillna(0).values
    n = len(precios)

    c = precios
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

    res = linprog(c=c, A_ub=A_ub or None, b_ub=b_ub or None,
                  A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")

    if not res.success:
        raise ValueError("Error en optimización Simplex: " + res.message)

    df_resultado = df.copy()
    df_resultado["%"] = res.x.round(4)
    costo_total = np.dot(precios, res.x) / 100

    return df_resultado, costo_total
