import procesamiento_datos as process
from functions.func_auxiliares import *
import sys

def procesar_datos():
    # 1- INGESTA Y PROCESADO INICIAL
    df = process.preprocesamiento()
    # 2- SEGREGACIÓN DE DATOS
    df_ingresos, df_gastos = process.separacion_ingresos_gastos(df)
    #3- AGRUPACION DE VARIABLES
    # 3.1- Agrupación de variables CONTINUAS
    df_ingresos, df_gastos = process.agrupacion_var_continuas(df_ingresos, df_gastos)
    #3.2- AGRUPACION DE VARIABLES CATEGÓRICAS
    df_ingresos, df_gastos = process.agrupacion_var_categoricas(df_ingresos, df_gastos)
    return df_ingresos, df_gastos

def obtener_respuesta_S_N(pregunta):
    while True:
        respuesta = input(f"\n{pregunta} (S/N): ").upper()
        if respuesta == 'S':
            return True
        elif respuesta == 'N':
            return False
        else:
            print("Por favor, ingresa 'S' o 'N'.")

def obtener_respuesta_cadena(pregunta):
    while True:
        respuesta = input(f"\n{pregunta}: ")
        if respuesta != '':
            return respuesta
        else:
            print("Por favor, ingresa una respuesta valida")

def visualizar_concep_aclarativos_existentes(archivo_json):
    for clave, lista in archivo_json.items():
        print(f"{clave}:")
        print(lista)


def identificar_indices(df_filtrado, archivo_json):
    print('\nPuedes categorizar más de un ítem a la vez en la misma categoría. \nIntroduce los índices uno a uno '
          'presionando "Intro" cada vez. \nCuando acabes, presiona cualquier letra A-Z: \n')
    indices = []
    while True:
        try:
            indice = int(input("Introduce un índice: "))
            if indice > 19:
                print("Debes introducir un índice entre 0-19")
            elif indice == -1:
                visualizar_concep_aclarativos_existentes(archivo_json)
            else:
                indices.append(indice)
        except ValueError:
            break
    indices = list(set(indices))
    indices.sort()
    print(f"\nEstos son los ítems escogidos:\n")
    for i in indices:
        print(f"{i}-{df_filtrado.iloc[i, 0]}")
    print("\nTodos estos ítems van a pertenecer a la misma categoría. Sin embargo,"
          "cada uno de ellos necesita tener una descripción aclaratoria del concepto.\n"
          "A esto se le llama concepto aclarativo.\n"
          "Dos ítems pueden compartir el mismo concepto aclarativo y, al calcular \n"
          "los totales y graficarlos se sumarán considerándose como un único ítem.\n"
          "Escribe el concepto aclarativo para cada ítem. Si hay dos o más que \n"
          "comparten el concepto aclarativo, escribe el índice del primero que ya\n"
          "hayas escrito en lugar de volver escribir el concepto aclarativo.\n"
          "Si deseas que el concepto aclarativo sea igual que el concepto original,\n"
          "escribe '='.")
    return indices

