import re
import pandas as pd
import sys

"""
fuente del dataframe: https://www.kaggle.com/leonardopena/top-spotify-songs-from-20102019-by-year
Vamos a hacer un recomendador de música (canciones de Spotify). 
Para ello hemos elegido un dataset en formato csv (spotify_top_charts_22.csv) y montar este 
proceso a través de una ETL. 
Lo intentaremos montar para poder desplegarlo en un contendor (veremos más detalle en clase)

Vamos a hacer un recomendador de música en función de un artista introducido.
"""

# Subirlo a un repositorio y pasar el link también.

def extract():
    df = pd.read_csv("data/spotify_top_charts_22.csv")
    print('\nSe han cargado los datos.')
    return df


def transform(df, entrada):
    # Vamos a descartar las columnas que no nos interesan
    df = df.drop(columns=["uri", "weeks_on_chart", "danceability", "energy", "key", "loudness", 
        "speechiness", "acousticness", "instrumentalness", "liveness", "time_signature", "duration_ms", "mode"])
    # Nos estamos quedando con el nombre de la canción, artistas, posición más alta en el ránking y el bpm.


    #print('Vamos a filtrar los datos por el nombre (o parte del nombre) de un artista o grupo.')
    #print('Por ejemplo, si queremos las canciones de The Beatles, escribimos "The Beatles", "Beatles" \no algo entre medias como "e Beatles".')
    #entrada = input("\nIntroduce el término por el que filtrar: ")
    #print(entrada)
    # Vamos a buscar la palabra introducida en el nombre de los artistas usando expresiones regulares
    regx = f'.*{entrada}.*' # generamos la expresión regular

    # Vamos filtrar el dataframe por la expresion regular en las columnas "artist_names" y "track_name", ignorando
    # mayusuclas y minusculas usando regex para ello. Cada filtrado se guarda en un dataframe diferente, que luego concatenamos.
    df_artista_principal = df[df['artist_names'].str.contains(re.compile(regx, flags=re.IGNORECASE))]

    df_artista_colaborador = df[df['track_name'].str.contains(re.compile(regx, flags=re.IGNORECASE))]


    # Juntamos los dataframes en uno, eliminamos duplicados y corregimos los índices del df resultante
    df = pd.concat([df_artista_principal, df_artista_colaborador]).drop_duplicates().reset_index(drop=True)
    

    # Los ordenamos por posición más alta a la que llegaron en el top 
    # (suponemos que esto es un buen sistema de recomendación de canciones)
    df = df.sort_values('peak_rank')
    print('\nEstas son las canciones que hemos encontrado:')
    print(df)
    
    return df


def load(data):
    nombre_archivo = input('\nIntroduce el nombre con el que guardar el archivo de recomendaciones (intro = por defecto): ')
    if nombre_archivo == '':
        data.to_csv("resultado_de_filtrar.csv", index=False)
        print('Se ha guardado la lista de recomendaciones en el archivo recomendaciones_spotify_22.csv')
    else:
        data.to_csv(f'{nombre_archivo}.csv', index=False)
        print(f'Se ha guardado la lista de recomendaciones en el archivo {nombre_archivo}.csv')


if __name__ == '__main__':
    entrada = ' '.join(sys.argv[1:])
    #print(entrada)
    df = extract()
    data = transform(df, entrada)
    load(data)
    