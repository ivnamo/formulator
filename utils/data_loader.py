# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------


import pandas as pd
import unicodedata
from utils.supabase_client import supabase


def _normalize_label(value: str) -> str:
    """Normalize a column label for tolerant matching."""
    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.replace("€", "eur")
    text = "".join(ch for ch in text if ch.isalnum())
    return text


def _find_column(df: pd.DataFrame, candidates: list[str], required_parts: list[str] | None = None) -> str | None:
    """Find the best matching column among candidates or by required normalized parts."""
    normalized_to_original = {_normalize_label(col): col for col in df.columns}

    for candidate in candidates:
        col = normalized_to_original.get(_normalize_label(candidate))
        if col:
            return col

    if required_parts:
        for normalized, original in normalized_to_original.items():
            if all(part in normalized for part in required_parts):
                return original

    return None


def cargar_datos():
    """Carga todas las materias primas ordenadas alfabéticamente por nombre."""
    response = supabase.table("materias_primas").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        df["%"] = pd.Series(dtype="float64")
        return df

    # Map cloud/local variants to canonical labels expected by UI.
    nombre_col = _find_column(
        df,
        candidates=["Materia Prima", "materia_prima", "materia prima", "nombre"],
        required_parts=["materia", "prima"],
    )
    precio_col = _find_column(
        df,
        candidates=["Precio €/kg", "precio_eur_kg", "precio/kg", "precio"],
        required_parts=["precio", "kg"],
    )

    rename_map = {}
    if nombre_col and nombre_col != "Materia Prima":
        rename_map[nombre_col] = "Materia Prima"
    if precio_col and precio_col != "Precio €/kg":
        rename_map[precio_col] = "Precio €/kg"
    if rename_map:
        df = df.rename(columns=rename_map)

    if "Materia Prima" in df.columns:
        df = df.sort_values("Materia Prima", ascending=True, na_position="last")

    if "Precio €/kg" not in df.columns:
        df["Precio €/kg"] = 0.0

    df["%"] = 0.0
    return df

