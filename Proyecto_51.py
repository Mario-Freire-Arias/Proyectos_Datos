import pandas as pd, requests, json, fpdf, warnings
from bs4 import BeautifulSoup as BS

def et_api():
    """
    funcion que hace la etl de la api de la nba. llama a las funciones de extraer transformar y cargar los datos de la api
    """
    key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' # key de la api de la nba (personal y privada, se obtiene al registrarse)
    key = 'd5bee63516764094aeeef070f34cedab'
    try:
        url = 'https://api.sportsdata.io/v3/nba/scores/json/Standings/2022?key=' + key
        response_standings = requests.get(url)
        dic_standings = response_standings.json()
        print('Tabla de clasificación extraida del la api correctamente')
        # guardamos el json en un fichero
        with open('respuestas/standings.json', 'w') as f:
            json.dump(dic_standings, f)
    except:
        # leemos el json de un fichero previamente guardado:
        with open('respuestas/standings.json', 'r') as f:
            dic_standings = json.load(f)

    try:    
        endpoint = 'https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/2022?key=' + key
        response = requests.get(endpoint)
        dic_stats = response.json()
        print('Estadísticas extraídas del la api correctamente')
        # vamos a guardarlo como un fichero json
        with open('respuestas/stats.json', 'w') as f:
            json.dump(dic_stats, f)
    except:
        # leemos el json de un fichero previamente guardado:
        with open('respuestas/stats.json', 'r') as f:
            dic_stats = json.load(f)

    # creamos un dataframe con los datos de la api de standings
    df_standings = pd.DataFrame(dic_standings) # nos da error
    

    # creamos un dataframe con los datos de la api de stats
    df_stats = pd.DataFrame(dic_stats)
    return df_standings, df_stats


def et_webscraping():
    """
    funcion que hace una etl del webscraping de la pagina de pronosticos de la nba
    """
    # vamos a hacer que no salgan las advertencias por pantalla
    warnings.filterwarnings('ignore')
    url_nba = 'https://www.solobasket.com/apuestas-deportivas/pronosticos-nba/'
    # creamos el request
    response = requests.get(url_nba)
    # creamos un objeto beautifulsoup para parsear el html
    sopa_nba = BS(response.text, 'html.parser')
    # imprimimos el html parseado
    tabla = sopa_nba.find('tbody', class_='nsn-tbody')
    # tenemos la tabla con 4 partidos y sus pronosticos
    textos_interes = tabla.find_all('p', style='text-align: center;')

    # ahora tenemos que extraer los datos de cada partido
    partidos = tabla.find_all('strong')
    negritas = tabla.find_all('b')
    negritas_texto = [negrita.text for negrita in negritas]
    # tenemos toda la informacion en los elementos de la lista, entre las etiquetas <strong> y </strong>.
    # Vamos a extraer el texto de entre las etiquetas de cada elemento de la lista
    partidos_texto = [partido.text for partido in partidos]
    # insertamos el elemento negritas_texto[2] despues del elemento de indice 5 de partidos_texto
    partidos_texto.insert(6, negritas_texto.pop(2))
    # vamos a insertar el elemento i de negritas_texto entre las fechas y las cuotas de cada partido
    for i in range(0, len(negritas_texto)):
        partidos_texto.insert(2 + 4*i, negritas_texto[i])
    diccionario = {'partidos': [], 'fechas': [], 'pronosticos': [], 'cuotas': []}
    for i in range(0, len(partidos_texto)):
        if i % 4 == 0:
            diccionario['partidos'].append(partidos_texto[i])
        elif i % 4 == 1:
            diccionario['fechas'].append(partidos_texto[i])
        elif i % 4 == 2:
            diccionario['pronosticos'].append(partidos_texto[i])
        elif i % 4 == 3:
            diccionario['cuotas'].append(partidos_texto[i])

    # vamos a crear una lista de los equipos que participan en los partidos asociados a la clave 'equipos'
    equipos = []
    for partido in diccionario['partidos']:
        equipos.append(partido.split(' vs ')[0])
        equipos.append(partido.split(' vs ')[1])
    equipos[3] = equipos[3].replace('LA', 'Los Angeles')
    tuplas_equipos = []
    for equipo in equipos:
        partes = equipo.split(' ')
        parte_grande = ' '.join(partes[:-1])
        tuplas_equipos.append((parte_grande, partes[-1]))
    diccionario['equipos'] = equipos
    df = pd.DataFrame()

    # vamos a fijar las columnas del dataframe
    df['ciudad_equipo'] = None
    df['equipo'] = None
    df['nombre_completo_equipo1'] = None
    df['nombre_completo_equipo2'] = None
    df['partidos'] = None
    df['fecha'] = None
    df['pronostico'] = None
    df['cuota'] = None

    for ciudad, equipo in tuplas_equipos:
        df = df.append({'equipo': equipo, 'ciudad_equipo': ciudad}, ignore_index=True)
        for i in range(len(diccionario['partidos'])):
            if equipo in diccionario['partidos'][i]:
                df.loc[df['equipo'] == equipo, 'partidos'] = diccionario['partidos'][i]
                df.loc[df['equipo'] == equipo, 'fecha'] = diccionario['fechas'][i]
                df.loc[df['equipo'] == equipo, 'pronostico'] = diccionario['pronosticos'][i]
                df.loc[df['equipo'] == equipo, 'cuota'] = diccionario['cuotas'][i]
    # añadimos los nombres completos de los equipos
    for i in range(len(df)):
        if i % 2 == 0:
            df.loc[i, 'nombre_completo_equipo1'] = df.loc[i, 'ciudad_equipo'] + ' ' + df.loc[i, 'equipo']
            df.loc[i, 'nombre_completo_equipo2'] = df.loc[i+1, 'ciudad_equipo'] + ' ' + df.loc[i+1, 'equipo']
        else:
            df.loc[i, 'nombre_completo_equipo1'] = df.loc[i-1, 'ciudad_equipo'] + ' ' + df.loc[i-1, 'equipo']
            df.loc[i, 'nombre_completo_equipo2'] = df.loc[i, 'ciudad_equipo'] + ' ' + df.loc[i, 'equipo']
    return df


