import pandas as pd

ruta = r'C:\Users\Cristian\Documents\6- Proyectos\2- Python\2-Analisis finanzas personales\Extractos Bancarios'
nombre_archivo1 = '01.01.2023-15.12.2023'
nombre_archivo2 = '01.01.2023-15.12.2023 CREDITO'
df1 = pd.read_excel(ruta + "/" + nombre_archivo1 + ".xlsx")
df2 = pd.read_excel(ruta + "/" + nombre_archivo2 + ".xlsx")

#Se coordinan las columnas del df con el df1
df2.drop('Concepto', inplace = True, axis = 1)
df2.rename(columns={'Fecha del movimiento': 'Fecha de la operación', 'Comercio': 'Concepto'}, inplace = True)
df2['Fecha valor'] = None
df2['Nro. Apunte'] = None
df2['Saldo'] = None

orden_col = ['Fecha de la operación', 'Fecha valor', 'Concepto', 'Importe', 'Saldo', 'Nro. Apunte']
#Se reordenan las columnas del df2
df2 = df2[orden_col]

#Se concatenan los dos df
df = pd.concat([df1, df2], axis = 0)

#Se eliminan los NAn de concepto
df.dropna(axis = 0, how='all', subset=['Concepto'], inplace = True)
#Se convierte la columna Fecha de la operación en formato fecha
df['Fecha de la operación'] = pd.to_datetime(df['Fecha de la operación'], format = 'mixed', dayfirst = True)
df = df.sort_values(by = 'Fecha de la operación', ascending = False)
#Se eliminan las filas de la tarjeta visa classic
df = df[df['Concepto'] != 'tarjeta visa classic']

#Se ordena por fecha
df['Fecha de la operación'] = pd.to_datetime(df['Fecha de la operación'], dayfirst = True)
df.sort_values(by = "Fecha de la operación", inplace = True)
df.reset_index(inplace = True, drop = True)

#Se recalcula el saldo
for i, fila in df.iterrows():
    if i == 0:
        pass
    else:
        df['Saldo'].iloc[i] = df['Saldo'].iloc[i - 1] + fila['Importe']

#Se ordena por fecha en el orden descendente (como estaba originalmente)
df.sort_values(by = "Fecha de la operación", inplace = True, ascending = False)
df.reset_index(inplace = True, drop = True)

#Exportar a excel
df.to_excel(ruta + "/" + nombre_archivo1 + ".comb" + ".xlsx", index = False)

print('Proceso ejecutado con éxito')