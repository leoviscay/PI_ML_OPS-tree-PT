<p align=center><img src=https://d31uz8lwfmyn8g.cloudfront.net/Assets/logo-henry-white-lg.png><p>

# <h1 align=center> **PROYECTO INDIVIDUAL N°1** </h1>
# <h2 align=center> ** Dataset: Steam Games** </h2>

# <h1 align=center>**Machine Learning Operations (MLOps)**</h1>

<p align="center">
<img src="https://user-images.githubusercontent.com/67664604/217914153-1eb00e25-ac08-4dfa-aaf8-53c09038f082.png"  height=300>
</p>

# <h2 align=center>**DESARROLLO de ETL y EDA**</h2>

<p style="text-indent: 20px;">
Los Dataset proporcionados para el presente práctico fueron provistos en tres unidaes de formato JSON, y con la descripción de los mismos en un diccionario formato xls.
En primera instancia se leyeron los archivos, para luego comenzar al analisis explotarorio y modificacion de los mismos, a través de la ejecución de los mismos como DataFrames de Pandas. </p>

<p style="text-indent: 20px;">
En dos de los tres Dataset, se observó una columna con contenido "anidado", el cual tuvo que ser desempaquetados para su extracción de datos. Esto permitió una mejor visualización de los contenidos, para su posterior transformación como eliminar o modificar datos nulos para evitar posteriores fallas de las funciones, renombrar columnas, etcétera.</p>

<p style="text-indent: 20px;">Una vez realizado este primer analísis, se guardaron los archivos provistos en distintos formatos de mejor legibilidad, por ejemplo .csv, y posteriormente en archivo .parquet para optimizar espacio.</p>

<p style="text-indent: 20px;">Posteriormente, se realizó sobre el DataFrame de reviews, la transformación solicitada para la creación de una columna de analisis de sentimiento a través de los datos provistos en una de las columnas anidadas. Este procedimiento se hizo con TextBlob.</p>

<p style="text-indent: 20px;">Realizada todas las modificaciones solicitidas, y las que a criterio se requerian para la funcionalidad de este proyecto, se realizó una unificación de los Dataset para filtrar las columnas necesarias y generar un solo Dataframe que será el que "alimente" las funciones de ejecución de la API.
</p>

<p style="text-indent: 20px;">
En simultáneo, se iba estructurando el proyecto para su visualización y fácil acceso a los archivos y lectura de los mismos.
</p>

# <h2 align=center>**CONTENIDO DE LA API**</h2>
La API, el cual esta en Render contiene 5 funciones y un sistema de recomendacion los cuales fueron solicitados, los cuales realizan el funcionamiento de top juegos, horas jugadas por determinados usuarios, año en donde tuvo un gran recibimiento los juegos, entre otros. Con respecto al sistema de recomendacion nos retornara 5 juegos similares, con respecto al juego que buscamos mediante el id

<p style="text-indent: 20px;">
El desarrollo de la API se realizó usando el framework FastAPI, con el fin de responder 5 (cinco) consultas propuestas y un sistema de recomendación, eligiendo para el presente el sistema ítem-ítem.
</p>

<p style="text-indent: 20px;">
Como se mencionara anteriormente, esta API se "alimentó" del DataFrame creado en el EDA y ETL de los datos, y su propósito era responder expresamente:

    * PlayTimeGenre: Debe devolver año con mas horas jugadas para dicho género.

    * UserForGenre: Debe devolver el usuario que acumula más horas jugadas para el género dado y una lista de la acumulación de horas jugadas por año.

    * UsersRecommend: Devuelve el top 3 de juegos MÁS recomendados por usuarios para el año dado.

    * UsersNotRecommend: Devuelve el top 3 de juegos MENOS recomendados por usuarios para el año dado.

    * sentiment_analysis( año : int ): Según el año de lanzamiento, se devuelve una lista con la cantidad de registros de reseñas de usuarios que se encuentren categorizados con un análisis de sentimiento.
</p>

<p style="text-indent: 20px;">
Luego, se realizó el sistema de recomendación Ítem-Ítem, para obtener el resultado de:

    * recomendacion_juego( id de producto ): Ingresando el id de producto, deberíamos recibir una lista con 5 juegos recomendados similares al ingresado

</p>


# <h2 align=center>**DEPLOYMENT**</h2>

<p style="text-indent: 20px;">
Con la API funcionando a nivel local, se procedió a Render, como servicio para que la API pueda ser consumida desde la web. En el transcurso de este proceso, se evaluaron múltiples alternativas para que funcionara la versión gratuita de este servicio.
</p>

<p style="text-indent: 20px;">
A fin de mostrar el funcionamiento de la API, se optó por un muestreo porcentual y aleatorio del DataFrame formado en el EDA y ETL, para que consuma datos y pueda responder a las consultas solicitadas.
</p>

# <h2 align=center>**LINKS**</h2>

## Repositorio

- [GitHub Repository](https://github.com/leoviscay/PI_ML_OPS-tree-PT)

## Deploy

- [Render Deployment](https://pi-steamgames-ipmi.onrender.com/)

## Demo

[![Watch the Video]