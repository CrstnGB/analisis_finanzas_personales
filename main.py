import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import scipy as sp
import math
from datetime import datetime
from functions.func_charts import *
import json
import os
from functions.func_auxiliares import *


# 0-PreConfiguración para las gráficas

#Creo un objeto PdfPages para almacenar las figuras en un archivo PDF

with PdfPages('prueba.pdf') as pdf:

    # 0.1- Configurar parámetros de gráficas

    altofig = 13
    anchofig = altofig * (2 ** (1/2))
    anchofig = 30
    plt.rcParams['figure.figsize'] = (anchofig, altofig)   #estas son las medidas en pulgadas de un A3
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 12
    plt.style.use('ggplot')

    # 0.2- Crear la figura1 y un objeto GridSpec
    fig1 = plt.figure()
    ax1 = plt.subplot()
    ax1.axis('off')
    ax1.set_title('EVOLUCIÓN Y COMPARACION INGRESOS VS GASTOS', y=1.08, fontsize = 20)
    gs1_1 = GridSpec(1, 2, height_ratios=[1], width_ratios=[3, 1])

    # 0.3- Crear subgráficas de la figura 1 usando las posiciones definidas por GridSpec
    ax1_1 = plt.subplot(gs1_1[0, 0])
    ax1_1.axis('off')
    ax1_1.set_ylabel('€')
    ax1_1.text(-0.1, 0.5, '€', rotation = 'vertical', ha = 'center', va = 'center', weight = 'bold', fontsize = 20)
    ax1_2 = plt.subplot(gs1_1[0, 1])
    ax1_2.axis('off')

    # 0.4- Añadir una cuadrículas internas
    gs_1_1_1 = GridSpecFromSubplotSpec(4, 1, subplot_spec=gs1_1[0, 0], height_ratios=[1, 1, 1, 1], width_ratios=[1])
    ax1_1_1 = plt.subplot(gs_1_1_1[0, 0])
    ax1_1_2 = plt.subplot(gs_1_1_1[1, 0])
    ax1_1_3 = plt.subplot(gs_1_1_1[2, 0])
    ax1_1_4 = plt.subplot(gs_1_1_1[3, 0])

    # 0.5- Añadir una cuadrículas internas
    gs_1_1_2 = GridSpecFromSubplotSpec(3, 1, subplot_spec=gs1_1[0, 1], height_ratios=[2, 2, 1], width_ratios=[1])
    ax1_2_1 = plt.subplot(gs_1_1_2[0, 0])
    ax1_2_1.axis('off')
    ax1_2_2 = plt.subplot(gs_1_1_2[1, 0])
    ax1_2_2.axis('off')
    ax1_2_3 = plt.subplot(gs_1_1_2[2, 0])
    ax1_2_3.axis('off')
    plt.subplots_adjust(hspace=0.5)

    #Se crea la figura 2 y su gridspec
    fig2 = plt.figure()
    ax2 = plt.subplot()
    ax2.axis('off')
    ax2.set_title('REPARTO DE INGRESOS Y GASTOS POR CONCEPTO Y CATEGORÍA', y=1.08, fontsize = 20)
    gs2_1 = GridSpec(2, 2, height_ratios=[2,1], width_ratios=[1, 1])
    ax2_1 = plt.subplot(gs2_1[0, 0])
    ax2_2 = plt.subplot(gs2_1[0, 1])
    ax2_3 = plt.subplot(gs2_1[1, 0])
    ax2_4 = plt.subplot(gs2_1[1, 1])
    plt.subplots_adjust(hspace = 0.1)

    # 0.6- Personalizar los títulos subgráficas
    #ax1_1.set_title('EVOLUCIÓN Y COMPARACION INGRESOS VS GASTOS', y = 1.03)
    #ax1_2.set_title('DISTRIBUCIÓN INGRESOS Y GASTOS', y = 1.03)

    # 0.7- Preparar colores a usar generales
    colores_I_G = ['#196F3D', '#E74C3C']

    #1- INGESTA Y PROCESADO INICIAL

    # 1.1- Importar datos
    ruta = r'C:\Users\Cristian\Documents\6- Proyectos\2- Python\2-Analisis finanzas personales\Extractos Bancarios'
    nombre_archivo = '01.01.2023-15.12.2023.comb.xlsx'
    df = pd.read_excel(ruta + "/" + nombre_archivo)

    #Se eliminan las tildes del dataframe para evitar errores de lectura
    # Función para eliminar tildes
    df['Concepto'] = df['Concepto'].apply(eliminar_tildes)

    # 1.2- Renombrar Columnas y borrar columnas
    df.rename(columns={"Fecha de la operación": "Fecha"}, inplace = True)
    #Se borra la columna "Fecha valor", ya que no aporta nada interesante al df
    df.drop(['Fecha valor', 'Nro. Apunte'], axis = 1, inplace = True)

    # 1.3- Relacionar los tipos de datos en el dataset
    print(df.dtypes)
    #Se convierte la columna de Fecha en un tipo de dato Fecha y Concepto en Category
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst = True)
    df['Concepto'] = df['Concepto'].astype('category')
    #Se ordena el dataset por fecha
    df.sort_values(by = "Fecha", inplace = True)
    df.reset_index(inplace = True, drop = True)
    #Al ordenar por fecha, puede que se haya mezclado el orden de los movimientos en un mismo día. Por ello, se debe recalcular el saldo
    for i, fila in df.iterrows():
        if i == 0:
            pass
        else:
            df['Saldo'].iloc[i] = df['Saldo'].iloc[i - 1] + fila['Importe']

    print(df.head(10))

    #GRAFICADO
    salary_tracing(df, ax1_1_1)


    #2- DIAGNÓSTICO DE CALIDAD DE LOS DATOS

    #2.1- Separación de tablas
    '''Debido a la naturaleza del df y antes de continuar con el análisis, se va a dividir el df en dos df diferentes:
    1- df_ingresos: para todos los movimientos positivos
    2- df_gastos: para todos los movimientos negativos'''
    df_ingresos = df[df['Importe'] > 0]
    df_ingresos.reset_index(inplace = True, drop = True)
    df_gastos = df[df['Importe'] < 0]
    df_gastos.reset_index(inplace = True, drop = True)

    #Para cada una de estas tablas, se eliminará la columna "Saldo", ya que carece de sentido al ya no ser un continuo.
    df_ingresos.drop('Saldo', axis=1, inplace=True)
    df_gastos.drop('Saldo', axis=1, inplace=True)

    #todos los valores de importe de gastos se pasarán a positivo debido a que el signo menos ya carece de sentido al haberse separado
    df_gastos['Importe'] = df_gastos['Importe'].apply(lambda x: abs(x))

    #GRAFICADO
    acum_comparison(df_ingresos, df_gastos, ax1_1_2)
    monthly_comparison(df_ingresos, df_gastos, ax1_1_4)
    yearly_comparison(df_ingresos, df_gastos, ax1_2_3)

    #3- AGRUPACION DE VARIABLES

    #3.1- Agrupación de variables CONTINUAS
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
      #Se cuentan cuántos valores son outliers de los que quedan

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

    #GASTOS
    df_gastos['Rango_Importe'] = None #Creo una nueva columna
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
    #Se identifican los distintos rangos y se guardan en una lista
    rangos_importes = list(df_gastos['Rango_Importe'].unique())

    for i in rangos_importes:
        df_gastos['Rango_Importe'][df_gastos['Rango_Importe'] == i] = f"[{math.floor(min(df_gastos['Importe'][df_gastos['Rango_Importe'] == i]))}, {math.floor(max(df_gastos['Importe'][df_gastos['Rango_Importe'] == i]))}]"

    #INGRESOS
    df_ingresos['Rango_Importe'] = None #Creo una nueva columna
    cant_datos_no_escritos = 1
    i = 1
    while cant_datos_no_escritos > 0:
      indices_datos_normales = definir_rango_importes(df_ingresos[df_ingresos['Rango_Importe'].isna()])
      df_ingresos['Rango_Importe'].iloc[indices_datos_normales] = i
      i += 1
      cant_datos_no_escritos = len(df_ingresos['Rango_Importe'][df_ingresos['Rango_Importe'].isna()])

    #Se identifican los distintos rangos y se guardan en una lista
    rangos_importes = list(df_ingresos['Rango_Importe'].unique())

    for i in rangos_importes:
        df_ingresos['Rango_Importe'][df_ingresos['Rango_Importe'] == i] = f"[{math.floor(min(df_ingresos['Importe'][df_ingresos['Rango_Importe'] == i]))}, {math.floor(max(df_ingresos['Importe'][df_ingresos['Rango_Importe'] == i]))}]"


    #GRAFICADO
    #INGRESOS
    filtro = df_ingresos.groupby('Rango_Importe')['Importe'].sum().sort_values(ascending = False)
    etiquetas = list(filtro.index)
    valores = list(filtro.values)
    unidad = '€'
    title = f'% por Rango - Ingresos'
    pie_chart(ax1_2_1, valores, etiquetas, title, unidad, colormap_verdes)

    #GASTOS
    filtro = df_gastos.groupby('Rango_Importe')['Importe'].sum().sort_values(ascending = False)
    etiquetas = list(filtro.index)
    valores = list(filtro.values)
    unidad = '€'
    title = f'% por Rango - Gastos'
    pie_chart(ax1_2_2, valores, etiquetas, title, unidad, colormap_rojos)

    #Ahora se pueden ver las distribuciones de importes pero mostrando los rangos de outliers

    #Se va a crear una lista donde almacenar tantos df como grupos haya.
    def obtener_df_rangos(df):
        #Se identifican los distintos rangos y se guardan en una lista
        rangos_importes = list(df['Rango_Importe'].unique())
        list_df_rangos = [df[df['Rango_Importe'].apply(lambda x: x == rango)] for rango in rangos_importes]
        return list_df_rangos

    #Se crea la lista de dataframes
    list_df_rangos_gastos = obtener_df_rangos(df_gastos)
    list_df_rangos_ingresos = obtener_df_rangos(df_ingresos)

    #Se resetean los index
    for _df in list_df_rangos_gastos:
        _df.reset_index(inplace = True, drop = True)

    for _df in list_df_rangos_ingresos:
        _df.reset_index(inplace = True, drop = True)

    #Se extraen los datos y se pintan las gráficas
    etiquetas = df['Fecha']
    valores = df['Importe']
    ax1_1_3.plot(etiquetas, valores, color = '#283747')
    #Pintar lineas de ouliers
    check_label_gastos = False
    check_label_ingresos = False

    for i, _df in enumerate(list_df_rangos_gastos):
        # Se definen los colores
        colormap = plt.get_cmap('Reds')
        num_colores = len(list_df_rangos_gastos)
        color_min = 0.2
        color_max = 0.7
        colores = colormap(np.linspace(color_min, color_max, num_colores))

        valor_outlier_alto = max(_df['Importe']) * (-1)
        valor_outlier_bajo = min(_df['Importe']) * (-1)
        ax1_1_3.axhspan(valor_outlier_bajo, valor_outlier_alto, facecolor=colores[i], alpha=0.3, label=f"[{math.ceil(valor_outlier_bajo)},{math.ceil(valor_outlier_alto)}]")
        ax1_1_3.axhline(y = valor_outlier_alto, color = colores[i], linestyle = '--', linewidth = 0.7)
        ax1_1_3.axhline(y=valor_outlier_bajo, color=colores[i], linestyle='--', linewidth=0.7)


    for _df in list_df_rangos_ingresos:
        # Se definen los colores
        colormap = plt.get_cmap('Greens')
        num_colores = len(list_df_rangos_gastos)
        color_min = 0.2
        color_max = 0.7
        colores = colormap(np.linspace(color_min, color_max, num_colores))

        valor_outlier_alto = max(_df['Importe'])
        valor_outlier_bajo = min(_df['Importe'])
        ax1_1_3.axhspan(valor_outlier_bajo, valor_outlier_alto, facecolor=colores[i], alpha=0.3, label=f"[{math.floor(valor_outlier_bajo)},{math.floor(valor_outlier_alto)}]")
        ax1_1_3.axhline(y=valor_outlier_alto, color=colores[i], linestyle='--', linewidth=0.7)
        ax1_1_3.axhline(y=valor_outlier_bajo, color=colores[i], linestyle='--', linewidth=0.7)

    ax1_1_3.set_title('Distribución de Importes y límites de Rangos')
    ax1_1_3.legend(bbox_to_anchor=(1, 1))

    #3.2- AGRUPACION DE VARIABLES CATEGÓRICAS
    #INGRESOS

    #df_ingresos['Concepto'][df_ingresos['Concepto'].str.contains('construcciones ferroviarias')] = 'trf. construcciones ferroviarias de madrid sl'

    '''Se puede crear unas categorizaciones superiores según:
    
    Tipo de pago (Tipo_Pago)
    1.   Bizum
    2.  Transferencia
    '''

    #Se crea la columna Tipo_Pago
    df_ingresos['Tipo_Pago'] = None
    #Se determinan los bizum
    df_ingresos.loc[df_ingresos['Concepto'].str.contains('bizum'),'Tipo_Pago'] = 'Bizum'
    #Por descarte, el resto son transferencias
    df_ingresos['Tipo_Pago'][df_ingresos['Tipo_Pago'].isna()] = 'Transferencia'

    '''Se van a crear unas categorías superiores para una mayor agrupación de conceptos. 
    Esto es un trabajo muy personal porque dependerá en gran medida del dueño del dataset. 
    La cantidad y el detalle que se quiera alcanzar dependerá será una decisión personal. 
    Sin embargo, se aconseja, al menos, categorizar el top 20 de los gastos comunes.
    
    Se crearán dos nuevas columnas:
    1. Concep_Aclarativo
    2. Concep_Categoria
    
    Además, se crearán listas con palabras clave a buscar en el concepto para poder agrupar apropiadamente.
    '''
    df_ingresos['Concep_Aclarativo'] = None
    df_ingresos['Concep_Categoria'] = None
    df_gastos['Concep_Aclarativo'] = None
    df_gastos['Concep_Categoria'] = None

    def obtener_clasificaciones(df, tipo):
        #Asignaciones de concepto aclarativo
        #Obtener la ruta al directorio actual del script
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        nuevas_columnas = ['Concep_Aclarativo', 'Concep_Categoria']
        for columna in nuevas_columnas:
            #Construir la ruta al archivo dentro de la carpeta relativa
            ruta_archivo = os.path.join(directorio_actual, 'jsons', f'{columna}_{tipo}.json')
            #Leer el archivo JSON
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo_json:
                datos_json = json.load(archivo_json)

            #Se escribe sobre la nueva columna accediendo al json
            for clave, valor in datos_json.items():
                if isinstance(valor, list):
                    valor = '|'.join(valor)
                df.loc[df['Concepto'].str.contains(valor, case = False), columna] = clave

            df.loc[df[columna].isna(), columna] = 'Otros'
        return df

    #Asignaciones de la clasificación para ingresos
    df_ingresos = obtener_clasificaciones(df_ingresos, 'ingresos')



    #GASTOS
    '''Claramente, tal y como ocurre con df_ingresos, se puede dividir claramente en Tipo_Pago. Sin embargo, los Tipo_Concepto son más variados y hay que tratarlos de forma diferente.
    
    Tipo de pago (Tipo_Pago)
    1.   Tarjeta débito
    2.  Transferencia
    3. Tarjeta crédito
    4. Bizum
    5. Recibo
    6. Cuota'''

    #Se crea la columna Tipo_Pago
    df_gastos['Tipo_Pago'] = None

    df_gastos.loc[df_gastos['Concepto'].str.contains('tj-'), 'Tipo_Pago'] = 'Tarjeta Débito'
    df_gastos.loc[df_gastos['Concepto'].str.contains('cargo bizum - '), 'Tipo_Pago'] = 'Bizum'
    df_gastos.loc[df_gastos['Concepto'].str.contains('trf. '), 'Tipo_Pago'] = 'Transferencia'
    df_gastos.loc[df_gastos['Concepto'].str.contains('rcbo.'), 'Tipo_Pago'] = 'Recibo'
    df_gastos.loc[df_gastos['Concepto'].str.contains('cuota '), 'Tipo_Pago'] = 'Cuota'
    df_gastos.loc[df_gastos['Concepto'].str.contains('adeudo '), 'Tipo_Pago'] = 'Adeudo'
    df_gastos.loc[df_gastos['Concepto'].str.contains('tarjeta visa classic'), 'Tipo_Pago'] = 'Tarjeta Crédito'

    #Después de esta categorización, si queda alguno no categorizado lo más probable es porque sean los de la tarjeta de crédito
    df_gastos['Tipo_Pago'][df_gastos['Tipo_Pago'].isna()] = 'Tarjeta Crédito'

    #Una vez está todo categorizado en Tipo_Pago,
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

    #Distribucion de variables categóricas
    primer_dia = min(df['Fecha'])
    ultimo_dia = max(df['Fecha'])
    n_dias = (ultimo_dia - primer_dia).days

    #Se escribe una función para estampar la fecha en una figura y el rango de fechas analizado
    def estampar_fechas(fig):
        fig.text(0.05, 0.05, f"Fecha de análisis: {datetime.now().strftime('%d.%m.%Y')}",
                  horizontalalignment='left', verticalalignment='top', fontsize=10)
        fig.text(0.05, 0.03, f"Rango de fechas analizado: {primer_dia.strftime('%d.%m.%Y')} al "
                              f"{ultimo_dia.strftime('%d.%m.%Y')}", horizontalalignment='left', verticalalignment='top',
                  fontsize=10)

    #Se escribe en la gráfica general en la primera página el rango de fechas analizado
    estampar_fechas(fig1)
    estampar_fechas(fig2)

    filtro = df_ingresos.groupby('Concep_Categoria')['Importe'].sum().sort_values(ascending = False)
    valores = list(filtro.values)
    etiquetas = list(filtro.index)
    unidad = '€'
    titulo = f'Reparto de {unidad} por Categoría - Ingresos'
    squared_chart(ax2_1, valores, etiquetas, n_dias, titulo, unidad, colormap_verdes)

    filtro = df_gastos.groupby('Concep_Categoria')['Importe'].sum().sort_values(ascending = False)
    valores = list(filtro.values)
    etiquetas = list(filtro.index)
    unidad = '€'
    titulo = f'Reparto de {unidad} por Categoría - Gastos'
    squared_chart(ax2_2, valores, etiquetas, n_dias, titulo, unidad, colormap_rojos)

    #Ahora se grafican con barras horizontales los conceptos aclarativos generales

    filtro = df_ingresos.groupby('Concep_Aclarativo')['Importe'].sum().sort_values(ascending = False).sort_values(ascending = False).head(20)
    valores = list(filtro.values)
    etiquetas = list(filtro.index)
    unidad = '€'
    titulo = f'Top 20 Concepto Aclarativo - General - Ingresos'
    barh_chart(ax2_3, valores, etiquetas, titulo, unidad, colormap_verdes)

    filtro = df_gastos.groupby('Concep_Aclarativo')['Importe'].sum().sort_values(ascending = False).sort_values(ascending = False).head(20)
    valores = list(filtro.values)
    etiquetas = list(filtro.index)
    unidad = '€'
    titulo = f'Top 20 Concepto Aclarativo - General - Gastos'
    barh_chart(ax2_4, valores, etiquetas, titulo, unidad, colormap_rojos)



    pdf.savefig(fig1)
    plt.close(fig1)
    pdf.savefig(fig2)
    plt.close(fig2)

    #Ahora se grafican con barras horizontales los conceptos aclarativos del top 6 de las categorías
    #Por cada categoría se crea una gráfica con su top 20. En cada figura (hoja) se añadirán 3 gráficas
    n_categorias_ingresos = len(df_ingresos['Concep_Categoria'].unique())
    n_categorias_gastos = len(df_gastos['Concep_Categoria'].unique())
    n_graficas_filas_figure = 4
    n_graficas_column_figure = 2
    n_figures_ingresos = math.ceil(n_categorias_ingresos / (n_graficas_filas_figure * n_graficas_column_figure))
    n_figures_gastos = math.ceil(n_categorias_gastos / (n_graficas_filas_figure * n_graficas_column_figure))

    #Se generan las gráficas de ingresos
    i_grafica = 0
    for i in range(n_figures_ingresos):
        fig = plt.figure()
        gs_loop = GridSpec(n_graficas_filas_figure, n_graficas_column_figure, height_ratios=[1, 1, 1, 1], width_ratios=[1, 1])
        for j in range(n_graficas_filas_figure):
            for k in range(n_graficas_column_figure):
                if i_grafica >= n_categorias_ingresos:
                    break
                ax_loop = plt.subplot(gs_loop[j, k])
                #ax_loop.axis('off')
                categoria = df_ingresos.groupby('Concep_Categoria')['Importe'].sum().sort_values(ascending=False).index[i_grafica]
                filtro = df_ingresos[df_ingresos['Concep_Categoria'] == categoria].groupby('Concep_Aclarativo')['Importe'].sum().sort_values(ascending = False).head(20)
                valores = list(filtro.values)
                etiquetas = list(filtro.index)
                unidad = '€'
                titulo = f'Concepto Aclarativo - Categoria {categoria} - Ingresos'
                barh_chart(ax_loop, valores, etiquetas, titulo, unidad, colormap_verdes)
                i_grafica += 1
        # Ajustar la separación horizontal entre las columnas usando wspace
        plt.subplots_adjust(hspace = 0.5)
        estampar_fechas(fig)
        pdf.savefig()
        plt.close()

    #Se generan las gráficas de gastos
    i_grafica = 0
    for i in range(n_figures_gastos):
        fig = plt.figure()
        gs_loop = GridSpec(n_graficas_filas_figure, n_graficas_column_figure, height_ratios=[1, 1, 1, 1], width_ratios=[1, 1])
        for j in range(n_graficas_filas_figure):
            for k in range(n_graficas_column_figure):
                if i_grafica >= n_categorias_gastos:
                    break
                ax_loop = plt.subplot(gs_loop[j, k])
                #ax_loop.axis('off')
                categoria = df_gastos.groupby('Concep_Categoria')['Importe'].sum().sort_values(ascending=False).index[i_grafica]
                filtro = df_gastos[df_gastos['Concep_Categoria'] == categoria].groupby('Concep_Aclarativo')['Importe'].sum().sort_values(ascending = False).head(20)
                valores = list(filtro.values)
                etiquetas = list(filtro.index)
                unidad = '€'
                titulo = f'Concepto Aclarativo - Categoria {categoria} - Gastos'
                barh_chart(ax_loop, valores, etiquetas, titulo, unidad, colormap_rojos)
                i_grafica += 1
        plt.subplots_adjust(hspace = 0.5)
        estampar_fechas(fig)
        pdf.savefig()
        plt.close()