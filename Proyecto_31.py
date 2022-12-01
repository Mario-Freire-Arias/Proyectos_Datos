import csv
import json

def extract():
    """
    Extrae los datos del fichero leaks.csv y los devuelve en una lista de
    diccionarios.
    """
    with open('leaks.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        leaks = []
        for row in reader:
            leaks.append(row)
    return leaks

def transform(leaks):
    """
    Transforma los datos de los leaks para que se ajusten al formato del
    fichero json de salida.
    """
    leaks_json = []
    for leak in leaks:
        leaks_json.append({'commit': leak['commit'], 'message': leak['message']})
    return leaks_json

def load(leaks_json):
    """
    Guarda los datos de los leaks en el fichero leaks.json
    """
    with open('leaks.json', 'w') as jsonfile:
        json.dump(leaks_json, jsonfile)

if __name__ == '__main__':
    leaks = extract()
    leaks_json = transform(leaks)
    load(leaks_json)