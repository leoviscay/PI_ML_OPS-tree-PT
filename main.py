# Importaciones
from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import HTMLResponse
import asyncio
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import os


# Se instancia la aplicación
app = FastAPI()

####################################### CARGA DE DATOS ###########################################
# Ruta del archivo Parquet Brotli
parquet_brotli_file_path = os.path.join(os.path.dirname(__file__), 'data/data_export_api_brotli.parquet')

try:
    # Intenta cargar el archivo Parquet con Brotli
    df_data = pd.read_parquet(parquet_brotli_file_path)

    df_data_muestra = df_data.sample(frac=0.001, random_state=42)

except FileNotFoundError:
    # Si el archivo no se encuentra, lanza una excepción HTTP
    raise HTTPException(status_code=500, detail="Error al cargar el archivo de datos comprimido con Brotli")


############################################ FUNCIONES ######################################

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
        # Filtrar el DataFrame por el género
        genero_filtrado = df_data_muestra.query(f"genres=='{genero}'")

        # Obtener el año con más horas jugadas
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
        # Cargar solo las columnas necesarias para esta función
        juegos_genero = df_data_muestra[['genres', 'release_anio', 'playtime_forever', 'user_id']].copy()

        condition = juegos_genero['genres'].apply(lambda x: genero in x)
        juegos_genero = juegos_genero[condition]

        juegos_genero['playtime_forever'] = juegos_genero['playtime_forever'] / 60
        juegos_genero['release_anio'] = pd.to_numeric(juegos_genero['release_anio'], errors='coerce')
        juegos_genero = juegos_genero[juegos_genero['release_anio'] >= 100]
        juegos_genero['Año'] = juegos_genero['release_anio']

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


    try:
        # Filtrar el DataFrame por el año
        filtered_df = df_data_muestra.query(f"reviews_anio == {anio}")

        # Filtrar el DataFrame por reseñas recomendadas
        filtered_df = filtered_df[filtered_df['reviews_recommend'] == True]

        # Filtrar el DataFrame por reseñas con sentimiento positivo o neutral
        filtered_df = filtered_df[filtered_df['sentiment_analysis'].isin([1, 2])]

        # Obtener el top 3 de juegos más recomendados
        recommend_counts = filtered_df.groupby('item_name')['item_name'].count().reset_index(name="count").sort_values(by="count", ascending=False).head(3)

        # Convertir el DataFrame a una lista
        top_3_dict = {f"Puesto {i+1}": juego for i, juego in enumerate(recommend_counts['item_name'])}
        
        return top_3_dict

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Error al cargar los archivos de datos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
   

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
        # Filtrar el DataFrame por el año
        filtered_df = df_data_muestra.query(f"reviews_anio == {anio}")
        

        # Filtrar el DataFrame por reseñas no recomendadas
        filtered_df = filtered_df[filtered_df['reviews_recommend'] == False]
        

        # Filtrar el DataFrame por reseñas con sentimiento negativo
        filtered_df = filtered_df[filtered_df['sentiment_analysis'] == 0]
        

        # Obtener el top 3 de juegos menos recomendados
        not_recommend_counts = filtered_df.groupby('item_name')['item_name'].count().reset_index(name="count").sort_values(by="count", ascending=False).head(3)
        

        # Convertir el DataFrame a una lista
        top_3_dict = {f"Puesto {i+1}": juego for i, juego in enumerate(not_recommend_counts['item_name'])}
        
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
        filtered_df = df_data_muestra.query(f"release_anio == {anio}")

        # Contar las reseñas por sentimiento
        sentiment_counts = filtered_df.groupby("sentiment_analysis")["sentiment_analysis"].size()

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
                        color: black; 
                        background-color: white; 
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
                    footer {
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

# Sistema de Recomendación Item-Item
@app.get("/recomendacion_juego/{product_id}")
async def recomendacion_juego(product_id: int = Path(..., description="ID del producto para obtener recomendaciones")):
    '''
    Esta función devuelve una lista de recomendaciones de juegos para un juego dado. 
    La función utiliza un algoritmo de recomendación de similitud coseno para calcular la similitud entre el juego dado 
    y todos los demás juegos en el conjunto de datos. 
    Los juegos más similares al juego dado se devuelven como recomendaciones.

    Args:
    product_id: El ID del juego para el que se desean las recomendaciones.

    Return:
    Un diccionario con dos claves:
    recomendaciones: Una lista de los nombres de los juegos recomendados.
    message: Un mensaje que indica si se encontraron recomendaciones o no.
    '''

   
    try:
        porcentaje_muestra = 50  # Definir el porcentaje de registros a seleccionar (ajusta según tus necesidades)

        # Obtener el número total de registros en el conjunto de datos
        total_registros = len(df_data_muestra)

        # Calcular el número de registros a seleccionar como un porcentaje del total
        num_registros = int(total_registros * (porcentaje_muestra / 100))

        # Limitar el conjunto de datos al porcentaje especificado de forma aleatoria
        df_subset = df_data_muestra.sample(n=num_registros, random_state=42).reset_index(drop=True)

        num_recommendations = 5  # Definir el número de recomendaciones como variable local

        juego_seleccionado = df_subset[df_subset['item_id'] == product_id]

        if juego_seleccionado.empty:
            raise HTTPException(status_code=404, detail=f"No se encontró el juego con ID {product_id}")

        title_game_and_genres = ' '.join(juego_seleccionado['item_name'].fillna('').astype(str) + ' ' + juego_seleccionado['genres'].fillna('').astype(str))

        # Obtener la matriz TF-IDF para todos los juegos en la muestra
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(df_subset['item_name'].fillna('').astype(str) + ' ' + df_subset['genres'].fillna('').astype(str))

        # Calcular la similitud solo para el juego seleccionado
        juego_tfidf = tfidf_vectorizer.transform([title_game_and_genres])
        similarity_scores = cosine_similarity(juego_tfidf, tfidf_matrix)

        if similarity_scores is not None:
            similar_games_indices = similarity_scores[0].argsort()[::-1]

            # Excluir el juego seleccionado de la lista de recomendaciones
            recommended_games = df_subset.loc[similar_games_indices[1:]]

            # Asegurarse de que los juegos recomendados estén presentes en el DataFrame original y sean distintos
            recommended_games = recommended_games[~recommended_games['item_id'].isin([product_id])].drop_duplicates(subset='item_name')

            recommendations_list = recommended_games.head(num_recommendations)['item_name'].tolist()

            if len(recommendations_list) < num_recommendations:
                # Si la cantidad de recomendaciones es menor a num_recommendations, llenar con valores nulos
                message = f"Se encontraron {len(recommendations_list)} recomendaciones para este ID."
                recommendations_list += [None] * (num_recommendations - len(recommendations_list))
            else:
                message = None

            return {"recomendaciones": recommendations_list, "message": message}
        else:
            # Si no hay similitud_scores, mostrar un mensaje
            return {"message": "No se encontraron juegos similares."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}") from e



######################################### Rutas #########################################################

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

@app.get(path='/recomendacion_juego/{product_id}', tags=["Sistema de Recomendación Item-Item"])
async def recomendacion_juego(product_id: int):
    return recomendacion_juego(product_id)