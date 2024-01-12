import pandas as pd
from functions.func_auxiliares import *
import numpy as np
import math
import os
import json

def preprocesamiento ():
    # 1- INGESTA Y PROCESADO INICIAL

    # 1.1- Importar datos
    ruta = r'C:\Users\Cristian\Documents\6- Proyectos\2- Python\2-Analisis finanzas personales\Extractos Bancarios'
    nombre_archivo = '01.01.2023-15.12.2023.comb.xlsx'
    df = pd.read_excel(ruta + "/" + nombre_archivo)

    # Se eliminan las tildes del dataframe para evitar errores de lectura
    # Función para eliminar tildes
    df['Concepto'] = df['Concepto'].apply(eliminar_tildes)

    # 1.2- Renombrar Columnas y borrar columnas
    df.rename(columns={"Fecha de la operación": "Fecha"}, inplace=True)
    # Se borra la columna "Fecha valor", ya que no aporta nada interesante al df
    df.drop(['Fecha valor', 'Nro. Apunte'], axis=1, inplace=True)

    # 1.3- Relacionar los tipos de datos en el dataset
    print(df.dtypes)
    # Se convierte la columna de Fecha en un tipo de dato Fecha y Concepto en Category
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
    df['Concepto'] = df['Concepto'].astype('category')
    # Se ordena el dataset por fecha
    df.sort_values(by="Fecha", inplace=True)
    df.reset_index(inplace=True, drop=True)
    # Al ordenar por fecha, puede que se haya mezclado el orden de los movimientos en un mismo día. Por ello,
    # se debe recalcular el saldo
    for i, fila in df.iterrows():
        if i == 0:
            pass
        else:
            df['Saldo'].iloc[i] = df['Saldo'].iloc[i - 1] + fila['Importe']

    return df

def separacion_ingresos_gastos(df):
    # 2- SEGREGACIÓN DE DATOS

    # 2.1- Separación de tablas
    '''Debido a la naturaleza del df y antes de continuar con el análisis, se va a dividir el df en dos df diferentes:
    1- df_ingresos: para todos los movimientos positivos
    2- df_gastos: para todos los movimientos negativos'''
    df_ingresos = df[df['Importe'] > 0]
    df_ingresos.reset_index(inplace=True, drop=True)
    df_gastos = df[df['Importe'] < 0]
    df_gastos.reset_index(inplace=True, drop=True)

    # Para cada una de estas tablas, se eliminará la columna "Saldo", ya que carece de sentido al ya no ser un continuo.
    df_ingresos.drop('Saldo', axis=1, inplace=True)
    df_gastos.drop('Saldo', axis=1, inplace=True)

    # todos los valores de importe de gastos se pasarán a positivo debido a que el signo menos ya carece de sentido al haberse separado
    df_gastos['Importe'] = df_gastos['Importe'].apply(lambda x: abs(x))

    return df_ingresos, df_gastos

