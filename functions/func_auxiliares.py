import unicodedata
import json
import os
from datetime import datetime, timedelta
import pandas as pd

def eliminar_tildes(texto):
    return ''.join((c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'))

def definir_rutas_jsons():
    # Obtener la ruta al directorio actual del script
    directorio_jsons = os.path.abspath('jsons')
    #directorio_jsons = os.path.join(directorio_actual, 'jsons')
    rutas_jsons = {
        'Concep_Aclarativo_ingresos': os.path.join(directorio_jsons, 'Concep_Aclarativo_ingresos.json'),
        'Concep_Aclarativo_gastos': os.path.join(directorio_jsons, 'Concep_Aclarativo_gastos.json'),
        'Concep_Categoria_ingresos': os.path.join(directorio_jsons, 'Concep_Categoria_ingresos.json'),
        'Concep_Categoria_gastos': os.path.join(directorio_jsons, 'Concep_Categoria_gastos.json'),
        'Prev_ingresos_extraordinarios': os.path.join(directorio_jsons, 'Prev_ingresos_extraordinarios.json'),
        'Prev_gastos_extraordinarios': os.path.join(directorio_jsons, 'Prev_gastos_extraordinarios.json')
    }
    return rutas_jsons

def leer_json(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo_json:
        datos_json = json.load(archivo_json)
    return datos_json

def escribir_json(ruta_archivo, datos_json):
    with open(ruta_archivo, "w") as archivo_json:
        json.dump(datos_json, archivo_json, indent=2)

def concatenardf(df1, df2):
    '''
    Esta función recibe 2 df, los concatena y los ordena por fecha en orden ascendente
    :param df1: dataframe 1
    :param df2: dataframe 2
    :return: dataframe concatenado y ordenado por fecha
    '''
    df = pd.concat([df1, df2], axis = 0)
    #Se ordena por fecha
    df.sort_values(by = "Fecha", inplace = True, ascending = True)
    df.reset_index(inplace = True, drop = True)
    return df

def obtener_salario_ini(df):
    salario_ini = df['Saldo'][df['Fecha'] == min(df['Fecha'])].iloc[0]
    return salario_ini

def recalcular_saldo(df, salario_ini):
    '''
    Recalcula el saldo a partir de un importe inicial y un df
    :param df: dataframe
    :param salario_ini: salario inicial
    :return: dataframe con el saldo recalculado
    '''
    # Se recalcula el saldo
    df['Saldo'] = 0
    for i, fila in df.iterrows():
        if i == 0:
            df['Saldo'].iloc[i] = salario_ini
        else:
            df['Saldo'].iloc[i] = df['Saldo'].iloc[i - 1] + fila['Importe']
    return df

def crear_calendario_anual(df):
    #Se obtienen los valores iniciales de interés
    salario_ini = obtener_salario_ini(df)
    fecha_ini = min(df['Fecha'])
    anio = fecha_ini.year
    fecha_ini = datetime.strptime(f"{anio}-01-01", "%Y-%m-%d")
    fecha_fin = datetime.strptime(f"{anio}-12-31", "%Y-%m-%d")
    #Se crea una lista con todas las fechas entre el rango de inicio y fin
    rango_fechas = []
    fecha_actual = fecha_ini
    while fecha_actual <= fecha_fin:
        rango_fechas.append(fecha_actual)
        fecha_actual += timedelta(days = 1)
    #Se añaden todas las fechas en forma de filas en el df en caso de que no existan ya
    rango_fechas = pd.to_datetime(rango_fechas) #Aunque ya esta en formato fecha, se transforma a fecha de pandas para poder ser comparado
    temp_dic = dict.fromkeys(df.columns)
    #Se asigno una lista para cada valor de la clave
    for key in temp_dic.keys():
        temp_dic[key] = []
    #Itero entre todas las fechas en rango fechas para comprobar si está o no en el df
    for fecha in rango_fechas:
        if fecha not in df['Fecha'].values:
            for key, value in temp_dic.items():
                if key == 'Fecha':
                    temp_dic[key].append(fecha)
                elif key == 'Importe' or key == 'Saldo':
                    temp_dic[key].append(0)
                elif key == 'Concepto':
                    temp_dic[key].append('-')
                elif key == 'Tipo_Movimiento':
                    temp_dic[key].append('-')
                else:
                    temp_dic[key].append(None)
    #Se crea un dataframe con el diccionario
    temp_df = pd.DataFrame(temp_dic)
    #Se concatenan los df y se recalcula el saldo
    df = concatenardf(df, temp_df)
    df = recalcular_saldo(df, salario_ini)
    return df


