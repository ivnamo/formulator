import pandas as pd

def cargar_datos(archivo):
    if archivo:
        df = pd.read_excel(archivo)
    else:
        df = pd.read_excel("materias_primas.xlsx")
    df["%"] = 0.0
    return df