#3- AGRUPACION DE VARIABLES
def agrupacion_var_continuas(df_ingresos, df_gastos):
    # 3.1- Agrupación de variables CONTINUAS
    '''Una manera muy sencilla de convertir variables continuas en otras categóricas es mediante el uso de cuartiles.
    Usando este concepto, se va a categorizar el importe de dos formas diferentes:
    1.   Rango_Importe
    2.   Nivel_Importe

    El rango se puede diferenciar con el uso de la discriminación de outliers de forma recurrente en varios bucles.

    Para el nivel, simplemente se dividirán los datos en deciles, quintiles, etc... dependiendo de la cantidad de datos que queden en los diferentes Rangos.
    '''

    '''Para llevar a cabo esta idea, se va a escribir una función que reciba al df y calcule los parámetros de un boxplot. 
    La idea es llamar de forma recurrente a esta función las veces definidas. De esta manera, se irá reduciendo la presencia 
    de outliers a medida que se van dejando fuera. Tras varios ciclos, apenas quedarán outliers o se habrán eliminado. 
    Así se podrá determinar lo habitual que es un gasto.
    '''

    def calcular_outliers(df):
        cuartiles = np.percentile(df['Importe'], [25, 50, 75])
        iqr = np.subtract(*np.percentile(df['Importe'], [75, 25]))

        '''En Python, el asterisco (*) se utiliza para desempaquetar los elementos de
        una secuencia (como una lista o tupla) y pasarlos como argumentos individuales
        a una función. En el contexto de tu pregunta, el asterisco está siendo utilizado
        para desempaquetar los resultados de la función percentile y pasarlos como
        argumentos a la función np.subtract.'''

        lim_sup_outliers = cuartiles[2] + 1.5 * iqr
        lim_inf_outliers = cuartiles[0] - 1.5 * iqr

        '''En los boxplot, los outliers se determinan como todo valor que está más
        allá de los bigotes. Los bigotes son las líneas que se determinan como el
        tercer cuartil + 1.5 veces el rango intercuartílico (Tercer cuartil menos el
        primer cuartil) y el primer cuartil -1.5 veces el rango intercuartílico.'''
        # Se cuentan cuántos valores son outliers de los que quedan

        cantidad_outliers_restantes = len(df['Importe'][(df['Importe'] >
                                                         lim_sup_outliers) | (df['Importe'] < lim_inf_outliers)])

        return cantidad_outliers_restantes, lim_sup_outliers, lim_inf_outliers

    '''Luego, se escribe otra función que define la frecuencia del rango de los importes. 
    Esta función va a devolver una lista con los índices de la tabla que, tras varios ciclos, ya carece de outliers.
    '''

    def definir_rango_importes(df):
        check = True
        while check == True:
            cantidad_outliers_restantes, lim_sup_outliers, lim_inf_outliers = calcular_outliers(df)
            df = df[(df['Importe'] <= lim_sup_outliers) & (df['Importe'] >= lim_inf_outliers)]
            check = False if cantidad_outliers_restantes == 0 else None
        return df.index.to_list()

    '''Por último, se llaman a las funciones pertinentes hasta que todo el dataset en la columna Rango_Importe esté rellena. 
    La idea es que los datos más comunes estén escritos como 1, y los menos comunes en adelante 
    (cuanto mayor sea el número menos común).
    '''

    # GASTOS
    df_gastos['Rango_Importe'] = None  # Creo una nueva columna
    cant_datos_no_escritos = 1
    i = 1
    while cant_datos_no_escritos > 0:
        indices_datos_normales = definir_rango_importes(df_gastos[df_gastos['Rango_Importe'].isna()])
        df_gastos['Rango_Importe'].iloc[indices_datos_normales] = i
        i += 1
        cant_datos_no_escritos = len(df_gastos['Rango_Importe'][df_gastos['Rango_Importe'].isna()])

    '''Estos grupos van a ser objeto de estudio por separado. De esta manera, ningún grupo afecta al otro teniendo 
    sentido calcular otros parámetros
    '''
    # Se identifican los distintos rangos y se guardan en una lista
    rangos_importes = list(df_gastos['Rango_Importe'].unique())

    for i in rangos_importes:
        df_gastos['Rango_Importe'][df_gastos[
                                       'Rango_Importe'] == i] = f"[{math.floor(min(df_gastos['Importe'][df_gastos['Rango_Importe'] == i]))}, {math.floor(max(df_gastos['Importe'][df_gastos['Rango_Importe'] == i]))}]"

    # INGRESOS
    df_ingresos['Rango_Importe'] = None  # Creo una nueva columna
    cant_datos_no_escritos = 1
    i = 1
    while cant_datos_no_escritos > 0:
        indices_datos_normales = definir_rango_importes(df_ingresos[df_ingresos['Rango_Importe'].isna()])
        df_ingresos['Rango_Importe'].iloc[indices_datos_normales] = i
        i += 1
        cant_datos_no_escritos = len(df_ingresos['Rango_Importe'][df_ingresos['Rango_Importe'].isna()])

    # Se identifican los distintos rangos y se guardan en una lista
    rangos_importes = list(df_ingresos['Rango_Importe'].unique())

    for i in rangos_importes:
        df_ingresos['Rango_Importe'][df_ingresos[
                                         'Rango_Importe'] == i] = f"[{math.floor(min(df_ingresos['Importe'][df_ingresos['Rango_Importe'] == i]))}, {math.floor(max(df_ingresos['Importe'][df_ingresos['Rango_Importe'] == i]))}]"

    return df_ingresos, df_gastos

def obtener_df_rangos(df):
    #Se identifican los distintos rangos y se guardan en una lista
    rangos_importes = list(df['Rango_Importe'].unique())
    list_df_rangos = [df[df['Rango_Importe'].apply(lambda x: x == rango)] for rango in rangos_importes]
    # Se resetean los index
    for _df in list_df_rangos:
        _df.reset_index(inplace=True, drop=True)
    return list_df_rangos

