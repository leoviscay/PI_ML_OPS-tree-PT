<p align=center><img src=https://d31uz8lwfmyn8g.cloudfront.net/Assets/logo-henry-white-lg.png><p>

# <h1 align=center> **PROYECTO INDIVIDUAL N°1** </h1>
# <h2 align=center> ** Plataforma Steam Games ** </h2>

# <h1 align=center>**Machine Learning Operations (MLOps)**</h1>


# <h2 align=center>**INTRODUCCION**</h2>

<p style="text-indent: 20px;">
Este proyecto simula el rol de un MLOps Engineer, es decir, la combinación de un Data Engineer y Data Scientist, para la plataforma multinacional de videojuegos Steam. La tarea consiste en desarrollar un Producto Mínimo Viable utilizando datos proporcionados, con el objetivo de exhibir una API implementada en un servicio en la nube. El producto final debe incluir la aplicación de dos modelos de Machine Learning: en primer lugar, un análisis de sentimientos sobre los comentarios de los usuarios de los juegos, y en segundo lugar, la capacidad de recomendar juegos tanto a partir del nombre de un juego como de las preferencias de un usuario específico.
</p>


# <h2 align=center>**DATASETS**</h2>
<p style="text-indent: 20px;">
Para este proyecto se proporcionaron tres archivos JSON:

* australian_user_reviews.json es un dataset que contiene los comentarios que los usuarios realizaron sobre los juegos que consumen, además de datos adicionales como si recomiendan o no ese juego, emoticones de gracioso y estadísticas de si el comentario fue útil o no para otros usuarios. También presenta el id del usuario que comenta con su url del perfil y el id del juego que comenta.

* australian_users_items.json es un dataset que contiene información sobre los juegos que juegan todos los usuarios, así como el tiempo acumulado que cada usuario jugó a un determinado juego.

* output_steam_games.json es un dataset que contiene datos relacionados con los juegos en sí, como los título, el desarrollador, los precios, características técnicas, etiquetas, entre otros datos.
</p>


# <h2 align=center>**DESARROLLO de ETL**</h2>

<p style="text-indent: 20px;">
Se llevó a cabo el proceso de Extracción, Transformación y Carga (ETL) de los tres conjuntos de datos proporcionados. Dos de estos conjuntos de datos presentaban una estructura anidada, es decir, contenían columnas con diccionarios o listas de diccionarios. Se implementaron diversas estrategias para transformar las claves de estos diccionarios en columnas independientes. Posteriormente, se procedió a completar los valores nulos en variables esenciales para el proyecto. Además, se eliminaron aquellas columnas con un alto porcentaje de valores nulos o que no contribuían significativamente al proyecto, con el objetivo de optimizar el rendimiento de la API y considerando las limitaciones de almacenamiento en el despliegue. Todas estas transformaciones se llevaron a cabo utilizando la biblioteca Pandas.
</p>

<p style="text-indent: 20px;">
Los Dataset proporcionados para el presente práctico fueron provistos en tres unidaes de formato JSON, y con su descripción en un diccionario formato xls.
En primera instancia se leyeron los archivos, para luego comenzar al analisis explotarorio y modificacion de los mismos, a través de la ejecución de los mismos como DataFrames de Pandas. </p>

<p style="text-indent: 20px;">
En dos de los tres Dataset, se observó una estructura con contenido "anidado", es decir, contenían columnas con diccionarios o listas de diccionarios, el cual tuvo que ser desempaquetados para su extracción de datos. Esto permitió una mejor visualización de los contenidos, para su posterior transformación como eliminar o modificar datos nulos para evitar posteriores fallas de las funciones, renombrar columnas, etcétera. Además, se eliminaron aquellas columnas con un alto porcentaje de valores nulos o que no contribuían significativamente al proyecto, con el objetivo de optimizar el rendimiento de la API y considerando las limitaciones de almacenamiento en el despliegue. Todas estas transformaciones se llevaron a cabo utilizando la biblioteca Pandas.</p>

<p style="text-indent: 20px;">
En simultáneo, se iba estructurando el proyecto para su visualización y fácil acceso a los archivos y lectura de los mismos.
</p>

