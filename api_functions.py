from fastapi import FastAPI, HTTPException

import pandas as pd
from typing import List

app = FastAPI(debug=True)


# Carga de datos en un único lugar para evitar repetición de código
try:
    df_dataExport = pd.read_parquet('data\data_export_api.parquet')
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Error al cargar el archivo de datos")

@app.get('/PlayTimeGenre/{genero}')
def PlayTimeGenre(genero: str):
    '''
    Datos:
    - genero (str): Género para el cual se busca el año con más horas jugadas.

    Funcionalidad:
    - Devuelve el año con más horas jugadas para el género especificado.

    Return:
    - Dict: {"Año de lanzamiento con más horas jugadas para Género X": int}
    '''
    try:
        genero_filtrado = df_dataExport[df_dataExport['genres'].apply(lambda x: genero in x)]

        if genero_filtrado.empty:
            raise HTTPException(status_code=404, detail=f"No hay datos para el género {genero}")

        genero_filtrado['playtime_forever'] = genero_filtrado['playtime_forever'] / 60

        max_hours_year = genero_filtrado.groupby('release_anio')['playtime_forever'].sum().idxmax()

        return {"Año de lanzamiento con más horas jugadas para el Género " + genero: int(max_hours_year)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/UserForGenre/{genero}')
def UserForGenre(genero:str):
    '''
    Datos:
    - genero (str): Género para el cual se busca el usuario con más horas jugadas y la acumulación de horas por año.

    Funcionalidad:
    - Devuelve el usuario con más horas jugadas y una lista de la acumulación de horas jugadas por año para el género especificado.

    Return:
    - Dict: {"Usuario con más horas jugadas para Género X": List, "Horas jugadas": List}
    '''
    try:
        condition = df_dataExport['genres'].apply(lambda x: genero in x)
        juegos_genero = df_dataExport[condition]

       
        juegos_genero['playtime_forever'] = juegos_genero['playtime_forever'] / 60
        juegos_genero['release_anio'] = pd.to_numeric(juegos_genero['release_anio'], errors='coerce')
        juegos_genero = juegos_genero[juegos_genero['release_anio'] >= 100]
        juegos_genero['Año'] = juegos_genero['release_anio']

        horas_por_usuario = juegos_genero.groupby(['user_id', 'Año'])['playtime_forever'].sum().reset_index()
        horas_por_usuario = juegos_genero.groupby(['user_id', 'Año'])['playtime_forever'].sum().reset_index()
        if not horas_por_usuario.empty:
            usuario_max_horas = horas_por_usuario.groupby('user_id')['playtime_forever'].sum().idxmax()
            usuario_max_horas = horas_por_usuario[horas_por_usuario['user_id'] == usuario_max_horas]
        else:
            usuario_max_horas = None

        acumulacion_horas = horas_por_usuario.groupby(['Año'])['playtime_forever'].sum().reset_index()
        acumulacion_horas = acumulacion_horas.rename(columns={'Año': 'Año', 'playtime_forever': 'Horas'})

        resultado = {
            "Usuario con más horas jugadas para " + genero: {"user_id": usuario_max_horas.iloc[0]['user_id'], "Año": int(usuario_max_horas.iloc[0]['Año']), "playtime_forever": usuario_max_horas.iloc[0]['playtime_forever']},
            "Horas jugadas": [{"Año": int(row['Año']), "Horas": row['Horas']} for _, row in acumulacion_horas.iterrows()]
        }

        return resultado

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Error al cargar los archivos de datos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get('/UsersRecommend/{anio}')
def UsersRecommend(anio: int):
    '''
    Datos:
    - anio (int): Año para el cual se busca el top 3 de juegos más recomendados.

    Funcionalidad:
    - Devuelve el top 3 de juegos más recomendados por usuarios para el año dado.

    Return:
    - List: [{"Puesto 1": str}, {"Puesto 2": str}, {"Puesto 3": str}]
    '''
    
    filtered_df = df_dataExport[
    (df_dataExport["reviews_anio"] == anio) &
    (df_dataExport["reviews_recommend"] == True) &
    (df_dataExport["sentiment_analysis"]>=1)
    ]
    recommend_counts = filtered_df.groupby("item_name")["item_name"].count().reset_index(name="count").sort_values(by="count", ascending=False).head(3)
    top_3_dict = {f"Puesto {i+1}": juego for i, juego in enumerate(recommend_counts['item_name'])}
    return top_3_dict


@app.get('/UsersNotRecommend/{anio}')
def UsersNotRecommend(anio: int):
    '''
  Devuelve el top 3 de juegos MENOS recomendados por usuarios para el año dado.

  Args:
    anio (int): Año para el cual se buscan los juegos menos recomendados.

  Returns:
    dict: Diccionario con el top 3 de juegos menos recomendados, con la estructura {posición: juego}.
    '''
    try:
        filtered_df = df_dataExport.query(
        f"reviews_anio == {anio} and reviews_recommend == False and sentiment_analysis == 0"
        )
        recommend_counts = filtered_df.groupby("item_name")["item_name"].count().reset_index(name="count").sort_values(by="count", ascending=False).head(3)
        top_3_dict = {f"Puesto {i+1}": juego for i, juego in enumerate(recommend_counts['item_name'])}
        return top_3_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al obtener los juegos menos recomendados.")


@app.get('/sentiment_analysis/{anio}')
def sentiment_analysis(anio: int):

    '''
    Según el año de lanzamiento, se devuelve una lista con la cantidad de registros de reseñas de usuarios que se encuentren categorizados con un análisis de sentimiento.

    Args:
        año (int): Año para el cual se busca el análisis de sentimiento.

    Returns:
        dict: Diccionario con la cantidad de reseñas por sentimiento.
    '''
  
    try:    
        # Filtrar el DataFrame por el año
        filtered_df = df_dataExport[df_dataExport["release_anio"] == anio]

        # Contar las reseñas por sentimiento
        sentiment_counts = filtered_df["sentiment_analysis"].value_counts()

        # Mapear las categorías a los nombres esperados
        sentiment_mapping = {2: "Positive", 1: "Neutral", 0: "Negative"}
        sentiment_counts_mapped = {sentiment_mapping[key]: value for key, value in sentiment_counts.items()}

        return sentiment_counts_mapped
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=404, detail=f"No hay datos para el año {anio}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      

def presentacion():
    '''
    Genera una página de presentación HTML para la API Steam de consultas de videojuegos.
    
    Returns:
    str: Código HTML que muestra la página de presentación.
    '''
    return '''
        <html>
            <head>
                <title>API Steam</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        padding: 20px;
                    }
                    h1 {
                        color: #333;
                        text-align: center;
                    }
                    p {
                        color: #666;
                        text-align: center;
                        font-size: 18px;
                        margin-top: 20px;
                    }
                    foorter {
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                <h1>API de consultas de videojuegos de la plataforma Steam</h1>
                <p>Bienvenido a la API de Steam para consultas sobre la plataforma de videojuegos.</p>
                <p>Proyencto Individual N°1 - Henry<p>
                <p>INSTRUCCIONES:</p>
                <p>Escriba <span style="background-color: lightgray;">/docs</span> a continuación de la URL actual de esta página para interactuar con la API</p>
                <footer> Autor: Leonel Viscay <footer>
            </body>
        </html>
    '''