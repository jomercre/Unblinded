# --------------------------------------------------
# -                 Unblinded                      -
# --------------------------------------------------
#
# Creadores: Axel Valton Juan & Joan Merlos Cremades

# Libraries

from funciones_navegacion import *

# Mode selector

M = 'SN'
'''
print('Available models:')
print('Read -> R')
print('Description -> D')
print('Navigation -> N')
print('Finding -> F\n')

M = input('Mode: ')

while M != 'R' and M != 'D' and M != 'N' and M != 'R':
    
    print('\nMode unavailable\n')
    
    print('Available models:')
    print('Read -> R')
    print('Description -> D')
    print('Navigation -> N')
    print('Simulated Navigation -> SN')
    print('Finding -> F\n')
    
    M = input('Mode: ')
'''

# Image input

img_path = 'new_img.png'

# Generate text

if M == 'R':
    
    # Read the image
    
    text = ReadMode(img_path)
    
    # Detect text
    
    if text == "":
        text = "Texto no detectado"
    else:
        # Correct text
        
        Intro = "Corrige el siguiente texto, añadiendo artículos y cambiando palabras si es necesario, para que sea más comprensible: "
        Conc = " Devuelve únicamente la versión corregida del texto, no añadas ningún comentario adicional."
        corr_prompt = Intro + text + Conc
                        
        text = ask_Groq(prompt = corr_prompt)
    
elif M == 'D':
    
    # Obtain information about the image
    
    descr = ask_Groq(img_path=img_path)
    
    # Detect danger
    
    text = ask_Groq(prompt=descr, Danger = True)
    
elif M == 'SN':
    
    origen_gps = (39.4699, -0.3763)
    
    '''
    destino_texto = obtener_destino_valido(gmaps, origen_gps)
    
    # Correct text
    
    Intro = "Corrige el siguiente texto, añadiendo artículos y cambiando palabras si es necesario, para que sea más comprensible: "
    Conc = " Devuelve únicamente la versión corregida del texto, no añadas ningún comentario adicional."
    corr_prompt = Intro + text + Conc
                    
    text = ask_Groq(prompt = corr_prompt)
    '''
    
    text = 'Ciudad de las artes y las ciencias'
    
    # Puedes usar direcciones exactas, nombres de ciudades, o lugares emblemáticos
    mi_ubicacion = "Valencia, España" 
    mi_destino = text
    
    resultado=calcular_ruta(gmaps, mi_ubicacion, mi_destino)
    
    if resultado:
        # Extraemos los pasos exactamente como discutimos
        pasos = resultado[0]['legs'][0]['steps']
        
        # Arrancamos el simulador pasándole los pasos y nuestra posición inicial
        iniciar_navegacion_simulada(pasos, origen_gps)
    
    text = "Has llegado a tu destino. Navegación finalizada."
    
elif M == 'F':

    # Tratamiento del texto obtenido
    
    text = None
    
    while text is None:
        
        text = SpeechToText()
        
     # Correct text
     
    Intro = "Corrige el siguiente texto, añadiendo artículos y cambiando palabras si es necesario, para que sea más comprensible: "
    Conc = " Devuelve únicamente la versión corregida del texto, no añadas ningún comentario adicional."
    corr_prompt = Intro + text + Conc
                     
    text = ask_Groq(prompt = corr_prompt)

    # Reduction of the text

    text = find_Groq(prompt=text)

    # Traduction to english

    Intro = "Traduceme el siguiente texto a inglés: "
    prompt = Intro + text

    prompt = ask_Groq(prompt=prompt)
    print(prompt)
    
    input('Pon cualquier cosa cuando hayas obtenido la imagen: ')
    
    # Obtain information about the image
    
    prompt = f"""Actúa como un asistente experto en accesibilidad visual. Te voy a proporcionar una imagen donde hay varios objetos resaltados explícitamente con colores vistosos. 

                    Tu objetivo es ayudar a una persona ciega a construir un mapa mental preciso de la escena. Por favor, sigue exactamente estos pasos:
                            
                    1. Contexto breve: Describe en una sola oración el entorno general de la imagen (por ejemplo, 'Es una cocina vista desde el frente' o 'Es una calle concurrida').
                    2. Identificación y Ubicación: Por cada objeto resaltado que detectes, indica qué es y detalla su posición utilizando una cuadrícula imaginaria de 3x3 (arriba/centro/abajo y izquierda/centro/derecha). 
                    3. Relación espacial (opcional pero recomendada): Si hay varios objetos resaltados, describe brevemente cómo están ubicados unos respecto a otros (ej. 'El objeto A está justo a la derecha y ligeramente por delante del objeto B').
                            
                    Ignora los objetos que no estén resaltados, a menos que sean un punto de referencia indispensable para ubicar a los que sí lo están. Sé claro, objetivo y descriptivo."""

    text = ask_Groq(img_path=img_path, prompt=prompt)
    
# Generate audio

TextToSpeech(text)


