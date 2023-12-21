# Importaciones
from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import HTMLResponse
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
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

# Crear una matriz de usuario-ítem
user_item_matrix = pd.pivot_table(df_dataExport, values='playtime_forever', index='user_id', columns='item_name', fill_value=0)

# Calcular la similitud del coseno entre usuarios
user_similarity = cosine_similarity(user_item_matrix)

# Función para obtener recomendaciones de ítems para un usuario
def recomendacion_usuario(user_id):
    '''
    Esta función toma un ID de producto como entrada y devuelve una lista de 5 juegos recomendados que son similares al juego especificado.

    Args:
    product_id (str): El ID del producto (juego) para el cual se desean obtener recomendaciones.
   
    Return:
    Lista de 5 juegos recomendados (str).
    '''
    idx = user_encoder.transform([user_id])[0]
    sim_scores = list(enumerate(user_similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_users = [item[0] for item in sim_scores[1:6]]  # Obtener los 5 usuarios más similares (excluyendo el propio)
    
    recommendations = []
    for user in sim_users:
        liked_items = user_item_matrix.loc[user].sort_values(ascending=False).index[:5].tolist()
        recommendations.extend(liked_items)

    return list(set(recommendations))

#############

from sklearn.metrics.pairwise import cosine_similarity

# Codificar etiquetas de usuario e ítem
user_encoder = LabelEncoder()
item_encoder = LabelEncoder()

df_dataExport['user_id'] = user_encoder.fit_transform(df_dataExport['user_id'])
df_dataExport['item_id'] = item_encoder.fit_transform(df_dataExport['item_name'])

# Crear una matriz de usuario-ítem
user_item_matrix = pd.pivot_table(df_dataExport, values='playtime_forever', index='user_id', columns='item_name', fill_value=0)

# Calcular la similitud del coseno entre usuarios
user_similarity = cosine_similarity(user_item_matrix)

# Función para obtener recomendaciones de ítems para un usuario
def recomendacion_usuario(user_id):

    '''
    Esta función toma un ID de usuario como entrada y devuelve una lista de 5 juegos recomendados para ese usuario en función de la similitud de usuarios.

    Parámetros:
    user_id (str): El ID del usuario para el cual se desean obtener recomendaciones.
    Salida:
    Lista de 5 juegos recomendados (str) para el usuario especificado.
    '''
    idx = user_encoder.transform([user_id])[0]
    sim_scores = list(enumerate(user_similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_users = [item[0] for item in sim_scores[1:6]]  # Obtener los 5 usuarios más similares (excluyendo el propio)
    
    recommendations = []
    for user in sim_users:
        liked_items = user_item_matrix.loc[user].sort_values(ascending=False).index[:5].tolist()
        recommendations.extend(liked_items)

    return list(set(recommendations))

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
def recomendacion_juego(product_id: str = Path(..., description="ID del producto para obtener recomendaciones")):
    # Llama a tu función de recomendación item-item aquí
    recommendations = recomendacion_juego(product_id)
    return {"recomendaciones": recommendations}

# Sistema de Recomendación User-Item
@app.get("/recomendacion_usuario/{user_id}", tags=["Sistema de Recomendación User-Item"])
def recomendacion_usuario(user_id: str = Path(..., description="ID del usuario para obtener recomendaciones")):
    # Llama a tu función de recomendación user-item aquí
    recommendations_usuario = recomendacion_usuario(user_id)
    return {"recomendaciones_usuario": recommendations_usuario}