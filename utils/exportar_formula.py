# ------------------------------------------------------------------------------
# FORMULATOR – Uso exclusivo de Iván Navarro
# Todos los derechos reservados © 2025
# Este archivo forma parte de un software no libre y no está autorizado su uso
# ni distribución sin consentimiento expreso y por escrito del autor.
# ------------------------------------------------------------------------------

import pandas as pd
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from io import BytesIO

def exportar_formula_excel(df: pd.DataFrame, nombre_formula: str) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Fórmula"

    # Mantener solo columnas útiles
    columnas_base = ["Materia Prima", "%", "Precio €/kg"]
    columnas_tecnicas = [col for col in df.columns if col not in columnas_base and col != "id"]
    columnas_final = columnas_base + columnas_tecnicas

    # Calcular valores ajustados al %
    df_export = df[columnas_base].copy()
    for col in columnas_tecnicas:
        df_export[col] = df[col] * df["%"] / 100

    # Escribir encabezados
    for col_idx, col_name in enumerate(columnas_final, start=1):
        ws.cell(row=1, column=col_idx, value=col_name)

    # Escribir datos sin totales ni fórmulas
    for row_idx, row in enumerate(df_export.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max(max_len + 2, 10)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

