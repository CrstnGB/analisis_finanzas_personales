import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

import pandas as pd

ruta = r'C:\Users\Cristian\Documents\6- Proyectos\2- Python\2-Analisis finanzas personales\Extractos Bancarios'
nombre_archivo1 = '01.01.2023-15.12.2023.xlsx'
nombre_archivo2 = '01.01.2023-15.12.2023 CREDITO.xlsx'
df1 = pd.read_excel(ruta + "/" + nombre_archivo1)
df2 = pd.read_excel(ruta + "/" + nombre_archivo2)

print(df1.columns)

print(df1[['Fecha valor']])