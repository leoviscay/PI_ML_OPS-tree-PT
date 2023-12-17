# Importaciones
from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import HTMLResponse
import api_functions as af
from api_functions import UsersRecommend
import importlib
importlib.reload(af)


# Se instancia la aplicación
app = FastAPI()

# Rutas

# Página de inicio
@app.get(path="/", response_class=HTMLResponse, tags=["Home"])
def home():
    return af.presentacion()

# Consultas Generales

@app.get(path='/PlayTimeGenre/{genero}', tags=["Consultas Generales"])
def play_time_genre(genero: str = Path(..., description="Género para el cual se busca el año con más horas jugadas(Ingresar formato 'Mxxx')")):
    return af.PlayTimeGenre(genero)

@app.get(path='/UserForGenre/{genero}', tags=["Consultas Generales"])
def user_for_genre(genero: str = Path(..., description="Género para el cual se busca el usuario con más horas jugadas y la acumulación de horas por año")):
    return af.UserForGenre(genero)


@app.get("/UsersRecommend/{anio}", tags=["Consultas Generales"])
def users_recommend(anio: int = Path(..., description="Año para el cual se busca el top 3 de juegos más recomendados")):
        try:
            result = UsersRecommend(anio)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get(path='/UsersNotRecommend/{anio}', tags=["Consultas Generales"])
def users_not_recommend(anio: int = Path(..., description="Año para el cual se busca el top 3 de juegos menos recomendados")):
    return af.UsersNotRecommend(anio)

@app.get(path='/sentiment_analysis/{anio}', tags=["Consultas Generales"])
def sentiment_analysis(anio: int = Path(..., description="Año para el cual se busca el análisis de sentimiento")):
    return af.sentiment_analysis(anio)

