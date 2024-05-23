# INTRO
Este es un proyecto personal que surge de la necesidad de controlar de la forma más eficiente posible mis finanzas personales sin necesidad de utilizar aplicaciones de terceros, ya que prefiero evitar compartir información sensible.

## Bases de funcionamiento
Este proyecto consta de tres etapas.
- **Ingesta de datos**: a partir de un extracto bancario excel, el programa será capaz de extraer los datos, preprocesarlo y realizar ciertas transformaciones. Por ejemplo, modificará la estructura de las columnas (eliminando columnas no usadas para el análisis, cambiando nombres de columnas...), separará en dos dataframes los ingresos y los gastos para un análisis por separado, creará clasificaciones de variables continuas de estos dataframes (los gastos y los ingresos) discretizándolos en rangos definidos por outliers, creará clasificaciones de variables categóricas como los conceptos, etc...
- **Previsión**: dando otro extracto bancario, idealmente, del año anterior completo al del análisis, se generará una línea de previsión del balance general del año en curso usando el modelo de regresión lineal de *sklearn*. De esta manera, se aprovechan las ventajas del *Machine Learning* para la estimación del balance.
- **Visualización**: generará un pdf, el cual se guardará en la carpeta de *Outputs_KPIs*, bajo el nombre de *dd.mm.aaaa.KPI_del_dd.mm.aaaa_al_dd.mm.aaaa.pdf*, siendo la primera fecha la fecha del análisis, la segunda fecha la fecha del primer día del año en el que existen registros en el excel de movimientos y la última fecha corresponde a la última fecha del año donde existen movimientos en el excel. Ej: *01.04.2024.KPI_Economia_del_01.01.2024_al_30.03.2024.pdf*. Este pdf contendrá un dashboard de gráficas creados a partir de *matplotlib* para poder revisar los resultados del análisis. Además, se generará un excel llamado *dfs_output.xlsx* donde se guardarán los dataframes ya procesados y usados para este reporte con el fin de que si un usuario desea usar otra herramienta de visualización interactiva, como por ejemplo, *PowerBI*, pueda hacerlo sin problema.

Además, existe un módulo que se ejecuta por separado llamado *fusionar_extractos.py*. El fin de este archivo es desglosar un tipo de gasto concreto: el de la tarjeta de **crédito**. En Caja Rural, así como en otros muchos bancos, a diferencia de los pagos realizado con tarjeta de **débito**, los de **crédito** adoptan un concepto único llamado *tarjeta visa classic* (este concepto puede variar en otros bancos). A través de la página web del banco, se puede sacar un extracto separado de los gastos de dicha tarjeta con los conceptos reales de los comercios y, este módulo, permite fusionar ambos extractos como si fuera uno. Esto permite alcanzar un mayor grado de control sobre los gastos. En algunos casos, habrá quien prefiera no usar este módulo y renombrar el concepto *tarjeta visa classic* como, por ejemplo, *mercadona*, porque tenga esta tarjeta como compra única para los supermercados.

## Acerca de las categorizaciones de variables categóricas (conceptos)
Una vez se visualizan los datos podemos percatarnos de que hay un porcentaje alto de gastos no categorizados, es decir, en la categoría *Otros*. Este programa, aunque trae cierta información de partida para categorizar con elementos generales (Ej: busca palabras clave en los concepto como *Mercadona* para categorizarlo como gasto doméstico), se puede configurar al 100%. Para ello, hay dos opciones:
- **Modificar directamente los json**: las categorizaciones están contenidas en los jsons de la carpeta *jsons*. Se tiene categorizado tanto los gastos como los ingresos. Además de las categorizaciones, se encontrarán otros jsons con los *conceptos aclarativos*. Estos sirven para poder dotar de sentido a ciertos conceptos que, a priori, pueden resultar complicados de entender. Por ejemplo, puede existir un gasto llamado *trsfn. 154891523*, pero tras revisar de forma manual el importe y las fechas, nos damos cuenta que se refiere al pago de la comunidad del edificio. Por lo tanto, podemos relacionar *trsfn. 154891523* con *Pago Comunidad* y, de esta forma, en el dashboard lo veremos de esta manera.
- **Utilizar el asistente de categorización**: ejecutando el archivo *asistente_categorizacion.py* tendremos una interfaz por consola que nos ayudará a categorizar nuestros gastos priorizando aquellos gastos cuya sumatoria sea mayor. Es decir, si dentro de la categoría *Otros* tenemos 10k €, divididos en 3 gastos, uno de 5k, otro de 3k y otro de 2k, nos aparecerá como sugerencia en la lista para categorizar primero el de 5k. De esta manera, se intenta disminuir lo máximo posible la cantidad de gastos no categorizados. Nótese que siempre se tendrá un % de gastos no categorizados, ya que es prácticamente inviable categorizar todos los minigastos no comunes. Los comunes, en cambio, sí se tendrán en cuenta, ya que palabras clave como *café*, *bar*, *restaurante*... están tenidas en cuenta en los json y, además, se pueden añadir palabras clave al gusto. Ojo, también se pueden introducir palabras como *mercad* e identificará aquel concepto donde aparezca *Mercadona*, *mercado*, *Mercadona*, ya que el programa hará un *match* si el concepto contiene dicho *string* y sin ser sensible a mayúsculas y minúsculas.

## Archivos de ejecución
- **main.py**: ejecutará el archivo orquestador del programa. Se nos pedirá ingresar el nombre del extracto bancario a analizar así como el nombre del extracto bancario sobre el que realizará la previsión.
- **asistente_categorizacion.py**: ejecutará la interfaz por consola del asistente de categorización
- **fusionar_extractos.py**: nos pedirá el nombre de los dos archivos a fusionar y creará otro archivo, que heredará el nombre del primero más ".comb.xlsx" ("comb" de combinado).
