"""
Generar un fichero excel con un reporte ejecutivo, un reporte de ingredientes, un reporte de pedidos 
(uno por cada hoja en el fichero de excel) para el dataset de Maven Pizzas trabajado en el bloque 3
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xlsxwriter


def extract():
    """
    Función que extrae los datos del fichero csv
    """
    pedidos = pd.read_csv("data/orders.csv")
    ingredientes = pd.read_csv("data/ingredientes_semana.csv")
    detalles = pd.read_csv("data/order_details.csv")

    return pedidos, ingredientes, detalles


def transform(pedidos, ingredientes, detalles):
    """ Función que transforma los datos """
    # le  cambiamos el nombre a la columna que no tiene nombre:
    ingredientes.rename(columns={'Unnamed: 0': 'ingrediente', 'count': 'weekly count'}, inplace=True)
    detalles = Separar_Tipo_Tamaño(detalles)

    """
    Vamos a convertir la columna date de pedidos en una columna de tipo datetime, para poder trabajar con ella
    """
    pedidos['date'] = pd.to_datetime(pedidos['date'], format='%d/%m/%Y')

    return pedidos, ingredientes, detalles


def load(pedidos, ingredientes, detalles):
    """ Función que genera el fichero excel con los reportes """
    # pedidos = order_id, date, time
    # ingredientes = ingrediente, count
    # detalles = order_details_id, order_id, pizza_id, quantity, pizza_type_id, pizza_size


    # Creamos el fichero excel
    writer = pd.ExcelWriter('output/maven_pizzas.xlsx', engine='xlsxwriter')    

    # Número de pedidos
    num_pedidos = pedidos.shape[0]
    # Número de ingredientes
    num_ingredientes = ingredientes.shape[0]
    # Ingredientes mas consumidos
    ingredientes_mas_consumidos = ingredientes.sort_values(by='weekly count', ascending=False).head(5)

    # Gráfica de distribucion de los ingredientes
    plot_ingredientes = ingredientes_mas_consumidos.plot(kind='bar', x='ingrediente', y='weekly count', title='Ingredientes más consumidos')
    plt.savefig('output/ingredientes_mas_consumidos.png')

    # Gráfica de distribución de pizzas más pedidas
    pizzas_mas_pedidas = detalles.groupby('pizza_id').sum().sort_values(by='quantity', ascending=False).head(5)
    plot_pizzas_mas_pedidas = pizzas_mas_pedidas.plot(kind='bar', y='quantity', title='Pizzas más pedidas')
    plt.savefig('output/pizzas_mas_pedidas.png')

    tipo_pizza_mas_pedida = detalles.groupby('pizza_type_id').sum().sort_values(by='quantity', ascending=False).head(5)
    plot_tipo_pizza_mas_pedida = tipo_pizza_mas_pedida.plot(kind='bar', y='quantity', title='Tipo de pizza más pedida')
    plt.savefig('output/tipo_pizza_mas_pedida.png')
    

    # Gráfica de distribución de tamaños más pedidos
    tamaños_mas_pedidos = detalles.groupby('pizza_size').sum().sort_values(by='quantity', ascending=False).head(5)
    plot_tamaños_mas_pedidos = tamaños_mas_pedidos.plot(kind='bar', y='quantity', title='Tamaños más pedidos')
    plt.savefig('output/tamaños_mas_pedidos.png')


    # Gráfica de numero de pedidos por mes del año
    pedidos['mes'] = pedidos.apply(lambda row: Sacar_Mes(row), axis=1)
    pedidos_por_mes = pedidos.groupby('mes').count().sort_values(by='mes', ascending=True)
    plot_pedidos_por_mes = pedidos_por_mes.plot(kind='bar', y='order_id', title='Pedidos por mes del año')
    plt.savefig('output/pedidos_por_mes.png')
    

    # Gráfica de lineas de numero de pedidos por hora del día
    pedidos['hora'] = pedidos.apply(lambda row: Sacar_Hora(row), axis=1)
    pedidos_por_hora = pedidos.groupby('hora').count().sort_values(by='hora', ascending=True)
    #print(pedidos_por_hora)
    plot_pedidos_por_hora = pedidos_por_hora.plot(kind='line', y='order_id', title='Pedidos por hora del día')
    plt.savefig('output/pedidos_por_hora.png')



    """
    Vamos a añadir las 5 graficas a una hoja de excel que se llama reporte ejecutivo
    """
    workbook = writer.book
    worksheet = workbook.add_worksheet('Reporte ejecutivo')
    worksheet.write(0, 0, 'Número de pedidos')
    worksheet.write(1, 0, num_pedidos)
    worksheet.write(2, 0, 'Número de ingredientes')
    worksheet.write(3, 0, num_ingredientes)

    worksheet.write(4, 0, 'Ingredientes más consumidos')
    worksheet.insert_image(5, 0, 'output/ingredientes_mas_consumidos.png')
    worksheet.write(29, 0, 'Pedidos por mes del año')
    worksheet.insert_image(30, 0, 'output/pedidos_por_mes.png')
    worksheet.write(54, 0, 'Pedidos por hora del día')
    worksheet.insert_image(55, 0, 'output/pedidos_por_hora.png')


    # Creamos un reporte de ingredientes
    ingredientes.to_excel(writer, sheet_name='Reporte ingredientes', index=False)
    """
    # OTRA FORMA MENOS EFICIENTE DE HACERLO
    worksheet = workbook.add_worksheet('Reporte de ingredientes')
    worksheet.write(0, 0, 'Nombre del ingrediente')
    worksheet.write(0, 1, 'Número de veces que se ha pedido')
    for i in range(0, ingredientes.shape[0]):
        worksheet.write(i+1, 0, ingredientes.iloc[i, 0])
        worksheet.write(i+1, 1, ingredientes.iloc[i, 1])
    """

    # creamos una nueva hoja llamada 'Reporte pedidos' y añadimos las imagenes 'tamaños_mas_pedidos.png', 'tipo_pizza_mas_pedida.png'
    # y 'pizzas_mas_pedidas.png'
    worksheet = workbook.add_worksheet('Reporte pedidos')
    worksheet.write(0, 0, 'Tamaños más pedidos')
    worksheet.insert_image(1, 0, 'output/tamaños_mas_pedidos.png')
    worksheet.write(25, 0, 'Tipo de pizza más pedida')
    worksheet.insert_image(26, 0, 'output/tipo_pizza_mas_pedida.png')
    worksheet.write(50, 0, 'Pizzas más pedidas')
    worksheet.insert_image(51, 0, 'output/pizzas_mas_pedidas.png')

    """
    Vamos a hacer un gráfico de barras de excel con la cantidad de pizzas pedididas en cada pedido.
    Para ello, tendremos que contar cuantas ocurrencias de cada order_id hay en el df de detalles, y luego
    contar cuantas veces se repite cada numero. 
    Por ejemplo, si para order_id = 1 hay 3 pizzas, y para order_id = 2 hay 2 pizzas, entonces tendremos que
    en el gráfico de barras, en la posición 3 habrá una barra de altura 1, y en la posición 2 habrá una barra de altura 1.
    """

    # contamos cuantas veces aparece cada order_id en el df detalles
    order_id_counts = detalles.groupby('order_id').count().sort_values(by='order_id', ascending=True)

    # contamos cuantas veces aparece cada numero de pizzas en el df order_id_counts
    order_id_counts = order_id_counts.groupby('quantity').count().sort_values(by='quantity', ascending=True)

    order_id_counts.drop(columns=['pizza_id', 'pizza_type_id','pizza_size'], inplace=True)

    order_id_counts.rename(columns={'order_details_id': 'cantidad de pedidos'}, inplace=True)
    # creamos una nueva columna que sea el numero de pizzas (1,2,3, ..., len(order_id_counts))
    order_id_counts['numero de pizzas'] = order_id_counts.index
    
    # cambiamos el orden de las columnas, de tal forma que 'numero de pizzas' sea la primera y 'cantidad de pedidos' la segunda
    order_id_counts = order_id_counts[['numero de pizzas', 'cantidad de pedidos']]
    print(order_id_counts.head(5))
    
    #worksheet = workbook.add_worksheet('Grafica de pizzas por pedido')

    # creamos un gráfico de barras con los datos de order_id_counts
    chart = workbook.add_chart({'type': 'column'})

    # cargamos el df order_id_counts a la hoja de excel, para luego poder hacer el gráfico
    order_id_counts.to_excel(writer, sheet_name='N_pedidos - N_pizzas_pedido', index=False)


    # añadimos los datos de order_id_counts al gráfico
    chart.add_series({
        'name':       'Pedidos',
        'categories': ['N_pedidos - N_pizzas_pedido', 1, 0, len(order_id_counts), 0],
        'values':     ['N_pedidos - N_pizzas_pedido', 1, 1, len(order_id_counts), 1],
    })

    # configuramos el gráfico
    chart.set_title({'name': 'Cantidad de pizzas por pedido'})
    chart.set_x_axis({'name': 'Número de pizzas'})
    chart.set_y_axis({'name': 'Cantidad de pedidos'})
    
    # añadimos el gráfico a la hoja de excel a la página 'Reporte pedidos'
    worksheet.insert_chart('A75', chart)

    # Guardamos el fichero excel
    writer.save()



def Sacar_Hora(row):
    """
    Función que saca la hora de la fecha
    """
    return int(row['time'].split(':')[0])


def Sacar_Mes(row):
    """
    Función que saca el mes de la fecha
    """
    return row['date'].month


def Separar_Tipo_Tamaño(df_order_details):
    # aqui tenemos que separar el tipo de pizza de su tamaño, para poder trabajar con ellos de forma independiente

    # Creamos una nueva columna con el tipo de pizza
    df_order_details['pizza_type_id'] = df_order_details.apply(lambda row: Sacar_Tipo_Pizza(row), axis=1)

    # creamos una nueva columna con el tamaño de la pizza
    df_order_details['pizza_size'] = df_order_details.apply(lambda row: Sacar_Tamaño_Pizza(row), axis=1)

    #print('\nDETALLES PEDIDOS\n', df_order_details.head(15))
    return df_order_details


def Sacar_Tamaño_Pizza(row):
    # aqui tenemos que sacar el tamaño de la pizza
    """
    Sabemos que el pizza_id es de la forma f'{NombrePizza}_{TamañoPizza}', y que tamaño pizza es
    una de las siguientes: s, m, l, xl, xxl.

    Nos vamos a apoyar en que el tamaño de la pizza es el último elemento de la cadena, y que
    el tamaño de la pizza es una de las siguientes: s, m, l, xl, xxl, separado del tipo de pizza por '_'
    
    Por tanto, rompemos el pizza_id en trozos según los guiones bajos, y cogemos el último elemento (el tamaño)
    
    EJEMPLOS: 
        para 'classic_dlx_m', el tipo de pizza es 'classic_dlx', y el tamaño es 'm' 
        para 'pep_msh_pep_s', el tipo de pizza es 'pep_msh_pep', y el tamaño es 's'
        para 'hawaiian_m', el tipo de pizza es 'hawaiian', y el tamaño es 'm'
    """
    try:
        pizza_size = row['pizza_id'].split('_')[-1]
        #pizza_size = '_'.join(pizza_size)
        return pizza_size
    except:
        return None


def Sacar_Tipo_Pizza(row):
    # las columnas son order_details_id, order_id, pizza_id, quantity
    """
    Vamos a quitarle a pizza_id el tamaño de la pizza, para que solo quede el tipo de pizza
    Para ello, podemos apoyarnos en que ya hemos filtrado el tamaño de la pizza, y que se separa del nombre
    de la pizza por un guión bajo (el último de la cadena). Por tanto, podemos usar la función split() para
    separar la cadena según los guiones bajos, descartar el último elemento de la lista que nos devuelve
    y volver a juntarlo todo con guiones bajos. 
    """
    try:
        # sacamos el tipo de pizza, quitando el tamaño de la pizza
        pizza_id = row['pizza_id'].split('_')[:-1]
        pizza_id = '_'.join(pizza_id)
        return pizza_id
    except:
        return None



if __name__ == '__main__':
    df_pedidos, df_ingredientes, df_detalles = extract()
    df_pedidos, df_ingredientes, df_detalles = transform(df_pedidos, df_ingredientes, df_detalles)
    load(df_pedidos, df_ingredientes, df_detalles)

