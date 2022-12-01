import pandas as pd
import math

def extract():
    # leemos los datos de la pizzeria de los csv
    """
    Nota: no vamos a leer todos los csv, porque hay algunos que no aportan nada de utilidad al objetivo.
    Los que nos interesan son los tipos de pizza y los pedidos. 
    """
    df_pizza_types = pd.read_csv('data/pizza_types.csv')
    # Columnas: pizza_type_id, name, category, ingredients
    
    df_order_details = pd.read_csv('data/order_details.csv')
    # Columnas: order_details_id, order_id, pizza_id, quantity
    
    return df_pizza_types, df_order_details


def transform(df_pizza_types, df_order_details):
    ponderaciones = {'s': 0.8, 'm': 1.0, 'l': 1.2, 'xl': 1.3, 'xxl': 1.4}
    """ Vamos a asignarle a cada pizza pedida un tamaño, y un tipo de pizza """
    # creamos una columna con el tamaño de la pizza y otra con el tipo de pizza
    df_order_details = Separar_Tipo_Tamaño(df_order_details)
    
    """ Ahora, vamos a añadir al dataframe de order details los ingredientes de la pizza pedida """
    pizza_ingredients = {}
    for i in range(len(df_pizza_types)):
        pizza_ingredients[df_pizza_types['pizza_type_id'][i]] = df_pizza_types['ingredients'][i]

    # creamos una columna con los ingredientes de la pizza
    df_order_details['pizza_ingredients'] = df_order_details['pizza_type_id'].map(pizza_ingredients)

    """ Vamos a contar cuantas veces aparece cada ingrediente en los pedidos """
    # creamos un diccionario con los ingredientes de cada pizza
    ingredients = {}
    n_pizzas = 0
    for i in range(len(df_order_details)):
        for ingredient in df_order_details['pizza_ingredients'][i].split(', '):
            if ingredient in ingredients:
                ingredients[ingredient] += ponderaciones[df_order_details['pizza_size'][i]] * df_order_details['quantity'][i]
            else:
                ingredients[ingredient] = ponderaciones[df_order_details['pizza_size'][i]] * df_order_details['quantity'][i]
            n_pizzas += ponderaciones[df_order_details['pizza_size'][i]] * df_order_details['quantity'][i]
    
    salsa_tomate = n_pizzas - Contar_Salsas(ingredients)
    ingredients['Tomato Sauce'] = salsa_tomate
    mozzarella = n_pizzas 
    # como la mozarella va en todas las pizzas, damos por hecho que si se especifica que lleva
    # mozzarella, es que lleva doble de la misma, por tanto, sumamos el numero de pizzas al numero 
    # de pizzas que llevan mozzarella doble
    
    ingredients['Mozzarella Cheese'] += mozzarella

    # creamos un dataframe con los ingredientes y el numero de veces que aparecen
    df_ingredients = pd.DataFrame.from_dict(ingredients, orient='index', columns=['count'])
    df_ingredients = df_ingredients.sort_values(by='count', ascending=False)

    print(df_ingredients)
    # vamos a dividir las unidades de los ingredientes entre 52, para hallar cuanto necesitamos para una semana
    df_ingredients['count'] = df_ingredients['count'] / 52
    # redondeamos los valores al entero mayor más cercano
    df_ingredients['count'] = df_ingredients['count'].apply(math.ceil)
    return df_ingredients


def load(df_final):
    # guardamos el dataframe en un csv
    df_final.to_csv('output/ingredientes_semana.csv')



def Informe_Datos(df_order_details):
    """ Informe de calidad de los datos, reflejando la tipología de cada columna y el numero de NaN y Null por cada columna """
    # vamos a almacenar los resultados en un archivo csv para poder acceder a ellos más tarde.
    tipos_datos = df_order_details.dtypes
    nulos = df_order_details.isnull().sum()
    vacios = df_order_details.isna().sum()
    

    df_informe = pd.DataFrame({'tipos_datos': tipos_datos, 'nulos': nulos, 'vacios': vacios})
    df_informe.to_csv('data/informe_datos.csv')
    print('\n\n\n')
    print('\nINFORME DE DATOS\n')
    print('Tipología de las columnas:\n', tipos_datos)
    print('\nNumero de NaN por columna:\n', vacios)
    print('\nNumero de Null por columna:\n', nulos)



def Contar_Salsas(diccionario_ingredientes):
    """
    Dado un diccionario con los ingredientes y las cantidades de los mismos, esta funcion devuelve el número de
    veces que aparece una salsa en los ingredientes (está la palabra 'Sauce' en las claves del diccionario).
    """
    numero_salsas = 0
    for ingrediente in diccionario_ingredientes:
        if 'Sauce' in ingrediente:
            numero_salsas += diccionario_ingredientes[ingrediente]
    return numero_salsas


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
    df_tipos_pizzas, df_detalles_pedidos = extract()
    Informe_Datos(df_detalles_pedidos)
    data = transform(df_tipos_pizzas, df_detalles_pedidos)
    load(data)