def definir_concep_aclarativo(df_filtrado, indices, archivo_json, bool_masivo = False):
    concep_aclarativos = dict()
    if bool_masivo == False:
        indices_definidos = []
        for indice in indices:
            concepto = df_filtrado.iloc[indice, 0]
            respuesta_valida = False
            while respuesta_valida == False:
                concep_aclarativo = input(f"Escribe el Concepto Aclarativo de \n'{concepto}': ")
                if concep_aclarativo == "=":
                    #Si el concep_aclarativo es igual que el concepto:
                    #Se comprueba que ese concepto no sea ya una clave en el diccionario. Si no existe, se crea la lista
                    if concepto not in concep_aclarativos:
                        concep_aclarativos[concepto] = []
                    #Se comprueba que en la lista no exista ya ese concepto. Si no existe, se añade.
                    if concepto not in concep_aclarativos[concepto]:
                        concep_aclarativos[concepto].append(concepto)
                    #df['Concep_Aclarativo'][df['Concepto'] == concepto] = concepto
                    respuesta_valida = True
                elif concep_aclarativo.isnumeric() == True:
                    indice_ref = int(concep_aclarativo)
                    if indice_ref not in indices:
                        print("El indice escogido de referencia no existe en la lista a categorizar.\n")
                        print(f"Estos son los indices elegidos y definidos: \n{indices_definidos}")
                    elif indice_ref not in indices_definidos:
                        print("El indice escogido de referencia aún no tiene un concepto aclarativo definido.\n")
                        print(f"Estos son los indices elegidos y definidos: \n{indices_definidos}")
                    else:
                        #Se obtiene el concepto de referencia del índice escogido
                        concepto_ref = df_filtrado.iloc[indice_ref, 0]
                        #Se busca entre todas las listas de las claves en cuál aparece el concepto_ref
                        for clave, valor_lista in concep_aclarativos.items():
                            for valor in valor_lista:
                                if valor == concepto_ref:
                                    concep_aclarativo = clave
                                    break
                                    break_outer = True
                                if break_outer == True:
                                    break
                        #Se comprueba que el valor no existe ya en la lista
                        if concepto not in concep_aclarativos[concep_aclarativo]:
                            #Se asocia a dicha clave el concepto como un valor más
                            concep_aclarativos[concep_aclarativo].append(concepto)
                        #concep_aclarativo = df['Concep_Aclarativo'][df['Concepto'] == concepto_ref].iloc[0]
                        #df['Concep_Aclarativo'][df['Concepto'] == concepto] = concep_aclarativo
                        respuesta_valida = True
                else:
                    if concep_aclarativo not in concep_aclarativos:
                        concep_aclarativos[concep_aclarativo] = []
                    if concepto not in concep_aclarativos[concep_aclarativo]:
                        concep_aclarativos[concep_aclarativo].append(concepto)
                    #df['Concep_Aclarativo'][df['Concepto'] == concepto] = concep_aclarativo
                    respuesta_valida = True
            #print(df[df['Concepto'] == concepto].index)
            indices_definidos.append(indice)
    else:
        cadenas = []
        print("\nSe pueden definir tantas cadenas como se desee. Ej. Para el concepto aclarativo 'Gasolina', podrías\n"
              "definir como cadena 'Repsol', 'Ballenoil', 'Gasol'...")
        print("Si quieres dejar de definir cadenas, escribe 'exit'.")
        print("Si quieres visualizar los Concep_Aclarativos existentes escribe '-1'")
        while True:
            cadena = obtener_respuesta_cadena("Escribe una cadena de texto a buscar en conceptos")
            if cadena == 'exit':
                if not len(cadenas) > 0:
                    print("Debes introducir al menos una cadena.")
                else:
                    break
            elif cadena == '-1':
                visualizar_concep_aclarativos_existentes(archivo_json)
            else:
                cadenas.append(cadena)
        concep_aclarativo = obtener_respuesta_cadena("\nAhora, introduce el concepto aclarativo")
        concep_aclarativos[concep_aclarativo] = cadenas
    return concep_aclarativos

def actualizar_archivo_json(archivo_json, nuevos_elementos):
    for clave, lista in nuevos_elementos.items():
        if clave not in archivo_json:
            archivo_json[clave] = lista
        else:
            for valor in lista:
                if valor not in archivo_json[clave]:
                    archivo_json[clave].append(valor)
    return archivo_json

def definir_concep_categoria(archivo_json, nuevos_concep_aclarativos):
    print(f"Estos son los conceptos aclarativos a clasificar:")
    cadena = ""
    for clave in nuevos_concep_aclarativos:
        cadena += clave + ", " if cadena != "" else clave
    print(cadena)
    print("\nEstas son las categorías existentes: \n")
    lista_claves_categorias = list(archivo_json.keys())
    for i, clave_categoria in enumerate(lista_claves_categorias):
        print(f"{i}-{clave_categoria}")
    for item in nuevos_concep_aclarativos:
        for clave_categoria, lista in archivo_json.items():
            if item in lista:
                print(f"\nEl concepto aclarativo {item} ya se encuentra en la categoría {clave_categoria}.")
                respuesta = obtener_respuesta_S_N("¿Deseas continuar? Esto categorizará todos los conceptos aclarativos"
                                              "seleccionados en la categoría mencionada.")
                if respuesta == True:
                    return clave_categoria
                else:
                    print("Programa interrumpido")
                    sys.exit()

    respuesta = obtener_respuesta_S_N("¿Quieres incluirlos en una categoría existente?")
    if respuesta == True:
        while True:
            i_categoria = input("Escribe el índice de la categoria escogida: ")
            if not i_categoria.isnumeric():
                print(f"Ingresa un número válido entre el rango [0-{len(lista_claves_categorias) - 1}]")
            elif int(i_categoria) > (len(lista_claves_categorias) - 1):
                print(f"Ingresa un número válido entre el rango [0-{len(lista_claves_categorias) - 1}]")
            else:
                categoria = lista_claves_categorias[int(i_categoria)]
                return categoria
    else:
        while True:
            categoria = input("Escribe la nueva categoría: ")
            if categoria == "":
                print("Introduce un valor valido")
            else:
                return categoria


