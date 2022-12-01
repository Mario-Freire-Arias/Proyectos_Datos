"""
Hacer un buscador de leaks en commits de github, para ello hay que usar pandas y expresiones
regulares además del arquetipo que hemos trabajado en clase, como optativo, montarlo todo 
en una imagen docker y hacer una barra de progreso para ver que esta haciendo nuestra ETL.

Subirlo a un repositorio y pasar el link también.
"""

#! user/bin/python3
# Path: Practica1.py
from git import Repo
import re, signal, time, sys
import pandas as pd


# Función para capturar la señal de interrupción Ctrl+C
def signal_handler():
    print('Se ha introducido Ctrl+C.')
    print('Terminando programa...')
    sys.exit(0)


def extract(repo_dir):
    """
    FUNCION QUE, DADO UN REPOSITORIO DE GIT, DEVUELVE UNA LISTA DE COMMITS
    DE LOS QUE HAY QUE SACAR LOS LEAKS.
        Recibe el directorio del repositorio y devuelve una lista de commits    
    """
    print('Extrayendo datos...')
    repo = Repo(repo_dir)
    commits = list(repo.iter_commits('develop'))
    print('Datos extraidos')
    return commits


def transform(commits):
    """
    FUNCION QUE, DADA UNA LISTA DE COMMITS, DEVUELVE UN DATAFRAME CON LOS LEAKS
    DE LOS COMMITS QUE SE HAN ENCONTRADO.
        Recibe una lista de commits y devuelve un dataframe con los leaks
    """
    print('Transformando datos...')
    # -filtramos los commits con sus mensajes y guardamos en un df- 
    df = pd.DataFrame(columns=['commit', 'message']) #creamos un dataframe vacio
    for commit in commits:
        for word in KEY_WORDS: # buscamos las palabras clave en los mensajes de los commits
            if re.search(word, commit.message, re.IGNORECASE):
                df = df.append({'commit': commit.hexsha, 'message': commit.message}, ignore_index=True)
                """
                NOTA:
                    A la hora de ejecutar el programa, sale un mensaje que nos advierte que,
                    en el futuro, .append() se va a quedar obsoleto y eliminar de pandas. 
                    Sin embargo, esto no afecta a la ejecucion del programa, por lo que lo
                    podemos seguir usando sin problema.
                """
    print('Datos transformados')
    return df
    
        
def load(dataframe_datos):
    """
    FUNCION DE CARGA DE DATOS:
        Recibimos un dataframe de pandas con los datos conseguidos y los guardamos en un .csv
    """
    # -guardamos el df en un csv-
    print('Guardando datos en un csv...')
    dataframe_datos.to_csv('leaks.csv', index=False)
    print('Datos guardados en leaks.csv')
    time.sleep(1)
    
    

if __name__ == '__main__':
    """ PARTE PRINCIPAL DEL PROGRAMA, EXTRAEMOS, TRANSFORMAMOS Y CARGAMOS LOS DATOS """
    
    # -definimos las palabras clave para buscar leaks y las hacemos globales- 
    global KEY_WORDS, REPO_DIR
    KEY_WORDS = ['credentials', 'password', 'key', 'username']
    REPO_DIR = './skale/skale-manager'

    # -definimos el signal handler-
    signal.signal(signal.SIGINT, signal_handler)

    print('Extrayendo datos...')
    commits = extract(REPO_DIR)
    print('Extracción completada.')

    print('Transformando datos...')
    dataframe_leaks = transform(commits)
    print('Transformación completada.')

    print('Cargando datos...')
    load(dataframe_leaks)
    print('Carga de datos completada.')

    sys.exit(0)
