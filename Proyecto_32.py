"""
Crear un archivo XML, donde se guarde el reporte de tipologia de datos de la practica de pizzas 
del bloque anterior y la recomendacion propuesta.
"""
import pandas as pd



def extract():
    """ Extraer los datos de los csv de la carpeta y guardarlos en sus respectivos dataframes """
    print('\tExtrayendo datos...')
    informe = pd.read_csv('data/informe_datos.csv')
    ingredientes = pd.read_csv('data/ingredientes_semana.csv')
    print('\tFin de la extraccion')
    return informe, ingredientes


def transform(informe, ingredientes):
    """ Transformacion de los datos, hay que devolverlos para que en la funcion load solo haya que guardarlos como xml """
    # Vamos a darle nombre a las columnas sin nombre de cada dataframe
    # (aquellas columnas que son Unnamed:0)
    print('\n\tTransformando datos...')
    informe.rename(columns={'Unnamed: 0':'seccion'}, inplace=True)
    ingredientes.rename(columns={'Unnamed: 0':'ingrediente'}, inplace=True)
    #print(informe.head())
    #print('\n\n',ingredientes.head())
    print('\tFin de la transformacion')
    return informe, ingredientes
    

def load(informe, ingredientes):
    """ Guardar los dataframes en un archivo xml """
    print('\n\tCargando datos...')
    informe.to_xml('output/informe.xml')
    ingredientes.to_xml('output/ingredientes.xml')
    print('\tFin de la carga')


if __name__ == '__main__':
    informe, ingredientes = extract()
    informe, ingredientes = transform(informe, ingredientes)
    load(informe, ingredientes)