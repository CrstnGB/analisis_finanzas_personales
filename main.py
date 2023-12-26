import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
import numpy as np
import pandas as pd
import scipy as sp
import math
from functions.func_charts import *


# 0-PreConfiguración para las gráficas

# 0.1- Configurar parámetros de gráficas

altofig = 13
anchofig = altofig * (2 ** (1/2))
plt.rcParams['figure.figsize'] = (anchofig, altofig)   #estas son las medidas en pulgadas de un A3
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 12
plt.style.use('ggplot')

# 0.2- Crear una figura y un objeto GridSpec
fig = plt.figure()
gs0 = GridSpec(1, 2, height_ratios=[1], width_ratios=[1, 1])

# 0.3- Crear subgráficas usando las posiciones definidas por GridSpec
ax1 = plt.subplot(gs0[0, 0])
ax1.axis('off')
ax2 = plt.subplot(gs0[0, 1])
ax2.axis('off')

# 0.4- Añadir una cuadrícula interna en el subgráfico ax1
gs_1 = GridSpecFromSubplotSpec(4, 1, subplot_spec=gs0[0, 0], height_ratios=[1, 1, 1, 1], width_ratios=[1])
ax1_1 = plt.subplot(gs_1[0, 0])
ax1_2 = plt.subplot(gs_1[1, 0])
ax1_3 = plt.subplot(gs_1[2, 0])
ax1_4 = plt.subplot(gs_1[3, 0])

# 0.5- Añadir una cuadrícula interna en el subgráfico ax2
gs_2 = GridSpecFromSubplotSpec(3, 2, subplot_spec=gs0[0, 1], height_ratios=[1, 1, 1], width_ratios=[1, 1])
ax2_1 = plt.subplot(gs_2[0, 0])
ax2_2 = plt.subplot(gs_2[0, 1])
ax2_3 = plt.subplot(gs_2[1, 0])
ax2_4 = plt.subplot(gs_2[1, 1])
ax2_5 = plt.subplot(gs_2[2, 0])
ax2_6 = plt.subplot(gs_2[2, 1])


# 0.6- Personalizar los títulos subgráficas
ax1.set_title('EVOLUCIÓN Y COMPARACION INGRESOS VS GASTOS', y = 1.03)
ax2.set_title('DISTRIBUCIÓN INGRESOS Y GASTOS', y = 1.03)

# 0.7- Preparar colores a usar generales
colores_I_G = ['#196F3D', '#E74C3C']

#1- INGESTA Y PROCESADO INICIAL

# 1.1- Importar datos
ruta = r'C:\Users\Cristian\Documents\6- Proyectos\2- Python\2-Analisis finanzas personales\Extractos Bancarios'
nombre_archivo = '01.01.2023-15.12.2023.comb.xlsx'
df = pd.read_excel(ruta + "/" + nombre_archivo)

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
salary_tracing(df, ax1_1)


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
acum_comparison(df_ingresos, df_gastos, ax1_2)
monthly_comparison(df_ingresos, df_gastos, ax1_3)

#3- AGRUPACION DE VARIABLES
#3.1- AGRUPACION DE VARIABLES CATEGÓRICAS
#INGRESOS
df_ingresos['Concepto'][df_ingresos['Concepto'].str.contains('construcciones ferroviarias')] = 'trf. construcciones ferroviarias de madrid sl'

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

#Asignaciones de concepto aclarativo

df_ingresos.loc[df_ingresos['Concepto'].str.contains('construcciones ferroviarias', case = False), 'Concep_Aclarativo'] = 'Cofema'
df_ingresos.loc[df_ingresos['Concepto'].str.contains('pensión', case = False), 'Concep_Aclarativo'] = 'Pensión Baja Pat/Mat'
df_ingresos.loc[df_ingresos['Concepto'].str.contains('adecco', case = False), 'Concep_Aclarativo'] = 'Navantia Adecco'
df_ingresos.loc[df_ingresos['Concepto'].str.contains('cristina miras', case = False), 'Concep_Aclarativo'] = 'Vitalia'
df_ingresos.loc[df_ingresos['Concepto'].str.contains('a.e.a.t', case = False), 'Concep_Aclarativo'] = 'Hacienda'

