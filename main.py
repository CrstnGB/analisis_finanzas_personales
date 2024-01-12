import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
from matplotlib.backends.backend_pdf import PdfPages
import math
from datetime import datetime
from functions.func_charts import *
import procesamiento_datos as process


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

    # 0.6- Preparar colores a usar generales
    colores_I_G = ['#196F3D', '#E74C3C']

    # 1- INGESTA Y PROCESADO INICIAL
    df = process.preprocesamiento()
    #GRAFICADO
    salary_tracing(df, ax1_1_1)

    # 2- SEGREGACIÓN DE DATOS
    df_ingresos, df_gastos = process.separacion_ingresos_gastos(df)
    #GRAFICADO
    acum_comparison(df_ingresos, df_gastos, ax1_1_2)
    monthly_comparison(df_ingresos, df_gastos, ax1_1_4)
    yearly_comparison(df_ingresos, df_gastos, ax1_2_3)

    #3- AGRUPACION DE VARIABLES
    # 3.1- Agrupación de variables CONTINUAS
    df_ingresos, df_gastos = process.agrupacion_var_continuas(df_ingresos, df_gastos)
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

    #Se va a crear una lista donde almacenar tantos df como grupos haya
    #Se crea la lista de dataframes
    list_df_rangos_gastos = process.obtener_df_rangos(df_gastos)
    list_df_rangos_ingresos = process.obtener_df_rangos(df_ingresos)

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
        ax1_1_3.axhspan(valor_outlier_bajo, valor_outlier_alto, facecolor=colores[i], alpha=0.3,
                        label=f"[{math.ceil(valor_outlier_bajo)},{math.ceil(valor_outlier_alto)}]")
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
        ax1_1_3.axhspan(valor_outlier_bajo, valor_outlier_alto, facecolor=colores[i], alpha=0.3,
                        label=f"[{math.floor(valor_outlier_bajo)},{math.floor(valor_outlier_alto)}]")
        ax1_1_3.axhline(y=valor_outlier_alto, color=colores[i], linestyle='--', linewidth=0.7)
        ax1_1_3.axhline(y=valor_outlier_bajo, color=colores[i], linestyle='--', linewidth=0.7)

    ax1_1_3.set_title('Distribución de Importes y límites de Rangos')
    ax1_1_3.legend(bbox_to_anchor=(1, 1))

    #3.2- AGRUPACION DE VARIABLES CATEGÓRICAS
    df_ingresos, df_gastos = process.agrupacion_var_categoricas(df_ingresos, df_gastos)

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

    #Se guarda el pdf y se cierran las primeras figuras
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