def cargar_datos(df_standings, df_stats, df_webscraping):
    """
    Funcion que carga los datos en un pdf
    """
    pdf = fpdf.FPDF()
    pdf.add_page()    
    # vamos a coger el primer equipo del df_webscraping 
    equipo = df_webscraping.loc[0, 'equipo']
    ciudad = df_webscraping.loc[0, 'ciudad_equipo']
    df_standings_equipo = df_standings[df_standings['Name'] == equipo]
    df_stats_equipo = df_stats[df_stats['Name'] == ciudad + ' ' + equipo]
    # vamos a hacer un informe sobre el equipo
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Datos del equipo ' + equipo + ' en la temporada ' + str(df_stats_equipo['Season'].values[0]), ln=1)
    pdf.set_font('Arial', size=12)
    pdf.cell(40, 10, 'Posicion en la clasificacion general: ' + str(df_standings_equipo['DivisionRank'].values[0]), ln=1)
    pdf.cell(40, 10, 'Partidos ganados: ' + str(df_stats_equipo['Wins'].values[0]), ln=1)
    pdf.cell(40, 10, 'Partidos perdidos: ' + str(df_standings_equipo['Losses'].values[0]), ln=1)
    pdf.cell(40, 10, 'Promedio de puntos encestados a favor por partido: ' + str(df_standings_equipo['PointsPerGameFor'].values[0]), ln=1)
    pdf.cell(40, 10, 'Promedio de puntos encestados en contra por partido: ' + str(df_standings_equipo['PointsPerGameAgainst'].values[0]), ln=1)
    pdf.cell(40, 10, 'Partidos ganados de los ultimos 10 jugados: ' + str(df_standings_equipo['LastTenWins'].values[0]), ln=1)
    pdf.cell(40, 10, 'Racha de partidos ganados/perdidos: ' + str(df_standings_equipo['Streak'].values[0]), ln=1)
    pdf.cell(40, 10, 'Descripcion de la racha de partidos ganados/perdidos: ' + str(df_standings_equipo['StreakDescription'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de acierto de tiros de 2 puntos: ' + str(df_stats_equipo['TwoPointersPercentage'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de acierto de tiros de 3 puntos: ' + str(df_stats_equipo['ThreePointersPercentage'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de acierto de tiros libres: ' + str(df_stats_equipo['FreeThrowsPercentage'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de recepcion de rebotes ofensivos: ' + str(df_stats_equipo['OffensiveReboundsPercentage'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de recepcion de rebotes defensivos: ' + str(df_stats_equipo['DefensiveReboundsPercentage'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de robos de balon: ' + str(df_stats_equipo['StealsPercentage'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de faltas personales: ' + str(df_stats_equipo['PersonalFouls'].values[0]), ln=1)
    pdf.cell(40, 10, 'Porcentaje de bloqueos: ' + str(df_stats_equipo['BlockedShots'].values[0]), ln=1)

    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Predicción a futuro del equipo.', ln=1)
    pdf.set_font('Arial', size=12)
    # vamos a coger el resultado esperado del proximo partido
    pdf.cell(40, 10, 'Proximo partido: ' + df_webscraping.loc[0, 'partidos'], ln=1)
    pdf.cell(40, 10, 'Fecha del partido: ' + df_webscraping.loc[0, 'fecha'], ln=1)
    pdf.cell(40, 10, 'Pronostico: ' + df_webscraping.loc[0, 'pronostico'], ln=1)
    pdf.cell(40, 10, 'Cuota del pronostico: ' + df_webscraping.loc[0, 'cuota'], ln=1)
    # vamos a imprimir por pantalla la prediccion del proximo partido
    print(f'Predicciones del proximo partido de {equipo}: ')
    print('\tProximo partido: ' + df_webscraping.loc[0, 'partidos'])
    print('\tFecha del partido: ' + df_webscraping.loc[0, 'fecha'])
    print('\tPronostico: ' + df_webscraping.loc[0, 'pronostico'])
    print('\tCuota del pronostico: ' + df_webscraping.loc[0, 'cuota'])    

    pdf.output('informe.pdf', 'F')


if __name__ == '__main__':
    df_standings, df_stats = et_api()
    df_webscraping = et_webscraping()
    cargar_datos(df_standings, df_stats, df_webscraping)