df_ingresos.loc[df_ingresos['Concep_Aclarativo'].isna(), 'Concep_Aclarativo'] = 'Otros'

salarios_cristian = ['construcciones ferroviarias', 'adecco']
salarios_cristina = ['cristina miras']
hacienda = ['a.e.a.t', 'pensión']

#Asignaciones de concepto categoria
df_ingresos['Concep_Categoria'] = None
df_ingresos.loc[df_ingresos['Concepto'].str.contains('|'.join(salarios_cristian), case = False), 'Concep_Categoria'] = 'Salario Cristian'
df_ingresos.loc[df_ingresos['Concepto'].str.contains('|'.join(salarios_cristina), case = False), 'Concep_Categoria'] = 'Salario Cristina'
df_ingresos.loc[df_ingresos['Concepto'].str.contains('|'.join(hacienda), case = False), 'Concep_Categoria'] = 'Pens. & Hac.'

df_ingresos.loc[df_ingresos['Concep_Categoria'].isna(), 'Concep_Categoria'] = 'Otros'
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
Sin embargo, se aconseja, al menos, categorizar el top 20 de los gastos comunes.

Se crearán dos nuevas columnas:
1. Concep_Aclarativo
2. Concep_Categoria

Además, se crearán listas con palabras clave a buscar en el concepto para poder agrupar apropiadamente.
'''

supermercados_espania = [
    'mercadona', 'dia', 'carref', 'eliant', 'lidl', 'fruteria', 'supeco', 'aldi',
    'eroski', 'caprabo', 'hipercor', 'alcampo', 'coviran', 'superdino', 'myprotein', 'hsn',
    'supersol', 'froiz', 'masymas', 'mas', 'mercadal', 'merkabici', 'ahorramas', 'tuotrosuper',
    'tusuper', 'ecocenter', 'coviran', 'masfresco', 'sumapaz', 'caserito',
    'masymas', 'mascoop', 'consumcoop', 'saludable', 'amazonfresh', 'ulabox',
    'hiperusera', 'isoySuper', 'tendamarket', 'primaprix', 'capraboacasa',
    'carritus', 'mistral', 'mundofood', 'delSuperes',
    'hiperber', 'ycoms', 'tabaola', 'youzee', 'entrellaves', 'delhortaeacasa',
    'autofacil', 'ontruck', 'notelapierdas'
]
estaciones_combustible_espania = [
    'petroprix', 'petrol', 'autofuel', 'ballenoil', 'Repsol',
    'Cepsa', 'BP', 'Galp', 'Shell', 'Avia',
    'E.S. Auchan', 'E.S. Alcampo', 'E.S. Carrefour', 'BonÁrea', 'Esclatoil',
    'Esso', 'GALP', 'Iberdoex', 'Iturmendi', 'Meroil',
    'Petrocat', 'Staroil', 'Valcarce', 'VLC', 'Agip',
    'Beroil', 'Campsa', 'Disa', 'Energy', 'Eurocam',
    'Farruco', 'Gases Express Nieto', 'Integra Oil', 'Lecta', 'Magna Oil',
    'MGOil', 'Molgas', 'Oil Albera', 'Oil Precio', 'PetroAlacant',
    'PetroPrix', 'Petromax', 'Petromiralmag', 'Petronor', 'Petroprix',
    'Petroset', 'Plenoil', 'Prellezo', 'Prio', 'Red Ahorro',
    'Repsol', 'SAGIM', 'Shell', 'Staroil', 'Tamoil',
    'Tegasa', 'Urbaprix', 'Urbia', 'VCC', 'VITOGAS', 'hm oil'
]
companias_luz_espania = [
    'Endesa', 'Iberdrola', 'Naturgy', 'Imagina energ', 'EDP España', 'Viesgo', 'Energía XXI', 'Holaluz', 'Aldro Energía',
    'Podo', 'Lucera', 'Aura Energía', 'HidroCantábrico', 'Energía Sostenible', 'Fortia Energía', 'Som Energia',
    'Factor Energía', 'Cepsa Energía', 'Fenie Energía', 'Gana Energía', 'Energía Verde', 'Gas Natural Fenosa',
    'Repsol Electricidad y Gas', 'EDP Renewables', 'Holaluz', 'Iberia Solar', 'Acciona Energía'
]
sitios_compras_web_espana = [
    'Amazon', 'AliExpress', 'eBay', 'Wallapop', 'Temu', 'back market',
    'El Corte Inglés', 'Fnac', 'MediaMarkt', 'Carrefour Online',
    'Zalando', 'Worten', 'PCComponentes',
    'Ulabox', 'Veepee',
    'Tiendanimal', 'PcBox', 'MobileFun',
    'Ulabox', 'Veepee', 'Tiendanimal', 'PcBox', 'MobileFun', 'marketplace'
]

tiendas_espana = [
    'El Corte Ingles', 'Primark', 'MediaMarkt', 'Zara', 'Mango', 'Decathlon',
    'Leroy Merlin', 'Aki Bricolaje', 'Ikea', 'FNAC', 'Toys "R" Us', 'jd', 'kiabi',
    'Sprinter', 'Bershka', 'Pull&Bear', 'Stradivarius', 'Conforama', 'newyorker',
    'Casa del Libro', 'PCComponentes', 'Leroy Merlin', 'El Ganso', 'Primor', 'alvaro moreno'
]

gimnasios = ['blue gorila', 'gim', 'gym', 'vigor']

df_gastos['Concep_Aclarativo'] = None

#Asignaciones de concepto aclarativo
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(supermercados_espania), case = False), 'Concep_Aclarativo'] = 'Supermercados'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(estaciones_combustible_espania), case = False), 'Concep_Aclarativo'] = 'Gasolina'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(companias_luz_espania), case = False), 'Concep_Aclarativo'] = 'Electricidad'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(gimnasios), case = False), 'Concep_Aclarativo'] = 'Gym'
df_gastos.loc[df_gastos['Concepto'].str.contains('hidralia', case = False), 'Concep_Aclarativo'] = 'Agua'
df_gastos.loc[df_gastos['Concepto'].str.contains('5618504251', case = False), 'Concep_Aclarativo'] = 'Préstamo Coche'
df_gastos.loc[df_gastos['Concepto'].str.contains('farmacia', case = False), 'Concep_Aclarativo'] = 'Farmacia'
df_gastos.loc[df_gastos['Concepto'].str.contains('multitranquilidad', case = False), 'Concep_Aclarativo'] = 'Seguro Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('adeslas', case = False), 'Concep_Aclarativo'] = 'Seguro Salud'
df_gastos.loc[df_gastos['Concepto'].str.contains('web recaudacion', case = False), 'Concep_Aclarativo'] = 'IBI'
df_gastos.loc[df_gastos['Concepto'].str.contains('5589240554', case = False), 'Concep_Aclarativo'] = 'Hipoteca Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('rosa maria rodriguez fernandez', case = False), 'Concep_Aclarativo'] = 'Garaje'
df_gastos.loc[df_gastos['Concepto'].str.contains('5660654871', case = False), 'Concep_Aclarativo'] = 'Comunidad Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('cocinas el pinar', case = False), 'Concep_Aclarativo'] = 'Ref. Cocina'
df_gastos.loc[df_gastos['Concepto'].str.contains('pepe mobile', case = False), 'Concep_Aclarativo'] = 'Internet y Móvil'
df_gastos.loc[df_gastos['Concepto'].str.contains('cafe', case = False), 'Concep_Aclarativo'] = 'Cafeteria'
df_gastos.loc[df_gastos['Concepto'].str.contains('restaurant', case = False), 'Concep_Aclarativo'] = 'Restaurante'
df_gastos.loc[df_gastos['Concepto'].str.contains('bar', case = False), 'Concep_Aclarativo'] = 'Bar'
df_gastos.loc[df_gastos['Concepto'].str.contains('aeat', case = False), 'Concep_Aclarativo'] = 'Hacienda'
df_gastos.loc[df_gastos['Concepto'].str.contains('picaz', case = False), 'Concep_Aclarativo'] = 'Ref. Despacho'
df_gastos.loc[df_gastos['Concepto'].str.contains('sotelo|eulalio', case = False), 'Concep_Aclarativo'] = 'Ref. Ventanas'
df_gastos.loc[df_gastos['Concepto'].str.contains('david rodriguez garcia', case = False), 'Concep_Aclarativo'] = 'Inst. Aire Acond.'
df_gastos.loc[df_gastos['Concepto'].str.contains('valenciana', case = False), 'Concep_Aclarativo'] = 'M. Big Data y DS'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(sitios_compras_web_espana), case = False), 'Concep_Aclarativo'] = 'Compras Web'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(tiendas_espana), case = False), 'Concep_Aclarativo'] = 'Compra Tiendas'
df_gastos.loc[df_gastos['Concepto'].str.contains('dental', case = False), 'Concep_Aclarativo'] = 'Dentista'
df_gastos.loc[df_gastos['Concepto'].str.contains('taller', case = False), 'Concep_Aclarativo'] = 'Mantenimiento Coche'
df_gastos.loc[df_gastos['Concepto'].str.contains('booking', case = False), 'Concep_Aclarativo'] = 'Hotel/Hostal'
df_gastos.loc[df_gastos['Concepto'].str.contains('limpieza', case = False), 'Concep_Aclarativo'] = 'Servicio Limpieza'
df_gastos.loc[df_gastos['Concepto'].str.contains('regalo', case = False), 'Concep_Aclarativo'] = 'Regalo'
df_gastos.loc[df_gastos['Concepto'].str.contains('fisiotera', case = False), 'Concep_Aclarativo'] = 'Fisioterapeuta'
df_gastos.loc[df_gastos['Concepto'].str.contains('linea directa aseguradora', case = False), 'Concep_Aclarativo'] = 'Seguro coche'
df_gastos.loc[df_gastos['Concepto'].str.contains('atitude estavel', case = False), 'Concep_Aclarativo'] = 'Hotel Despedida Sergio'

df_gastos.loc[df_gastos['Concep_Aclarativo'].isna(), 'Concep_Aclarativo'] = 'Otros'

#Ahora igual con Concep_Categoria
df_gastos['Concep_Categoria'] = None

df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(supermercados_espania), case = False), 'Concep_Categoria'] = 'Supermercados'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(estaciones_combustible_espania), case = False), 'Concep_Categoria'] = 'Transporte'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(companias_luz_espania), case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(gimnasios), case = False), 'Concep_Aclarativo'] = 'Deporte'
df_gastos.loc[df_gastos['Concepto'].str.contains('hidralia', case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('5618504251', case = False), 'Concep_Categoria'] = 'Transporte'
df_gastos.loc[df_gastos['Concepto'].str.contains('farmacia|fcia', case = False), 'Concep_Categoria'] = 'Salud'
df_gastos.loc[df_gastos['Concepto'].str.contains('multitranquilidad', case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('adeslas', case = False), 'Concep_Categoria'] = 'Salud'
df_gastos.loc[df_gastos['Concepto'].str.contains('web recaudacion', case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('5589240554', case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('rosa maria rodriguez fernandez', case = False), 'Concep_Categoria'] = 'Transporte'
df_gastos.loc[df_gastos['Concepto'].str.contains('5660654871', case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('cocinas el pinar', case = False), 'Concep_Categoria'] = 'Mejora Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('pepe mobile', case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('cafe', case = False), 'Concep_Categoria'] = 'Cafet. & Rest'
df_gastos.loc[df_gastos['Concepto'].str.contains('restaurant', case = False), 'Concep_Categoria'] = 'Cafet. & Rest'
df_gastos.loc[df_gastos['Concepto'].str.contains('bar', case = False), 'Concep_Categoria'] = 'Cafet. & Rest'
df_gastos.loc[df_gastos['Concepto'].str.contains('aeat', case = False), 'Concep_Categoria'] = 'Hacienda'
df_gastos.loc[df_gastos['Concepto'].str.contains('picaz', case = False), 'Concep_Categoria'] = 'Mejora Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('sotelo|eulalio', case = False), 'Concep_Categoria'] = 'Mejora Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('david rodriguez garcia', case = False), 'Concep_Categoria'] = 'Mejora Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('valenciana', case = False), 'Concep_Categoria'] = 'Formación'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(sitios_compras_web_espana), case = False), 'Concep_Categoria'] = 'Compras Tiendas y web'
df_gastos.loc[df_gastos['Concepto'].str.contains('|'.join(tiendas_espana), case = False), 'Concep_Categoria'] = 'Compras Tiendas y web'
df_gastos.loc[df_gastos['Concepto'].str.contains('dental', case = False), 'Concep_Categoria'] = 'Salud'
df_gastos.loc[df_gastos['Concepto'].str.contains('taller', case = False), 'Concep_Categoria'] = 'Transporte'
df_gastos.loc[df_gastos['Concepto'].str.contains('booking', case = False), 'Concep_Categoria'] = 'Viajes y Hoteles'
df_gastos.loc[df_gastos['Concepto'].str.contains('limpieza', case = False), 'Concep_Categoria'] = 'Hogar'
df_gastos.loc[df_gastos['Concepto'].str.contains('regalo', case = False), 'Concep_Categoria'] = 'Regalos'
df_gastos.loc[df_gastos['Concepto'].str.contains('fisiotera', case = False), 'Concep_Categoria'] = 'Salud'
df_gastos.loc[df_gastos['Concepto'].str.contains('linea directa aseguradora', case = False), 'Concep_Categoria'] = 'Transporte'
df_gastos.loc[df_gastos['Concepto'].str.contains('atitude estavel', case = False), 'Concep_Categoria'] = 'Viajes y Hoteles'

df_gastos.loc[df_gastos['Concep_Categoria'].isna(), 'Concep_Categoria'] = 'Otros'

#Distribucion de variables categóricas
primer_dia = min(df['Fecha'])
ultimo_dia = max(df['Fecha'])
n_dias = (ultimo_dia - primer_dia).days

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

filtro = df_ingresos.groupby('Concep_Aclarativo')['Importe'].sum().sort_values(ascending = False).sort_values(ascending = False).head(20)
valores = list(filtro.values)
etiquetas = list(filtro.index)
unidad = '€'
titulo = f'Top 20 Concepto Aclarativo - Ingresos'
barh_chart(ax2_3, valores, etiquetas, titulo, unidad, colormap_verdes)

filtro = df_gastos.groupby('Concep_Aclarativo')['Importe'].sum().sort_values(ascending = False).sort_values(ascending = False).head(20)
valores = list(filtro.values)
etiquetas = list(filtro.index)
unidad = '€'
titulo = f'Top 20 Concepto Aclarativo - Gastos'
barh_chart(ax2_4, valores, etiquetas, titulo, unidad, colormap_rojos)

#3.2- Agrupación de variables CONTINUAS
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
title = f'Reparto de {unidad} por Rango de Importe - Ingresos'
pie_chart(ax2_5, valores, etiquetas, title, unidad, colormap_verdes)

#GASTOS
filtro = df_gastos.groupby('Rango_Importe')['Importe'].sum().sort_values(ascending = False)
etiquetas = list(filtro.index)
valores = list(filtro.values)
unidad = '€'
title = f'Reparto de {unidad} por Rango de Importe - Gastos'
pie_chart(ax2_6, valores, etiquetas, title, unidad, colormap_rojos)

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
ax1_4.plot(etiquetas, valores, color = '#283747')
#Pintar lineas de ouliers
check_label_gastos = False
check_label_ingresos = False
for _df in list_df_rangos_gastos:
    valor_outlier = [max(_df['Importe']) * (-1) for i in range(len(etiquetas))]
    if check_label_gastos == False:
        ax1_4.plot(etiquetas, valor_outlier, color = colores_I_G[1], linewidth = 0.7, linestyle = '--', label = 'Límites Outliers Gastos')
        check_label_gastos = True
    else:
        ax1_4.plot(etiquetas, valor_outlier, color = colores_I_G[1], linewidth = 0.7, linestyle = '--')

for _df in list_df_rangos_ingresos:
    valor_outlier = [max(_df['Importe']) for i in range(len(etiquetas))]
    if check_label_ingresos == False:
        ax1_4.plot(etiquetas, valor_outlier, color = colores_I_G[0], linewidth = 0.7, linestyle = '--', label = 'Límites Outliers Ingresos')
        check_label_ingresos = True
    else:
        ax1_4.plot(etiquetas, valor_outlier, color = colores_I_G[0], linewidth = 0.7, linestyle = '--')

ax1_4.set_title('Distribución de Importes y límites de Rangos')
# Ajustar el diseño de la figura
plt.tight_layout()

# Mostrar la figura
plt.show()