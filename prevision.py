import procesamiento_datos as process
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import functions.func_auxiliares as aux
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model


def procesar_datos():
    # 1- INGESTA Y PROCESADO INICIAL
    nombre_archivo = input("Ingresa el nombre del extracto usado para la previsión del balance (sin extensión): ")
    df = process.preprocesamiento(nombre_archivo = nombre_archivo)
    salario_ini_prev = aux.obtener_salario_ini(df)
    print(f'Salario inicial (extracto para previsión): {salario_ini_prev}')
    # 2- SEGREGACIÓN DE DATOS
    df_ingresos, df_gastos = process.separacion_ingresos_gastos(df)
    #3- AGRUPACION DE VARIABLES
    # 3.1- Agrupación de variables CONTINUAS
    df_ingresos, df_gastos = process.agrupacion_var_continuas(df_ingresos, df_gastos)
    #3.2- AGRUPACION DE VARIABLES CATEGÓRICAS
    df_ingresos, df_gastos = process.agrupacion_var_categoricas(df_ingresos, df_gastos)
    return df_ingresos, df_gastos, salario_ini_prev

def incluir_extraordinarios(df, df_extraordinarios):
    if len(df_extraordinarios) > 0:
        df_extraordinarios['Fecha'] = df_extraordinarios['Fecha'].apply(
            lambda fecha: datetime.strptime(fecha, '%Y-%m-%d'))
        # Se unen los df con los extraordinarios
        df = aux.concatenardf(df, df_extraordinarios)
        return df
    else:
        return df

def prevision():
    #Preprocesamiento de datos igual que para un análisis
    df_ingresos, df_gastos, salario_ini_prev = procesar_datos()

    #AHORA SE PROCESAN LOS DATOS PARA REALIZAR UNA PREVISION BASADO EN UNA REGRESIÓN LINEAL

    #1- Descartamos outliers; solo nos quedamos con los dos primero df de las listas
    #Se concatenan los dos df

    #Se va a crear una lista donde almacenar tantos df como grupos haya
    #Se crea la lista de dataframes
    list_df_rangos_gastos = process.obtener_df_rangos(df_gastos)
    list_df_rangos_ingresos = process.obtener_df_rangos(df_ingresos)

    #Se concatenan los dos primeros df de las listas
    if len(list_df_rangos_ingresos) > 1:
        df_ingresos = aux.concatenardf(list_df_rangos_ingresos[0], list_df_rangos_ingresos[1])

    if len(list_df_rangos_ingresos) > 1:
        df_gastos = aux.concatenardf(list_df_rangos_gastos[0], list_df_rangos_gastos[1])

    #Se incluyen los gastos e ingresos extraordinarios
    rutas_jsons = aux.definir_rutas_jsons()
    datos_json_ingresos = aux.leer_json(rutas_jsons['Prev_ingresos_extraordinarios'])
    datos_json_gastos = aux.leer_json(rutas_jsons['Prev_gastos_extraordinarios'])

    #Por el tipo de formato en el que vienen los datos del json (lista de diccionarios), hay que tratarlos para
    #pasarlos a dataframes
    for df_ingresos_extraordinarios in datos_json_ingresos:
        #Se pasa a formato DataFrame el json
        df_ingresos_extraordinarios = pd.DataFrame(df_ingresos_extraordinarios)
        # Se unen los df con los extraordinarios
        df_ingresos = incluir_extraordinarios(df_ingresos, df_ingresos_extraordinarios)

    for df_gastos_extraordinarios in datos_json_gastos:
        #Se pasa a formato DataFrame el json
        df_gastos_extraordinarios = pd.DataFrame(df_gastos_extraordinarios)
        # Se unen los df con los extraordinarios
        df_gastos = incluir_extraordinarios(df_gastos, df_gastos_extraordinarios)

    #Se inicializa la columna Saldo
    df_ingresos['Saldo'] = 0
    df_gastos['Saldo'] = 0

    #Se negativizan los importes de gastos
    df_gastos['Importe'] = df_gastos['Importe'].apply(lambda x: x * (-1))

    #Se concatenan los dos df
    df_transformado = aux.concatenardf(df_ingresos, df_gastos)

    #Se eliminan las columnas Rango_Importe y Tipo_Pago
    df_transformado = df_transformado.drop(['Rango_Importe', 'Tipo_Pago'], axis = 1)

    #Para homogeneizar la cantidad de datos con respecto al df del año en curso, se incluyen todos los dias del año
    df_transformado = aux.crear_calendario_anual(df_transformado)

    #Como cada día puede tener más de un registro, se agrupa por fecha
    serie_transformado = df_transformado.groupby('Fecha')['Importe'].sum()

    #Necesito un df, no una serie, para añadir el saldo
    df_transformado = pd.DataFrame({'Fecha': serie_transformado.index, 'Importe': serie_transformado.values})

    #Se añade la columna de saldo
    df_transformado['Saldo'] = 0

    #Se recalcula el saldo
    df_transformado = aux.recalcular_saldo(df_transformado, salario_ini_prev)

    #Se definen la variables de entrenamiento X e y
    X_train = df_transformado.index
    X_train = np.reshape(X_train, (-1, 1))
    y_train = df_transformado['Saldo']

    #Se genera el modelo de ML

    #Se define el grado del polinomio
    poli_reg = PolynomialFeatures(degree = 6)
    #Se transforman las características existentes en características de mayor grado
    X_poli = poli_reg.fit_transform(X_train)
    #Defino el algoritmo a entrenar
    model = linear_model.LinearRegression()
    #Entreno el modelo
    model.fit(X_poli, y_train)
    y_pred = model.predict(X_poli)
    #Se redimensionan a una sola dimensión
    X_train = np.reshape(X_train, (-1))
    y_pred = np.reshape(y_pred, (-1))
    #y_pred = pd.Series(y_pred)
    return X_train, y_train, y_pred, salario_ini_prev

#Ahora se pueden guardar la variables X_train e y_pred en un json para ser utilizado
#en las gráficas de análisis

if __name__ == '__main__':
    X_train, y_train, y_pred, _ = prevision()
    plt.plot(X_train, y_train, color = 'b')
    plt.plot(X_train, y_pred, color = 'r')
    plt.plot()
    plt.show()




