# Importaciones
from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import HTMLResponse
import asyncio
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


# Se instancia la aplicación
app = FastAPI()

############################################ FUNCIONES ######################################

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


##################################### ML ###########################################################

def obtener_recomendaciones(id_juego):
    try:
        # Busca el juego en el DataFrame por ID
        juego_seleccionado = df_dataExport[df_dataExport['item_id'] == id_juego]

        # Verifica si el juego con el ID especificado existe
        if juego_seleccionado.empty:
            raise HTTPException(status_code=404, detail=f"No se encontró el juego con ID {id_juego}")

        title_game_and_genres = ' '.join(juego_seleccionado['item_name'].fillna('').astype(str) + ' ' + juego_seleccionado['genres'].fillna('').astype(str))
       
        tfidf_vectorizer = TfidfVectorizer()
        similarity_scores = None

        chunk_tags_and_genres = df_dataExport['item_name'].fillna('').astype(str) + ' ' + df_dataExport['genres'].fillna('').astype(str)
        games_to_compare = [title_game_and_genres] + chunk_tags_and_genres.tolist()

        tfidf_matrix = tfidf_vectorizer.fit_transform(games_to_compare)

        similarity_scores = cosine_similarity(tfidf_matrix)

        if similarity_scores is not None:
            similar_games_indices = similarity_scores[0].argsort()[::-1]

            num_recommendations = 5
            recommended_games = df_dataExport.loc[similar_games_indices[1:num_recommendations + 1]]

            # Devuelve un diccionario con los nombres de los juegos recomendados
            return {"recomendaciones": recommended_games['item_name'].tolist()}

        return {"message": "No se encontraron juegos similares."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}") from e


###################################### Rutas #########################################################

# Página de inicio
@app.get(path="/", response_class=HTMLResponse, tags=["Home"])
def home():
    return presentacion()

# Consultas Generales

@app.get(path='/PlayTimeGenre/{genero}', tags=["Consultas Generales"])
def play_time_genre(genero: str = Path(..., description="Género para el cual se busca el año con más horas jugadas(Ingresar formato 'Mxxx')")):
    return PlayTimeGenre(genero)

@app.get(path='/UserForGenre/{genero}', tags=["Consultas Generales"])
def user_for_genre(genero: str = Path(..., description="Género para el cual se busca el usuario con más horas jugadas y la acumulación de horas por año")):
    return UserForGenre(genero)


@app.get("/UsersRecommend/{anio}", tags=["Consultas Generales"])
def users_recommend(anio: int = Path(..., description="Año para el cual se busca el top 3 de juegos más recomendados")):
        try:
            result = UsersRecommend(anio)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get(path='/UsersNotRecommend/{anio}', tags=["Consultas Generales"])
def users_not_recommend(anio: int = Path(..., description="Año para el cual se busca el top 3 de juegos menos recomendados")):
    return UsersNotRecommend(anio)

@app.get(path='/sentiment_analysis/{anio}', tags=["Consultas Generales"])
def sentiment_analysis(anio: int = Path(..., description="Año para el cual se busca el análisis de sentimiento")):
    return sentiment_analysis(anio)

# Sistema de Recomendación Item-Item
@app.get("/recomendacion_juego/{product_id}", tags=["Sistema de Recomendación Item-Item"])
async def endpoint_recomendacion_juego(product_id: int = Path(..., description="ID del producto para obtener recomendaciones")):
    try:
        # Validación del tipo de entrada
        if not isinstance(product_id, int):
            raise HTTPException(status_code=422, detail="El ID del juego debe ser un número entero")

        # Llama a tu función de recomendación item-item de manera asíncrona
        loop = asyncio.get_event_loop()
        recommendations = await loop.run_in_executor(None, obtener_recomendaciones, product_id)
        return recommendations

    except HTTPException as e:
        raise e  # Mantén el manejo de excepciones HTTP para devolver los códigos de estado adecuados

    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Error: Columna no encontrada - {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}") from e
