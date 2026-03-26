# --------------------------------------------------
# -              Unblinded Functions               -
# --------------------------------------------------
#
# Creadores: Axel Valton Juan & Joan Merlos Cremades

# Librerías

import googlemaps
import re
from datetime import datetime
import time
import os
from gtts import gTTS
import pygame
from geopy.distance import geodesic
import speech_recognition as sr
import os
from dotenv import load_dotenv
from PIL import Image
from groq import Groq
import base64
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import easyocr



# Inicializamos el mezclador de audio de pygame

pygame.mixer.init()

#  Inicializamos las API's correspondientes

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)
API_KEY = os.getenv("MAPS_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

# Funciones para utilizar IA generativa

def ReadMode(img_path):

    lector = easyocr.Reader(['es'])
    resultados = lector.readtext(img_path)
    lista_de_textos = [fragmento[1] for fragmento in resultados]

    # Unimos todo el texto en una única variable
    text = " ".join(lista_de_textos)
    
    return text

def TextToSpeech(texto):
    
    # Generamos un archivo único basado en el tiempo actual
    nombre_archivo = f"instruccion_{int(time.time())}.mp3"
    
    try:
        # Generamos el audio
        tts = gTTS(text=texto, lang='es', slow=False)
        tts.save(nombre_archivo)
        
        # Reproducimos el audio
        pygame.mixer.music.load(nombre_archivo)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.music.unload()
        
        # Borramos el archivo
        if os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)
        else:
            print('No se ha podido borrar')
            
    except Exception as e:
        print(f"Error al generar o reproducir la voz: {e}")
    
    return

def image_file_to_base64(image_path):
    try:
        # Abrimos el archivo en modo lectura binaria
        with open(image_path, "rb") as image_file:
            # Leemos y codificamos el archivo
            
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string.decode('utf-8')
    except Exception as e:
        print(f"Error al leer la imagen: {e}")
        return None

def ask_Groq(prompt=None, img_path=None, Danger=False):
    try:
        if img_path is None and Danger == False:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "REGLAS ESTRICTAS: "
                            "1. NUNCA uses saludos, introducciones (como 'Aquí tienes', 'Me encantaría describir', 'En la imagen se ve') ni despedidas. "
                            "2. Sé extremadamente preciso, objetivo y ve directo al grano. "
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", 
            )
            
            return chat_completion.choices[0].message.content
        
        elif img_path is None and Danger:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "Eres un asistente de accesibilidad visual para personas ciegas."
                            "REGLAS ESTRICTAS: "
                            "1. El texto de entrada procede de una imagen, si encuentras algun peligro para personas invidentes añadelo a principio del texto."
                            "   Los principales peligros que debes detectar son semáforos en rojo, aceras sin paso de cebra o zonas con caídas abruptas."
                            "2. En caso de no detectar peligro no indiques que no hay peligro, limitate a realizar un resumen del texto."
                            "3. Nunca uses saludos, introducciones (como 'Aquí tienes', 'Me encantaría describir', 'En la imagen se ve') ni despedidas. "
                            "4. Sé extremadamente preciso y objetivo, evitando descripciones que puedan resultar obvias para una persona tales como el mar es azul o el césped es verde."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", 
            )
            return chat_completion.choices[0].message.content

        elif prompt is None:

            img_base64 = image_file_to_base64(img_path)

            text_prompt = "Soy una persona ciega que quiero obtener información detallada de la siguiente imagen:"
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "Eres un asistente de accesibilidad visual para personas ciegas. "
                            "REGLAS ESTRICTAS: "
                            "1. Responde únicamente con la descripción de la imagen o la advertencia de peligro. "
                            "2. Nunca uses saludos, introducciones ni despedidas. ")
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                        ]
                    }
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct", # Modelo específico para visión
            )
            return chat_completion.choices[0].message.content

        else:

            img_base64 = image_file_to_base64(img_path)

            text_prompt = f"Soy una persona ciega que quiero obtener información de la siguiente imagen: {prompt}"
            
            chat_completion = client.chat.completions.create(
                messages=[
                                {
                        "role": "system", 
                        "content": (
                            "Eres un asistente de accesibilidad visual para personas ciegas. "
                            "REGLAS ESTRICTAS: "
                            "1. Responde únicamente con la descripción de la imagen o la advertencia de peligro. "
                            "2. Nunca uses saludos, introducciones (como 'Aquí tienes', 'Me encantaría describir', 'En la imagen se ve') ni despedidas. "
                            "3. Sé extremadamente preciso, objetivo y ve directo al grano. "
                            "4. No menciones el color de los objetos resaltados. "
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                        ]
                    }
                ],
                model="meta-llama/llama-4-scout-17b-16e-instruct",
            )
            return chat_completion.choices[0].message.content

    except Exception as e:
        return f"Error en la petición: {e}"
    
