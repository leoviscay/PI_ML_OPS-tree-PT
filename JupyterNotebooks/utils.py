import pandas as pd
from textblob import TextBlob
import re

import pandas as pd
from textblob import TextBlob
import re

# Funciones ETL

def types_data_df(df):
    '''
    Analiza de los tipos de datos en un DataFrame y devuelve un resumen que incluye información sobre
    los tipos de datos en cada columna, el porcentaje de valores no nulos y nulos, así como la
    cantidad de valores nulos por columna.

    Parameters:
        df (pandas.DataFrame): El DataFrame que se va a analizar.

    Returns:
        pandas.DataFrame: Un DataFrame que contiene el resumen de cada columna, incluyendo:
        - 'nombre_campo': Nombre de cada columna.
        - 'tipo_datos': Tipos de datos únicos presentes en cada columna.
        - 'no_nulos_%': Porcentaje de valores no nulos en cada columna.
        - 'nulos_%': Porcentaje de valores nulos en cada columna.
        - 'nulos': Cantidad de valores nulos en cada columna.
    '''

    mi_dict = {"nombre_campo": [], "tipo_datos": [], "no_nulos_%": [], "nulos_%": [], "nulos": []}

    for columna in df.columns:
        porcentaje_no_nulos = (df[columna].count() / len(df)) * 100
        mi_dict["nombre_campo"].append(columna)
        mi_dict["tipo_datos"].append(df[columna].apply(type).unique())
        mi_dict["no_nulos_%"].append(round(porcentaje_no_nulos, 2))
        mi_dict["nulos_%"].append(round(100-porcentaje_no_nulos, 2))
        mi_dict["nulos"].append(df[columna].isnull().sum())

    df_info = pd.DataFrame(mi_dict)
        
    return df_info

import pandas as pd
import re

def extract_anio_release(fecha):
    '''
    Extrae el año de una fecha en formato 'yyyy-mm-dd' y maneja valores nulos.

    Entrada: fecha en formato 'yyyy-mm-dd' 
    Return: 
        'yyyy' si el dato es válido.
        Si la fecha es nula, no sigue el formato esperado o es inconsistente,
        devuelve 'Dato no disponible'.

    Parameters:
        fecha (str or float or None): formato 'yyyy-mm-dd'.

    Returns:
        str: El año de la fecha si es válido, 'Dato no disponible' si es nula o el formato es incorrecto.
    '''
    if pd.notna(fecha):
        # Utiliza el método match de re con el patrón
        if re.match(r'^\d{4}-\d{2}-\d{2}$', str(fecha)):
            return str(fecha).split('-')[0]
        else:
            return 'Dato no disponible'
   


def replace_float(value):
    '''
    Reemplaza valores no numéricos y nulos en una columna con 0.0.

    Entrada: 'valor' y convertirlo a un número float.
    Si se puede, el valor numérico se mantiene. 
    Si la conversión falla o el valor es nulo, se devuelve 0.0 en su lugar.

    Parameters:
        value: El valor a convertir

    Returns:
        float: El valor numérico si la conversión es exitosa o nulo, o 0.0 si la conversión falla.
    '''
    if pd.isna(value):
        return 0.0
    try:
        float_value = float(value)
        return float_value
    except:
        return 0.0

def date_converter(cadena_fecha):
    '''
    Convierte una cadena de fecha en un formato específico a otro formato de fecha.
    
    Args:
    cadena_fecha (str): Cadena str
    
    Returns:
    str: Cadena de fecha en el formato "YYYY-MM-DD" o un mensaje de error si la cadena no cumple el formato esperado.
    '''
    match = re.search(r'(\w+\s\d{1,2},\s\d{4})', cadena_fecha)
    if match:
        fecha_str = match.group(1)
        try:
            fecha_dt = pd.to_datetime(fecha_str)
            return fecha_dt.strftime('%Y-%m-%d')
        except:
            return 'Fecha inválida'
    else:
        return 'Formato inválido'


###### FUNCIONES FEATURE ENGINNER

def sentiment_analysis(review):
    '''
    Realiza un análisis de sentimiento en un texto dado y devuelve un valor numérico que representa el sentimiento.

    Esta función utiliza la librería TextBlob para analizar el sentimiento en un texto dado y
    asigna un valor numérico de acuerdo a la polaridad del sentimiento.

    Parameters:
        review (str): El texto que se va a analizar para determinar su sentimiento.

    Returns:
        int: Un valor numérico que representa el sentimiento del texto:
             - 0 para sentimiento negativo.
             - 1 para sentimiento neutral o no clasificable.
             - 2 para sentimiento positivo.
    '''
    if review is None:
        return 1
    analysis = TextBlob(review)
    polarity = analysis.sentiment.polarity
    if polarity < -0.2:
        return 0  
    elif polarity > 0.2: 
        return 2 
    else:
        return 1 


############################# API


from fastapi import FastAPI, HTTPException
from typing import List, Dict




'''
def play_time_genre(genero: str):
    try:
        # Filtra el DataFrame por el género especificado
        df_filtered = df_dataExport[df_dataExport['genres'] == genero]

        # Encuentra el año con más horas jugadas para el género
        max_playtime_year = df_filtered.groupby('release_anio')['playtime_forever'].sum().idxmax()

        return {"Año de lanzamiento con más horas jugadas para Género": int(max_playtime_year)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def user_for_genre(genero: str):
    try:
        # Filtra el DataFrame por el género especificado
        df_filtered = df_dataExport[df_dataExport['genres'] == genero]

        # Encuentra el usuario con más horas jugadas para el género
        max_playtime_user = df_filtered.groupby('user_id')['playtime_forever'].sum().idxmax()

        # Agrupa las horas jugadas por año
        playtime_by_year = df_filtered.groupby('release_anio')['playtime_forever'].sum().reset_index()
        playtime_by_year = playtime_by_year.rename(columns={'playtime_forever': 'Horas'})

        return {"Usuario con más horas jugadas para Género": max_playtime_user, "Horas jugadas": playtime_by_year.to_dict(orient='records')}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def users_recommend(año: int):
    try:
        # Filtra el DataFrame por el año especificado y reviews recomendadas
        df_filtered = df_dataExport[(df_dataExport['release_anio'] == año) & (df_dataExport['sentiment_analysis'] == 2)]

        # Encuentra el top 3 de juegos más recomendados por usuarios
        top_games = df_filtered.groupby('item_name')['user_id'].count().nlargest(3).reset_index()

        return [{"Puesto {}".format(i+1): top_games.iloc[i, 0]} for i in range(3)]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''

