"""
Se pide: 
    Generar un reporte ejecutivo para el COO de Maven Pizzas en formato pdf 
"""

import pandas as pd
import fpdf

"""

"""


def extract():
    informe = pd.read_csv('data/informe_datos.csv')
    ingredientes_semanales = pd.read_csv('data/ingredientes_semana.csv')
    return informe, ingredientes_semanales

def transform(informe, ingredientes_semanales):
    informe.rename(columns={'Unnamed 0': 'campo'})
    ingredientes_semanales.rename(columns={'Unnamed: 0': 'ingrediente', 'count':'cantidad'}, inplace=True)

    return informe, ingredientes_semanales

def load(informe, ingredientes_semanales):
    """ Función que carga datos en un pdf y lo guarda en local. """
    generar_imagenes() # generamos las imágenes que queramos incluir en el informe pdf
    pdf = fpdf.FPDF()

    pdf.add_page()
    pdf.set_margins(30, 20, 30)
    #print(pdf.w,pdf.h) # vemos que el ancho es 210 y el alto es 297 mm
    pdf.set_font('Arial', 'B', 16)
    """
    pdf.cell(w, h, txt, border, ln, align, fill, link):
        w: ancho de la celda
        h: alto de la celda
        txt: texto que queremos incluir en la celda
        border: 1 si queremos que la celda tenga borde, 0 si no
        ln: 0 para que la proxima celda sea a la derecha, 1 si queremos que la celda sea nueva linea
        a: alineacion del texto dentro de la celda (L, C, R, J)
    """
    pdf.cell(30, 10, '', 0, 0, 'C')
    pdf.cell(w=80, h=10, txt='Informe ejecutivo', border=0, ln=1, align='L')
    pdf.set_font('Arial', '', 12)
    """
    Tenemos el texto que queremos incluir en el archivo data/texto_reporte_ejecutivo.txt
    Vamos a leerlo e incluirlo por parrafos en el pdf.    
    """
    with open('data/texto_reporte_ejecutivo.txt', 'r') as f:
        texto = f.read()
        parrafos = texto.split('\n\n')
        for parrafo in parrafos:
            pdf.multi_cell(w=0, h=6, txt=parrafo, border=0, align='J')
            pdf.ln(5)


    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Consumo de ingredientes por semana')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 10, 'Ingredientes')
    pdf.cell(40, 10, 'Cantidad')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    for i in range(len(ingredientes_semanales)):
        pdf.cell(80, 10, ingredientes_semanales['ingrediente'][i])
        pdf.cell(40, 10, str(ingredientes_semanales['cantidad'][i]))
        pdf.ln(10)


    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Gráficos resumen')
    
    # cargamos las imágenes que hemos generado en la función generar_imagenes()
    pdf.image('data/imagenes/ingredientes_mas_consumidos.png', x=10, y=30, w=100)
    pdf.image('data/imagenes/pedidos_por_hora.png', x=100, y=30, w=100)
    pdf.image('data/imagenes/pedidos_por_mes.png', x=10, y=100, w=100)
    pdf.image('data/imagenes/pizzas_mas_pedidas.png', x=100, y=100, w=100)
    pdf.image('data/imagenes/tamaños_mas_pedidos.png', x=10, y=170, w=100)
    pdf.image('data/imagenes/tipo_pizza_mas_pedida.png', x=100, y=170, w=100)



    pdf.output('output/informe_ejecutivo.pdf', 'F')


def generar_imagenes():
    """
    Funcion que generaría las imágenes de data/imagenes que serán incluídas en el informe pdf.
    """
    # Estas imágenes ya se generan en otro programa, es absurdo repetir el proceso aquí.
    # Simplemente cogemos las imágenes y nos las guardamos en una carpeta.
    pass


if __name__ == '__main__':
    print('Generar un reporte ejecutivo para el COO de Maven Pizzas en formato pdf')
    informe, ingredientes_semanales = extract()
    informe, ingredientes_semanales = transform(informe, ingredientes_semanales)
    load(informe, ingredientes_semanales)
