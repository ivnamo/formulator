import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.writer.excel import save_virtual_workbook
from io import BytesIO

def exportar_formula_excel(df: pd.DataFrame, nombre_formula: str) -> BytesIO:
    """
    Exporta una fórmula a un archivo Excel con fórmulas automáticas de precio y composición.

    Args:
        df (pd.DataFrame): Fórmula con columnas 'Materia Prima', 'Precio €/kg', '%', y parámetros técnicos.
        nombre_formula (str): Nombre de la fórmula para identificar el archivo.

    Returns:
        BytesIO: Archivo Excel listo para descarga.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Fórmula"

    # Escribir encabezados
    columnas = df.columns.tolist()
    columnas += ["Subtotal €/kg"]
    ws.append(columnas)

    for i, row in enumerate(df.itertuples(index=False), start=2):
        values = list(row)
        # Fórmula subtotal: =Precio * % / 100
        precio = row._asdict().get("Precio €/kg", 0)
        pct = row._asdict().get("%", 0)
        col_precio = columnas.index("Precio €/kg") + 1
        col_pct = columnas.index("%") + 1
        formula_subtotal = f"=C{i}*D{i}/100"
        ws.append(values + [formula_subtotal])

    fila_total = len(df) + 2
    ws[f"A{fila_total}"] = "TOTAL €/kg:"
    col_subtotal = columnas.index("Subtotal €/kg") + 1
    ws[f"{chr(64 + col_subtotal)}{fila_total}"] = f"=SUM({chr(64 + col_subtotal)}2:{chr(64 + col_subtotal)}{fila_total - 1})"

    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max(max_length + 2, 10)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output
