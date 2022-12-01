import pandas as pd
import numpy as np
import re
import dateutil.parser as dparser
import datetime
import time

def extract():
    orders = pd.read_csv('data/orders.csv', delimiter=';')
    # COLUMNAS ORDERS: order_id, date, time
    details = pd.read_csv('data/order_details.csv', delimiter=';')
    # COLUMNAS DETAILS: order_details_id, order_id, pizza_id, quantity
    return orders, details

def transform(orders, details):
    """
    Tenemos que limpiar los datos de de orders y order_details. Esto significa:
        - eliminar nulos
        - eliminar nans
        - eliminar duplicados
        - uniformizar los datos (ej: si uno es 'USA' y otro 'U.S.a', hay que ponerlos iguales. Para ello, usaremos REGEX)
            · dar formato uniforme a todo: fechas, ordenar por id de pedido, etc.
    """

    # limpiamos orders
    orders_limpio = limpiar_orders(orders)

    # limpiamos details
    details_limpio = limpiar_details(details)

    return orders_limpio, details_limpio

def load(orders, details):
    # cargamos los datos en un csv distinto por df, dentro de la carpeta output
    orders.to_csv('output/orders_limpio.csv', index=False)
    details.to_csv('output/details_limpio.csv', index=False)



def limpiar_orders(orders):
    """
    Funcion que tiene por objetivo uniformizar los datos de orders.
    
    Pasos:
        1. Ordenar el df por id de pedido (esto es el orden verdadero, ya que se va incrementando conforme se van haciendo pedidos,
        por tanto, sabemos que si un id es mayor, va despues en el tiempo que otro id menor)
        2. Rellenar nulos mediante ffill para fechas y horas, a fin de reconstruir cuantos más datos mejor
        (hacemos un ffill porque la mayoría de pedidos se concentran en las horas centrales del día)
        3. Dar formato uniforme a fechas y horas
        4. 
    """
    print('Procesando orders...')

    orders = orders.sort_values(by=['order_id'], ascending=True, ignore_index=True) # ordenamos los datos por id de pedido

    orders = rellenar_orders_nulos(orders) # si falta alguna fecha u hora, la rellenamos con la anterior.
    
    # formateamos las fechas
    orders['date'] = orders.apply(lambda row: formatear_fecha(row), axis=1)

    # formateamos la hora
    orders['time'] = orders.apply(lambda row: formatear_hora(row), axis=1)

    # rellenamos las horas que estén vacías (todas que sean 25:00:00)
    orders['time'] = orders.apply(lambda row: rellenar_horas_nulas(row), axis=1)

    # corregimos las horas de los pedidos (si es a las 00:00:00, le pasamos la hora que tiene la fecha)
    orders['time'] = orders.apply(lambda row: corregir_horas(row), axis=1)

    # hacemos que date pase de ser yyyy-mm-dd HH:MM:SS a dd/mm/yyyy
    orders['date'] = orders.apply(lambda row: recortar_fechas(str(row['date'])), axis=1)

    print('Orders procesado.')
    return orders

def rellenar_orders_nulos(orders):
    """
    Funcion que rellena los nulos de orders en funcion de los valores de sus vecinos.
    """
    # rellenamos las nulas para intentar reconstruirlos con los datos que tenemos
    orders['date'] = orders['date'].fillna(method='ffill')
    orders['time'] = orders['time'].fillna(method='ffill')

    return orders

def formatear_fecha(linea_df):
    """ Funcion que da formato a las fechas de orders """
    # tenemos que tener en cuenta también las fechas que son el numero de segundos a partir de que un tio
    # decidio ponerlo como estandar (POSIX timestamp)
    try:
        try:
            # convert type to int
            linea_df['date'] = int(linea_df['date'])
            # convert from POSIX timestamp to datetime
            return datetime.datetime.fromtimestamp(linea_df['date']).strftime('%d/%m/%Y')

        except:
            return dparser.parse(str(linea_df['date']), fuzzy=True)
    except:
        cadena = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(float(linea_df['date']))))
        return cadena

def formatear_hora(linea_df):
    """ Funcion que da formato a las horas de orders """

    """
    Posibles formatos:
        {HH}:{MM} {AM|PM}, {HH}:{MM}:{SS}, {HH}H {MM}M {SS}S
    Ejemplos:
        18:58 PM, 14:36:32, 21H 28M 27S
    

    Queremos unificarlos todos a un único formato de 24h,
        horas:minutos:segundos
    """
    try:
        linea_df['time'] = str(linea_df['time'])

        if 'PM' in linea_df['time'] or 'AM' in linea_df['time']:
            # formato {HH}:{MM} {AM|PM}
            hora_dia = linea_df['time'].split(' ')[0]
            hora_dia += ':00'
            return hora_dia

        elif 'H' in linea_df['time']:
            # formato {HH}H {MM}M {SS}S
            hora_dia = linea_df['time'].split(' ')
            hora_dia = hora_dia[0][:-1] + ':' + hora_dia[1][:-1] + ':' + hora_dia[2][:-1]
            return hora_dia
        
        elif ':' in linea_df['time']:
            # formato {HH}:{MM}:{SS}
            # este formato es el que queríamos, asi que no lo tocamos
            return linea_df['time']

        else:
            # campo vacío
            # vamos a fijar una hora NO VALIDA por defecto, para hacer comprobaciones luego
            return '25:00:00'
    
    except:
        return 'ERROR'