def proceso_categorizacion(df, tipo):
    print(f"Estos son los 20 movimientos de {tipo.upper()} no categorizados (Otros) por orden de importe total de mayor a menor: \n")
    df_filtrado = df[df['Concep_Aclarativo'] == 'Otros'].groupby('Concepto', observed=False)[
        'Importe'].sum().sort_values(ascending = False).head(20).reset_index()
    print(df_filtrado)

    # Se lee el archivo json para los conceptos aclarativos
    archivo_concep_aclarativo_json = leer_json(rutas_jsons[f'Concep_Aclarativo_{tipo}'])

    bool_masivo = obtener_respuesta_S_N("¿Desea categorizar de forma masiva?")
    if bool_masivo == False:
        bool_categorizar = obtener_respuesta_S_N("¿Desea categorizar alguno/s de los items individualmente?")
        if bool_categorizar == True:
            indices = identificar_indices(df_filtrado, archivo_concep_aclarativo_json)
    else:
        indices = None

    if bool_masivo == True or bool_categorizar == True:
        #Se llama a una función que devuelve un diccionario con los nuevos conceptos aclarativos
        nuevos_concep_aclarativos = definir_concep_aclarativo(df_filtrado, indices,
                                                              archivo_concep_aclarativo_json,bool_masivo)
        #Se integra este diccionario con el json
        nuevo_archivo_concep_aclarativo_json = actualizar_archivo_json(archivo_concep_aclarativo_json,
                                                                       nuevos_concep_aclarativos)
        '''Más adelante se escribirá sobre el archivo, para evitar escritura en caso de error en el resto de este trozo
        de codigo'''
        #Se vuelve a leer el archivo json, pero esta vez, de categorias
        archivo_concep_categoria_json = leer_json(rutas_jsons[f'Concep_Categoria_{tipo}'])
        #Se define la categoria
        nueva_categoria = definir_concep_categoria(archivo_concep_categoria_json, nuevos_concep_aclarativos)
        #Se crea un diccionario con la nueva categoria y los nuevos conceptos aclarativos
        nueva_categoria_definida = {nueva_categoria: list(nuevos_concep_aclarativos.keys())}
        # Se integra este diccionario con el json
        nuevo_archivo_concep_categoria_json = actualizar_archivo_json(archivo_concep_categoria_json,
                                                                       nueva_categoria_definida)
        # Se cargan los nuevos datos del archivo json los archivos jsons
        escribir_json(rutas_jsons[f'Concep_Aclarativo_{tipo}'], nuevo_archivo_concep_aclarativo_json)
        escribir_json(rutas_jsons[f'Concep_Categoria_{tipo}'], nuevo_archivo_concep_categoria_json)

        print("jsons actualizados")
    else:
        print("Programa finalizado")

print("\nBienvenido/a al asistente de categorización. Con este asistente, podrás categorizar todos tus ingresos y tus\n"
      "gastos para llevar un mejor control sobre los mismos. Este proceso se puede realizar de dos maneras distintas: \n\n"
      "1- De forma individual: se irá seleccionando conceptos sugeridos (según un mayor gasto acumulado por concepto)\n"
      "a los que se les asociará un concepto aclarativo y, a continuación, se les incluirá en una categoría nueva o \n"
      "existente.\n\n"
      "2- De forma masiva: se definirá una cadena de texto, la cual se usará para hacer una búsqueda entre todos los\n"
      "conceptos. Aquel concepto que contenga dicha cadena de texto tendrá el concepto aclarativo que el usuario \n"
      "también defina. Tras esto, al igual que anteriormente, se les incluirá en una categoría nueva o existente.\n\n"
      "El concepto aclarativo es imprescindible para una buena categorización, ya que en sí mismo puede generar grupos\n."
      "Ej: 'mercadona camposoto' y 'mercadona pinto' pueden tener un mismo concepto aclarativo llamado 'mercadona'.\n"
      "Si esto se categoriza masivamente, se puede definir la cadena de texto 'mercadona' para la búsqueda y asociación\n"
      "de todos los conceptos que contengan dicha cadena de texto al concepto aclarativo 'mercadona'.")

rutas_jsons = definir_rutas_jsons()
df_ingresos, df_gastos = procesar_datos()
bool_categorizar_ingresos = obtener_respuesta_S_N("¿Desea categorizar ingresos?")
if bool_categorizar_ingresos:
    proceso_categorizacion(df_ingresos, 'ingresos')

bool_categorizar_gastos = obtener_respuesta_S_N("¿Desea categorizar gastos?")
if bool_categorizar_gastos:
    proceso_categorizacion(df_gastos, 'gastos')