def agrupacion_var_categoricas(df_ingresos, df_gastos):
    # 3.2- AGRUPACION DE VARIABLES CATEGÓRICAS
    # INGRESOS
    '''Se puede crear unas categorizaciones superiores según:

    Tipo de pago (Tipo_Pago)
    1.   Bizum
    2.  Transferencia
    '''
    # Se crea la columna Tipo_Pago
    df_ingresos['Tipo_Pago'] = None
    # Se determinan los bizum
    df_ingresos.loc[df_ingresos['Concepto'].str.contains('bizum'), 'Tipo_Pago'] = 'Bizum'
    # Por descarte, el resto son transferencias
    df_ingresos['Tipo_Pago'][df_ingresos['Tipo_Pago'].isna()] = 'Transferencia'

    '''Se van a crear unas categorías superiores para una mayor agrupación de conceptos. 
    Esto es un trabajo muy personal porque dependerá en gran medida del dueño del dataset. 
    La cantidad y el detalle que se quiera alcanzar dependerá será una decisión personal. 
    Sin embargo, se aconseja, al menos, categorizar el top 20 de los gastos comunes.

    Se crearán dos nuevas columnas:
    1. Concep_Aclarativo: se unificarán ciertos conceptos para un mayor entendimiento a la hora de leer la información 
    en los gráficos. Ej: un concepto puede ser Petroprix, pero esto puede se mayormente entendido como Gasolina o 
    Gasolinera. 
    2. Concep_Categoria: se unificarán conceptos según el criterio del usuario. Por ejemplo, la Gasolina puede estar
    junto con reparaciones de taller  y con prestamo del coche bajo la categoría de Transporte.

    Estos conceptos aclarativos y clasificaciones se almacenarán dentro de unos archivos json para poder gestionarlos
    independientemente de este código.

    Como esto es un trabajo personal del usuario, se escribirá un código como asistente para ayudar al usuario a 
    categorizar todo aquello que no lo esté hasta el momento y que sea importante debido a su alto importe.
    '''
    df_ingresos['Concep_Aclarativo'] = None
    df_ingresos['Concep_Categoria'] = None
    df_gastos['Concep_Aclarativo'] = None
    df_gastos['Concep_Categoria'] = None

    def obtener_clasificaciones(df, tipo):
        # Asignaciones de concepto aclarativo
        # Obtener la ruta al directorio actual del script
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        nuevas_columnas = ['Concep_Aclarativo', 'Concep_Categoria']
        for columna in nuevas_columnas:
            # Construir la ruta al archivo dentro de la carpeta relativa
            ruta_archivo = os.path.join(directorio_actual, 'jsons', f'{columna}_{tipo}.json')
            # Leer el archivo JSON
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo_json:
                datos_json = json.load(archivo_json)

            # Se escribe sobre la nueva columna accediendo al json
            for clave, valor in datos_json.items():
                valor = '|'.join(valor)
                if columna == nuevas_columnas[0]:
                    df.loc[df['Concepto'].str.contains(valor, case=False), columna] = clave
                else:
                    df.loc[df[nuevas_columnas[0]].str.contains(valor, case=False), columna] = clave

            df.loc[df[columna].isna(), columna] = 'Otros'
        return df

    # Asignaciones de la clasificación para ingresos
    df_ingresos = obtener_clasificaciones(df_ingresos, 'ingresos')

    # GASTOS
    '''Claramente, tal y como ocurre con df_ingresos, se puede dividir claramente en Tipo_Pago. Sin embargo, los Tipo_Concepto son más variados y hay que tratarlos de forma diferente.

    Tipo de pago (Tipo_Pago)
    1.   Tarjeta débito
    2.  Transferencia
    3. Tarjeta crédito
    4. Bizum
    5. Recibo
    6. Cuota'''

    # Se crea la columna Tipo_Pago
    df_gastos['Tipo_Pago'] = None

    df_gastos.loc[df_gastos['Concepto'].str.contains('tj-'), 'Tipo_Pago'] = 'Tarjeta Débito'
    df_gastos.loc[df_gastos['Concepto'].str.contains('cargo bizum - '), 'Tipo_Pago'] = 'Bizum'
    df_gastos.loc[df_gastos['Concepto'].str.contains('trf. '), 'Tipo_Pago'] = 'Transferencia'
    df_gastos.loc[df_gastos['Concepto'].str.contains('rcbo.'), 'Tipo_Pago'] = 'Recibo'
    df_gastos.loc[df_gastos['Concepto'].str.contains('cuota '), 'Tipo_Pago'] = 'Cuota'
    df_gastos.loc[df_gastos['Concepto'].str.contains('adeudo '), 'Tipo_Pago'] = 'Adeudo'
    df_gastos.loc[df_gastos['Concepto'].str.contains('tarjeta visa classic'), 'Tipo_Pago'] = 'Tarjeta Crédito'

    # Después de esta categorización, si queda alguno no categorizado lo más probable es porque sean los de la tarjeta de crédito
    df_gastos['Tipo_Pago'][df_gastos['Tipo_Pago'].isna()] = 'Tarjeta Crédito'

    # Una vez está todo categorizado en Tipo_Pago,
    # se procede a la normalización del concepto antes de estudiar la categorización como Tipo_Concepto
    df_gastos['Concepto'] = df_gastos['Concepto'].str.replace('tj-', '')
    df_gastos['Concepto'] = df_gastos['Concepto'].str.replace('cargo bizum - ', '')
    df_gastos['Concepto'] = df_gastos['Concepto'].str.replace('trf. ', '')
    df_gastos['Concepto'] = df_gastos['Concepto'].str.replace('rcbo.', '')
    df_gastos['Concepto'] = df_gastos['Concepto'].str.replace('cuota ', '')
    df_gastos['Concepto'] = df_gastos['Concepto'].str.replace('adeudo ', '')

    '''Se van a crear unas categorías superiores para una mayor agrupación de conceptos. 
    Esto es un trabajo muy personal porque dependerá en gran medida del dueño del dataset. 
    La cantidad y el detalle que se quiera alcanzar dependerá será una decisión personal. 
    Sin embargo, se aconseja, al menos, categorizar el top 20 de los gastos comunes.'''

    # Asignaciones de la clasificación para ingresos
    df_gastos = obtener_clasificaciones(df_gastos, 'gastos')

    return df_ingresos, df_gastos