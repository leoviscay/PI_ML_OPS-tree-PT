from fastapi import FastAPI, HTTPException
import pandas as pd

app = FastAPI()

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
def UserForGenre(genero: str):
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
        genero_data = df_dataExport[condition]

        genero_data['playtime_forever'] = genero_data['playtime_forever'] / 60
        genero_data = genero_data[genero_data['posted'] >= 100]

        genero_data['Año'] = genero_data['posted']

        horas_por_usuario = genero_data.groupby(['user_id', 'Año'])['playtime_forever'].sum().reset_index()

        if not horas_por_usuario.empty:
            usuario_max_horas = horas_por_usuario.groupby('user_id')['playtime_forever'].sum().idxmax()
            usuario_max_horas = horas_por_usuario[horas_por_usuario['user_id'] == usuario_max_horas]
        else:
            usuario_max_horas = None

        acumulacion_horas = horas_por_usuario.groupby(['Año'])['playtime_forever'].sum().reset_index()
        acumulacion_horas = acumulacion_horas.rename(columns={'Año': 'Año', 'playtime_forever': 'Horas'})

        resultado = {
            "Usuario con más horas jugadas para " + genero: usuario_max_horas.to_dict(orient='records'),
            "Horas jugadas": acumulacion_horas.to_dict(orient='records')
        }

        return resultado

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
        reviews_filtradas = df_dataExport[(df_dataExport['release_anio'] == anio) & (df_dataExport['recommend'] == True) & (df_dataExport['sentiment_analysis'] >= 1)]

        if reviews_filtradas.empty:
            raise HTTPException(status_code=404, detail=f"No hay datos para el año {anio} con los filtros especificados.")

        recomendaciones_por_juego = reviews_filtradas.groupby('item_name')['recommend'].sum().reset_index()

        if recomendaciones_por_juego.empty:
            raise HTTPException(status_code=404, detail=f"No hay juegos recomendados para el año {anio} con los filtros especificados.")

        top_juegos_recomendados = recomendaciones_por_juego.nlargest(3, 'recommend')

        resultado = [{"Puesto 1": top_juegos_recomendados.iloc[0]['item_name']},
                     {"Puesto 2": top_juegos_recomendados.iloc[1]['item_name']},
                     {"Puesto 3": top_juegos_recomendados.iloc[2]['item_name']}]

        return resultado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/UsersNotRecommend/{anio}')
def UsersNotRecommend(anio: int):
    '''
    Datos:
    - anio (int): Año para el cual se busca el top 3 de juegos menos recomendados.

    Funcionalidad:
    - Devuelve el top 3 de juegos menos recomendados por usuarios para el año dado.

    Return:
    - List: [{"Puesto 1": str}, {"Puesto 2": str}, {"Puesto 3": str}]
    '''
    try:
        reviews_filtradas = df_dataExport[(df_dataExport['release_anio'] == anio) & (df_dataExport['recommend'] == False) & (df_dataExport['sentiment_analysis'] == 0)]

        if reviews_filtradas.empty:
            raise HTTPException(status_code=404, detail=f"No hay datos de juegos menos recomendados para el año {anio} con los filtros especificados.")

        juegos_menos_recomendados = reviews_filtradas['item_name'].value_counts().reset_index()
        juegos_menos_recomendados.columns = ['item_name', 'count']

        top_juegos_menos_recomendados = juegos_menos_recomendados.nlargest(3, 'count')

        resultado = [{"Puesto 1": top_juegos_menos_recomendados.iloc[0]['item_name']},
                     {"Puesto 2": top_juegos_menos_recomendados.iloc[1]['item_name']},
                     {"Puesto 3": top_juegos_menos_recomendados.iloc[2]['item_name']}]

        return resultado

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
                </style>
            </head>
            <body>
                <h1>API de consultas de videojuegos de la plataforma Steam</h1>
                <p>Bienvenido a la API de Steam donde se pueden hacer diferentes consultas sobre la plataforma de videojuegos.</p>
                <p>INSTRUCCIONES:</p>
                <p>Escriba <span style="background-color: lightgray;">/docs</span> a continuación de la URL actual de esta página para interactuar con la API</p>
            </body>
        </html>
    '''