def rellenar_horas_nulas(linea_df):
    """
    Tenemos un conjunto de horas que nos dieron error, por lo que fijamos que fuesen una hora no válida,
        25:00:00
    Puede darse el caso que en el campo fecha si que haya una hora, por lo que en ese caso, vamos a tomarla
    y fijarla como hora del pedido.

    El campo hora es una cadena de formato {HH}:{MM}:{SS}
    El campo fecha es un objeto datetime
    """
    if linea_df['time'] != '25:00:00':
        return linea_df['time']
    else:
        if linea_df['date'] != 'ERROR':
            return linea_df['date'].strftime('%H:%M:%S')
        else:
            return '00:00:00'

def corregir_horas(linea_df):
    """
    Tenemos una linea del df ya con todo homogeneizado. Vamos a intentar recuperar la hora del pedido, si es posible.
    Para ello, tenemos una fecha en formato yyyy-mm-dd HH:MM:SS y una hora en formato HH:MM:SS
    Si nuestra hora es 00:00:00 y la hora que marca nuestra fecha no lo es, hacemos que la hora sea la de la fecha.
    Si ambas son 00:00:00, dejamos el campo vacío (para luego eliminarlo con un dropna en el df)
    """
    # columnas: order_id; date; time
    if linea_df['time'] == '00:00:00':
        if '00:00:00' in str(linea_df['date']):
            return np.nan
        else:
            # fecha = 'yyyy-mm-dd HH:MM:SS'
            # devolvemos los 8 últimos caracteres de la cadena
            return str(linea_df['date'])[-8:]
    else:
        return linea_df['time']

def recortar_fechas(fila_df):
    """
    Funcion que coje la fila 'date' de df de order_details en formato yyyy-mm-dd hh:mm:ss y devuelve
    exclusivamente la fecha en formato dd/mm/yyyy
    """
    fecha = fila_df[:10].split('-')
    return fecha[2] + '/' + fecha[1] + '/' + fecha[0]

def cambiar_formato_fecha(fila_df):
    """
    Funcion que coje la fila 'date' de df de order_details en formato yyyy-mm-dd y devuelve
    exclusivamente la fecha en formato dd/mm/yyyy
    """
    lista = fila_df['date'].split('-')
    return lista[2] + '/' + lista[1] + '/' + lista[0]



def limpiar_details(details):
    """
    Funcion que tiene por objetivo uniformizar los datos de details.

    # COLUMNAS DE details: order_details_id, order_id, pizza_id, quantity
    """
    # vamos a ir iterando por las filas del df y corrigiendo los errores que vayamos encontrando
    """
    droppear todas las filas que tengan algún nulo en cualquiera de sus columnas (si tiene nulo, no vale)

    hacer un .lower() de las strings de las columnas order_id, pizza_id y quantity
    """
    print('Procesando details...')
    
    # eliminamos nulos
    details = details.dropna()

    # pasamos todas las columnas a minúsculas
    details['order_id'].astype(str).str.lower()
    details['pizza_id'].astype(str).str.lower()
    details['quantity'].astype(str).str.lower()
    
    details['pizza_id'] = details.apply(lambda row: cambios_pizza_id(row['pizza_id']), axis=1)
    details['quantity'] = details.apply(lambda row: cambios_quantity(row['quantity']), axis=1)
    
    # ordenamos details según order_details_id
    details = details.sort_values(by=['order_details_id'], ascending=True, ignore_index=True)
    #print(details.head(20))
    print('Details procesado.')

    return details

def cambios_pizza_id(fila_df):
    cambios = {'-':'_', ' ':'_', '@':'a', '0':'o', '3':'e', '5':'s', '8':'b', '9':'g'}
    for caracter in cambios.keys():
        if caracter in fila_df:
            fila_df = fila_df.replace(caracter, cambios[caracter])
    return fila_df

def cambios_quantity(fila_df):
    cambios = {'-':'', 'one':'1', 'two':'2', 'three':'3', 'four':'4', 'five':'5', 'six':'6', 'seven':'7', 'eight':'8', 'nine':'9', 'ten':'10'}
    for caracter in cambios.keys():
        if caracter in fila_df.lower():
            fila_df = fila_df.lower().replace(caracter, cambios[caracter])
    return fila_df


def Informe_Datos(orders, details):
    """
    Funcion que hace un informe de calidad de los datos, reflejando la tipología de cada columna y el numero 
    de NaN y Null por cada columna
    """
    print('Informe de datos de orders.csv')
    # vamos a reflejar el tipo de dato por columna
    print(orders.dtypes)
    # vamos a reflejar el numero de nulos por columna
    print(orders.isnull().sum())
    # vamos a reflejar el numero de nulos totales
    print('Numero de nulos totales: ', orders.isnull().sum().sum())

    print('\nInforme de datos de details.csv')
    # vamos a reflejar el tipo de dato por columna
    print(details.dtypes)
    # vamos a reflejar el numero de nulos por columna
    print(details.isnull().sum())
    # vamos a reflejar el numero de nulos totales
    print('Numero de nulos totales: ', details.isnull().sum().sum())

if __name__ == '__main__':
    orders, details = extract()
    Informe_Datos(orders, details)
    orders, details = transform(orders, details)
    load(orders, details)