def find_Groq(prompt):
    try:
        chat_completion = client.chat.completions.create(
        messages=[
                    {
                        "role": "system", 
                        "content": (
                            """Actúa como un extractor automático de entidades. El siguiente texto procede de una persona invidente que desea encontrar un objeto.
                                Tu única finalidad es identificar y extraer el objeto que se está buscando.
                                
                                REGLAS ESTRICTAS E INQUEBRANTABLES:
                                1. Nunca uses saludos, introducciones, explicaciones, ni puntuación final.
                                2. La salida debe ser estrictamente el sustantivo principal del objeto. Nada más.
                                3. Devuelve la palabra siempre en minúsculas.
                                4. Si el usuario menciona características (ej. "taza roja") o nombres compuestos (ej. "gafas de sol"), extrae ÚNICAMENTE el sustantivo base ("taza", "gafas").
                                
                                EJEMPLOS DE SALIDA ESPERADA:
                                Entrada: "¿Dónde he dejado mis llaves?"
                                Salida: llaves
                                
                                Entrada: "Ayúdame a encontrar el bastón, por favor."
                                Salida: bastón
                                
                                Entrada: "Quiero buscar mi teléfono móvil."
                                Salida: teléfono"""
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", 
            )
            
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"Error en la petición: {e}"
    
def SpeechToText():
    reconocedor = sr.Recognizer()
    
    with sr.Microphone() as origen:
        
        # Calibración del ruido
        print("\n Calibrando el ruido de fondo...")
        reconocedor.adjust_for_ambient_noise(origen)
        
        # Decir la instrucción
        TextToSpeech("Dime lo que deseas buscar...")
        
        # Guardar la respuesta
        audio = reconocedor.listen(origen)
        
    try:
        
        # Intentamos pasar el audio a texto
        texto_detectado = reconocedor.recognize_whisper(
            audio, 
            model="small", 
            language="spanish" # Obligamos al modelo a escuchar en español
        )
        
        # Limpiamos el archivo
        texto_detectado = texto_detectado.strip()
        
        return texto_detectado
        
    except sr.UnknownValueError:
        # Error de no comprensión
        TextToSpeech("No he podido entenderte, por favor inténtalo de nuevo.") 
        return None
        
    except Exception as e:
        # Error técnico
        TextToSpeech("Ha ocurrido un error técnico al procesar el audio.")
        return None

# Funciones para el modo navegación

def escuchar_destino_whisper():
    rec = sr.Recognizer()
    
    with sr.Microphone() as origen:
        # Calibramos el ruido de fondo
        rec.adjust_for_ambient_noise(origen)
        
        # Preguntamos el destino
        TextToSpeech("Dime tu destino...")
        
        # Guardamos la respuesta
        audio = rec.listen(origen)
        
    try:
        # Pasamos el audio detectado a texto
        texto_detectado = rec.recognize_whisper(
            audio, 
            model="small", 
            language="spanish"
        )
        
        # Limpiamos el texto
        texto_detectado = texto_detectado.strip()
        
        # Confirmamos por audio el destino de la ruta
        TextToSpeech(f"Calculando ruta hacia {texto_detectado}.")
        
        return texto_detectado
        
    except sr.UnknownValueError:
        # Error de interpretación
        TextToSpeech("No he podido entenderte, por favor inténtalo de nuevo.") 
        return None
        
    except Exception as e:
        # Error técnico
        TextToSpeech("Ha ocurrido un error técnico al procesar el audio.")
        return None

def obtener_ciudad_actual(gmaps, coordenadas_gps):
    try:
        # Pasamos las coordenadas geográficas a google
        resultados = gmaps.reverse_geocode(coordenadas_gps)
        
        if resultados:
            # Nos quedamos con la ciudad
            for componente in resultados[0]['address_components']:
                if 'locality' in componente['types']:
                    ciudad = componente['long_name']
                    return ciudad
                    
            # Si no hay ciudad (estamos en un pueblo) buscamos la provincia
            for componente in resultados[0]['address_components']:
                if 'administrative_area_level_2' in componente['types']:
                    provincia = componente['long_name']
                    return provincia
        
        # Si no se encuentra nada, se devuelve un texto vacío
        return ""
        
    except Exception as e:
        # Si hay algún error, se devuelve un texto vacío
        return ""
   
def obtener_destino_valido(gmaps, origen_gps):
    ciudad_actual = obtener_ciudad_actual(gmaps, origen_gps)
    
    while True: 
        destino_hablado = escuchar_destino_whisper()
        
        if destino_hablado:
            
            resultados_global = gmaps.geocode(destino_hablado)
            
            se_dijo_ciudad = False
            ciudad_detectada = None
            
            if resultados_global:
                for comp in resultados_global[0]['address_components']:
                    if 'locality' in comp['types'] or 'administrative_area_level_2' in comp['types']:
                        ciudad_detectada = comp['long_name']
                        break

                if ciudad_detectada and ciudad_detectada.lower() in destino_hablado.lower():
                    texto_min = destino_hablado.lower().strip()
                    ciudad_min = ciudad_detectada.lower()
                    
                    if f" en {ciudad_min}" in texto_min or f" a {ciudad_min}" in texto_min or texto_min == ciudad_min:
                        se_dijo_ciudad = True
            
            if se_dijo_ciudad:
                tipos = resultados_global[0].get('types', [])
                es_generico = 'locality' in tipos or 'country' in tipos
                es_parcial = resultados_global[0].get('partial_match', False)
                
                if es_parcial and es_generico:
                    TextToSpeech(f"No encuentro ese lugar exacto en {ciudad_detectada}. Por favor, dímelo de nuevo.")
                    continue
                else:
                    direccion_oficial = resultados_global[0]['formatted_address']
                    TextToSpeech(f"Destino encontrado. Calculando ruta hacia {direccion_oficial}.")
                    return direccion_oficial
                    
            else:
                mejor_resultado = None
                menor_distancia = float('inf') 
                
                # Búsqueda local
                if ciudad_actual:
                    resultados_local = gmaps.geocode(f"{destino_hablado}, {ciudad_actual}")
                    if resultados_local:
                        t = resultados_local[0].get('types', [])
                        p = resultados_local[0].get('partial_match', False)
                        
                        if not (p and ('locality' in t or 'country' in t)):
                            lat = resultados_local[0]['geometry']['location']['lat']
                            lng = resultados_local[0]['geometry']['location']['lng']
                            dist = geodesic(origen_gps, (lat, lng)).kilometers
                            
                            if dist < menor_distancia:
                                menor_distancia = dist
                                mejor_resultado = resultados_local[0]
                                
                # Búsqueda global
                if resultados_global:
                    t = resultados_global[0].get('types', [])
                    p = resultados_global[0].get('partial_match', False)
                    
                    es_nuestra_ciudad_por_defecto = ciudad_actual and (ciudad_actual.lower() in resultados_global[0]['formatted_address'].lower())
                    es_pais = 'country' in t
                    
                    if not (p and (es_pais or es_nuestra_ciudad_por_defecto)):
                        lat = resultados_global[0]['geometry']['location']['lat']
                        lng = resultados_global[0]['geometry']['location']['lng']
                        dist = geodesic(origen_gps, (lat, lng)).kilometers
                        
                        if dist < menor_distancia:
                            menor_distancia = dist
                            mejor_resultado = resultados_global[0]
                            
                # Devolvemos el resultado
                if mejor_resultado:
                    direccion_oficial = mejor_resultado['formatted_address']
                    TextToSpeech(f"Destino encontrado. Calculando ruta hacia {direccion_oficial}.")
                    return direccion_oficial
                else:
                    TextToSpeech("No he podido encontrar ese lugar cerca de ti. Por favor, dímelo de nuevo.")
                    continue
        else:
            TextToSpeech("Vamos a intentarlo otra vez.")

def calcular_ruta(gmaps, origen, destino, modo_transporte="walking"):
    
    # Solicitamos la ruta maps
    now = datetime.now()
    try:
        resultado = gmaps.directions(origen,
                                     destino,
                                     mode=modo_transporte,
                                     departure_time=now,
                                     language="es")
        
        # Procesamos la respuesta
        if resultado:
            # Extraemos la información del primer trayecto
            ruta = resultado[0]['legs'][0]
            distancia = ruta['distance']['text']
            duracion = ruta['duration']['text']

            print("-" * 40)
            print(f"Distancia total: {distancia}")
            print(f"Tiempo estimado: {duracion}")
            print("-" * 40)
            print("Instrucciones paso a paso:")

            # Iteramos sobre los pasos para mostrarlos
            for paso in ruta['steps']:
                # Limpiamos el texto html
                instruccion_limpia = re.sub(r'<[^>]+>', '', paso['html_instructions'])
                distancia_paso = paso['distance']['text']
                
                print(f" > {instruccion_limpia} ({distancia_paso})")
            return resultado
        else:
            TextToSpeech("No se encontró ninguna ruta entre esos dos puntos.")
            
    except Exception as e:
        TextToSpeech("Ocurrió un error al conectar con la API de maps")

#  Función simulada para obtener tu GPS
def obtener_mi_ubicacion_actual():
    # Coordenadas en formato (Latitud, Longitud)
    return (39.4699, -0.37628) 

def iniciar_navegacion(pasos_de_la_ruta):
    
    for paso in pasos_de_la_ruta:
        # Limpiamos el HTML de la instrucción de maps
        instruccion_limpia = re.sub(r'<[^>]+>', '', paso['html_instructions'])
        
        # Leemos la instrucción
        TextToSpeech(instruccion_limpia)
        
        #  Sacamos las coordenadas de dónde termina este tramo 
        coordenadas_fin_tramo = (paso['end_location']['lat'], paso['end_location']['lng'])
        
        tramo_completado = False
        
        # Entramos en el bucle mientras caminamos por este tramo
        while not tramo_completado:
            mi_ubicacion = obtener_mi_ubicacion_actual()
            distancia_metros = geodesic(mi_ubicacion, coordenadas_fin_tramo).meters
            
            print(f"A {distancia_metros:.0f} metros de la próxima indicación...")
            
            # Verificamos si es momento de dar la siguiente orden (distancia <= 12 metros)
            if distancia_metros <= 12:
                tramo_completado = True 
            else:
                time.sleep(2)
                
    TextToSpeech("Has llegado a tu destino. Navegación finalizada.")
    
def iniciar_navegacion_simulada(pasos_de_la_ruta, ubicacion_inicial):
    print("\n" + "="*40)
    print("INICIANDO SIMULACIÓN DE NAVEGACIÓN")
    print("="*40 + "\n")
    
    # Guardamos la posición inicial
    mi_ubicacion_simulada = ubicacion_inicial
    
    for paso in pasos_de_la_ruta:
        # el HTML de la instrucción de maps
        instruccion_limpia = re.sub(r'<[^>]+>', '', paso['html_instructions'])
        TextToSpeech(instruccion_limpia)
        
        # Obtenemos las coordenadas de final del tramo
        coordenadas_fin_tramo = (paso['end_location']['lat'], paso['end_location']['lng'])
        tramo_completado = False
        
        # Simulamos que estamos andando hacia el objetivo
        while not tramo_completado:
            
            lat_actual, lng_actual = mi_ubicacion_simulada
            lat_fin, lng_fin = coordenadas_fin_tramo
            
            nueva_lat = lat_actual + (lat_fin - lat_actual) * 0.30
            nueva_lng = lng_actual + (lng_fin - lng_actual) * 0.30
            mi_ubicacion_simulada = (nueva_lat, nueva_lng)
            
            # Calculamos la distancia al punto objetivo
            distancia_metros = geodesic(mi_ubicacion_simulada, coordenadas_fin_tramo).meters
            
            print(f"Distancia a la maniobra: {distancia_metros:.0f} metros")
            
            # Verificamos si es momento de dar la siguiente orden (distancia <= 12 metros)
            if distancia_metros <= 12:
                tramo_completado = True 
            else:
                time.sleep(1.5) 