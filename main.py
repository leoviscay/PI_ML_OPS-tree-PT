# Importaciones
from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import HTMLResponse
import api_functions as af
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
def play_time_genre(genero: str = Path(..., description="Género para el cual se busca el año con más horas jugadas")):
    return af.PlayTimeGenre(genero)

@app.get(path='/UserForGenre/{genero}', tags=["Consultas Generales"])
def user_for_genre(genero: str = Path(..., description="Género para el cual se busca el usuario con más horas jugadas y la acumulación de horas por año")):
    return af.UserForGenre(genero)

@app.get(path='/UsersRecommend/{anio}', tags=["Consultas Generales"])
def users_recommend(anio: int = Path(..., description="Año para el cual se busca el top 3 de juegos más recomendados")):
    return af.UsersRecommend(anio)

@app.get(path='/UsersNotRecommend/{anio}', tags=["Consultas Generales"])
def users_not_recommend(anio: int = Path(..., description="Año para el cual se busca el top 3 de juegos menos recomendados")):
    return af.UsersNotRecommend(anio)

# Resto de las rutas...