<p style="text-indent: 20px;">
  Estas transformaciones se pueden visualizar en: 
  <a href="https://github.com/leoviscay/PI_ML_OPS-tree-PT/blob/main/JupyterNotebooks/01_ETL_SteamGames.ipynb">ETL-Steam Games</a>, 
  <a href="https://github.com/leoviscay/PI_ML_OPS-tree-PT/blob/main/JupyterNotebooks/01_ETL_User_Items.ipynb">ETL-User Items</a>, 
  <a href="https://github.com/leoviscay/PI_ML_OPS-tree-PT/blob/main/JupyterNotebooks/01_ETL_User_Reviews.ipynb">ETL-User Reviews</a>
</p>


# <h2 align=center>**FEATURE ENGINEERING**</h2>

<p style="text-indent: 20px;">
Se recibió una solicitud específica para incorporar un análisis de sentimiento a los comentarios de los usuarios como parte de este proyecto. Para cumplir con este requerimiento, se introdujo una nueva columna denominada 'sentiment_analysis', la cual sustituye a la columna que originalmente contenía los comentarios de los usuarios. Esta nueva columna clasifica los sentimientos de los comentarios según la siguiente escala:

- 0 si el sentimiento es negativo,
- 1 si es neutral o si no hay un comentario asociado,
- 2 si el sentimiento es positivo.
</p>

<p style="text-indent: 20px;">
Dado que el propósito de este proyecto es llevar a cabo una prueba de concepto, se implementó un análisis de sentimiento básico utilizando TextBlob, una biblioteca de procesamiento de lenguaje natural (NLP) en Python. La meta de esta metodología es asignar un valor numérico a un texto, en este caso, a los comentarios que los usuarios dejaron para un juego específico. Este valor numérico representa si el sentimiento expresado en el texto es negativo, neutral o positivo.
</p>

<p style="text-indent: 20px;">
En términos de funcionamiento, esta metodología toma una revisión de texto como entrada, utiliza TextBlob para calcular la polaridad del sentimiento y luego clasifica la revisión como negativa, neutral o positiva en función de la polaridad calculada. Este enfoque proporciona una manera efectiva de cuantificar y categorizar los sentimientos expresados en los comentarios de los usuarios.
</p>

<p style="text-indent: 20px;">Realizadas todas las modificaciones solicitidas, y las que a criterio se requerian para la funcionalidad de este proyecto, se realizó una unificación de los Dataset para filtrar las columnas necesarias y generar un solo Dataframe que será el que "alimente" las funciones de ejecución de la API.
</p>

<p style="text-indent: 20px;">
  Este desarrollo se puede visualizar en: 
  <a href="https://github.com/leoviscay/PI_ML_OPS-tree-PT/blob/main/JupyterNotebooks/02_Feature_Enginner.ipynb">Fearure Engineering</a>. 
</p>


# <h2 align=center>**DESARROLLO de EDA**</h2>

<p style="text-indent: 20px;">
Se llevó a cabo un Análisis Exploratorio de Datos (EDA) en los tres conjuntos de datos que fueron sometidos al proceso de Extracción, Transformación y Carga (ETL), con el propósito de identificar las variables pertinentes para la creación del modelo de recomendación. En este análisis, se empleó la biblioteca Pandas para la manipulación de datos, y las librerías Matplotlib y Seaborn para la visualización.
</p>

<p style="text-indent: 20px;">
 Este desarrollo se puede visualizar en: 
  <a href="https://github.com/leoviscay/PI_ML_OPS-tree-PT/blob/main/JupyterNotebooks/03_EDA.ipynb">EDA</a>.
</p>


# <h2 align=center>**CONTENIDO DE LA API**</h2>

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

<p style="text-indent: 20px;">
El desarrollo del código que consume la API y el posterior servicio web, se puede visualizar en: 
 <a href="https://github.com/leoviscay/PI_ML_OPS-tree-PT/blob/main/main.py">main.py</a>
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

- [Ver Video](https://www.loom.com/share/f741b94830c6472cb4cafebc8defed8a)
