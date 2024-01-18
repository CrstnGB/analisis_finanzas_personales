# Función para eliminar tildes
import unicodedata
import json
import os

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
        'Concep_Categoria_gastos': os.path.join(directorio_jsons, 'Concep_Categoria_gastos.json')
    }
    return rutas_jsons

def leer_json(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo_json:
        datos_json = json.load(archivo_json)
    return datos_json

def escribir_json(ruta_archivo, datos_json):
    with open(ruta_archivo, "w") as archivo_json:
        json.dump(datos_json, archivo_json, indent=2)