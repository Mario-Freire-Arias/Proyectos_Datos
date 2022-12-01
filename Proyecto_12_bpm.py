import regex as re
import pandas as pd
import sys
"""
Hacer un recomendador de uno de los topics que elijáis, películas, música, 
series... En nuestro caso, música. Para ello tendréis que elegir un dataset 
en formato csv y montar este proceso a través de una ETL orquestada con uno 
de las herramientas que veamos en clase, y como opcional, montarlo para poder 
desplegarlo en un contendor (veremos más detalle en clase)

Vamos a hacer un recomendador de música en función del bpm de la canción.
Nota: bpm = beats per minute, el pulso por minuto de la canción
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
    # print('\n', df.head())


    #entrada = "\nEscoge un bpm por el que filtrar las canciones (margen de +-5): "
    
    # La expresión regular se usaría si, por ejemplo, quisiesemos filtrar por artista. 
    bpm = int(entrada)
    #regex = re.compile(entrada, re.IGNORECASE)

    # Podríamos cambiar la columna tempo a int para comparar, pero no es estrictamente necesario.
    # Además, no es perfecto, ya que estamos redondeando hacia abajo independientemente de los decimales. 
    # df['tempo'] = df['tempo'].astype(int)

    # Filtramos por bpm en un rango de +-5
    # Traducción: coge las filas del df que bumplan que bpm-5 <= tempo <= bpm+5
    df = df[(df['tempo'] >= bpm-5) & (df['tempo'] <= bpm+5)] 
    
    # Los ordenamos por posición más alta a la que llegaron en el top 
    # (suponemos que esto es un buen sistema de recomendación de canciones)
    df = df.sort_values('peak_rank')
    print('Estas son las canciones que hemos encontrado: ')
    print(df)
    
    return df

def load(data):
    #print(type(data))
    #print(data)
    nombre_archivo = input('\nIntroduce el nombre con el que guardar el archivo de recomendaciones (intro = por defecto): ')
    if nombre_archivo == '':
        data.to_csv("spotify_transformado_22.csv", index=False)
        print('Se ha guardado la lista de recomendaciones en el archivo recomendaciones_spotify_22.csv')
    else:
        data.to_csv(f'{nombre_archivo}.csv', index=False)
        print(f'Se ha guardado la lista de recomendaciones en el archivo {nombre_archivo}.csv')


if __name__ == '__main__':
    entrada = ' '.join(sys.argv[1:])
    df = extract()
    data = transform(df, entrada)
    load(data)
    # Ahora tenemos que hacer el recomendador, para ello tenemos que preguntar el bpm 
    # que le gusta al usuario y hacer un filtro de los datos para que nos muestre
    # las canciones que más se parecen a ese género de música que le gusta al usuario

    # Para hacer la recomendación en sí, vamos a filtrar las canciones que tengan un bpm similar (+-5)
    # al solicitado y mostraremos primero las que más alto llegaron en el top. 
    # Si Fede quiere, podemos preguntar cual fue la última canción que escuchó y le recomendamos la siguiente en esa lista.



