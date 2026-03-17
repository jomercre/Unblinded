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
import easyocr


#  Inicializar el mezclador de audio de pygame
pygame.mixer.init()

#  Inicializar el cliente con API Key
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=API_KEY)

def decir_instruccion(texto):
    print(f"🔊 Hablando: '{texto}'")
    
    # Generamos un nombre único basado en el tiempo actual para evitar bloqueos
    nombre_archivo = f"instruccion_{int(time.time())}.mp3"
    
    try:
        # Generar y guardar el audio con el nombre único
        tts = gTTS(text=texto, lang='es', slow=False)
        tts.save(nombre_archivo)
        
        # Cargar y reproducir
        pygame.mixer.music.load(nombre_archivo)
        pygame.mixer.music.play()
        
        # Esperar a que termine de hablar
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Soltar el archivo de la memoria de pygame
        pygame.mixer.music.unload()
        
        # Borrar el archivo de tu disco duro para no dejar basura
        if os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)
            
    except Exception as e:
        print(f"Error al generar o reproducir la voz: {e}")

def escuchar_destino_whisper():
    reconocedor = sr.Recognizer()
    
    with sr.Microphone() as origen:
        print("\n🎤 Calibrando el ruido de fondo...")
        reconocedor.adjust_for_ambient_noise(origen)
        
        print("🗣️ Ya puedes hablar. Dime tu destino...")
        # 1. El asistente te pregunta por voz el destino
        decir_instruccion("Dime tu destino...")
        
        # Escucha tu respuesta
        audio = reconocedor.listen(origen)
        
    try:
        print("⏳ Transcribiendo con Whisper (esto puede tardar unos segundos dependiendo de tu PC)...")
        
        # AQUÍ ESTÁ LA MAGIA DE WHISPER
        texto_detectado = reconocedor.recognize_whisper(
            audio, 
            model="small", 
            language="spanish" # Obligamos al modelo a escuchar en español
        )
        
        # Whisper a veces añade espacios o puntos al final, lo limpiamos un poco
        texto_detectado = texto_detectado.strip()
        
        print(f"✅ Has dicho: '{texto_detectado}'")
        
        # 2. El asistente te confirma que te ha escuchado y va a calcular la ruta
        decir_instruccion(f"Calculando ruta hacia {texto_detectado}.")
        
        return texto_detectado
        
    except sr.UnknownValueError:
        print("❌ Whisper no pudo procesar el audio.")
        # Aviso por voz si no entiende
        decir_instruccion("No he podido entenderte, por favor inténtalo de nuevo.") 
        return None
        
    except Exception as e:
        print(f"❌ Ocurrió un error con Whisper: {e}")
        # Aviso por voz si hay un error técnico
        decir_instruccion("Ha ocurrido un error técnico al procesar el audio.")
        return None

def obtener_ciudad_actual(gmaps, coordenadas_gps):
    print("🌍 Detectando tu ciudad actual...")
    try:
        # Le enviamos las coordenadas (Latitud, Longitud) a Google
        resultados = gmaps.reverse_geocode(coordenadas_gps)
        
        if resultados:
            # Google devuelve mucha info. Buscamos el componente que sea la "ciudad"
            for componente in resultados[0]['address_components']:
                if 'locality' in componente['types']:
                    ciudad = componente['long_name']
                    print(f"📍 Estás en: {ciudad}")
                    return ciudad
                    
            # Si por lo que sea estás en un pueblo sin 'locality', buscamos la provincia
            for componente in resultados[0]['address_components']:
                if 'administrative_area_level_2' in componente['types']:
                    provincia = componente['long_name']
                    print(f"📍 Estás en la provincia de: {provincia}")
                    return provincia
                    
        return "" # Si falla, devolvemos un texto vacío
        
    except Exception as e:
        print(f"❌ Error al detectar la ciudad: {e}")
        return ""
   
def obtener_destino_valido(gmaps, origen_gps):
    ciudad_actual = obtener_ciudad_actual(gmaps, origen_gps)
    
    while True: 
        destino_hablado = escuchar_destino_whisper()
        
        if destino_hablado:
            print(f"🔍 Evaluando '{destino_hablado}'...")
            
            resultados_global = gmaps.geocode(destino_hablado)
            
            se_dijo_ciudad = False
            ciudad_detectada = None
            
            if resultados_global:
                for comp in resultados_global[0]['address_components']:
                    if 'locality' in comp['types'] or 'administrative_area_level_2' in comp['types']:
                        ciudad_detectada = comp['long_name']
                        break
                        
                # 1. COMPROBAR SI SE HA DICHO LA CIUDAD EXPLICÍTAMENTE
                if ciudad_detectada and ciudad_detectada.lower() in destino_hablado.lower():
                    texto_min = destino_hablado.lower().strip()
                    ciudad_min = ciudad_detectada.lower()
                    
                    if f" en {ciudad_min}" in texto_min or f" a {ciudad_min}" in texto_min or texto_min == ciudad_min:
                        se_dijo_ciudad = True
            
            if se_dijo_ciudad:
                print(f"🏙️ Detectado que has especificado la ciudad: {ciudad_detectada}")
                # 2. SI SE HA DICHO LA CIUDAD
                tipos = resultados_global[0].get('types', [])
                es_generico = 'locality' in tipos or 'country' in tipos
                es_parcial = resultados_global[0].get('partial_match', False)
                
                if es_parcial and es_generico:
                    print("❌ Dirección inválida en la ciudad especificada.")
                    decir_instruccion(f"No encuentro ese lugar exacto en {ciudad_detectada}. Por favor, dímelo de nuevo.")
                    continue
                else:
                    direccion_oficial = resultados_global[0]['formatted_address']
                    print(f"✅ Dirección validada: {direccion_oficial}")
                    decir_instruccion(f"Destino encontrado. Calculando ruta hacia {direccion_oficial}.")
                    return direccion_oficial
                    
            else:
                print("📍 No has especificado ciudad. Buscando la dirección más cercana...")
                # 3. SI NO SE HA DICHO LA CIUDAD: Pelea de distancias
                mejor_resultado = None
                menor_distancia = float('inf') 
                
                # --- OPCIÓN A: Búsqueda Local Forzada ---
                if ciudad_actual:
                    resultados_local = gmaps.geocode(f"{destino_hablado}, {ciudad_actual}")
                    if resultados_local:
                        t = resultados_local[0].get('types', [])
                        p = resultados_local[0].get('partial_match', False)
                        
                        # Aquí seguimos siendo ESTRICTOS. Si fuerza la ciudad y da genérico, es trampa.
                        if not (p and ('locality' in t or 'country' in t)):
                            lat = resultados_local[0]['geometry']['location']['lat']
                            lng = resultados_local[0]['geometry']['location']['lng']
                            dist = geodesic(origen_gps, (lat, lng)).kilometers
                            
                            if dist < menor_distancia:
                                menor_distancia = dist
                                mejor_resultado = resultados_local[0]
                                
                # --- OPCIÓN B: Búsqueda Global (Modificada para permitir correcciones) ---
                if resultados_global:
                    t = resultados_global[0].get('types', [])
                    p = resultados_global[0].get('partial_match', False)
                    
                    # LA MAGIA: Permitimos los partial_match de 'locality' (pueblos mal pronunciados).
                    # Solo bloqueamos si devuelve un PAÍS entero o si, por algún error raro, 
                    # nos devuelve nuestra propia ciudad por defecto.
                    es_nuestra_ciudad_por_defecto = ciudad_actual and (ciudad_actual.lower() in resultados_global[0]['formatted_address'].lower())
                    es_pais = 'country' in t
                    
                    if not (p and (es_pais or es_nuestra_ciudad_por_defecto)):
                        lat = resultados_global[0]['geometry']['location']['lat']
                        lng = resultados_global[0]['geometry']['location']['lng']
                        dist = geodesic(origen_gps, (lat, lng)).kilometers
                        
                        if dist < menor_distancia:
                            menor_distancia = dist
                            mejor_resultado = resultados_global[0]
                            
                # --- RESOLUCIÓN ---
                if mejor_resultado:
                    direccion_oficial = mejor_resultado['formatted_address']
                    print(f"✅ Dirección validada (a {menor_distancia:.1f} km): {direccion_oficial}")
                    decir_instruccion(f"Destino encontrado. Calculando ruta hacia {direccion_oficial}.")
                    return direccion_oficial
                else:
                    print("❌ No se encontró ninguna dirección cercana válida.")
                    decir_instruccion("No he podido encontrar ese lugar cerca de ti. Por favor, dímelo de nuevo.")
                    continue
        else:
            decir_instruccion("Vamos a intentarlo otra vez.")

def calcular_ruta(gmaps, origen, destino, modo_transporte="walking"):
    print(f"Calculando ruta desde '{origen}' hasta '{destino}'...\n")
    
    # 2. Solicitar la ruta a la API
    now = datetime.now()
    try:
        resultado = gmaps.directions(origen,
                                     destino,
                                     mode=modo_transporte, # Puede ser "driving", "walking", "bicycling" o "transit"
                                     departure_time=now,
                                     language="es") # Resultados en español
        
        # Procesar la respuesta
        if resultado:
            # Extraemos la información del primer trayecto (leg)
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
                # La API devuelve el texto con etiquetas HTML (ej. <b>Gira a la derecha</b>)
                # Usamos una expresión regular simple para limpiar ese HTML y dejar solo el texto
                instruccion_limpia = re.sub(r'<[^>]+>', '', paso['html_instructions'])
                distancia_paso = paso['distance']['text']
                
                print(f" > {instruccion_limpia} ({distancia_paso})")
            return resultado
        else:
            print("No se encontró ninguna ruta entre esos dos puntos.")
            
    except Exception as e:
        print(f"Ocurrió un error al conectar con la API: {e}")



#  Función simulada para obtener tu GPS
def obtener_mi_ubicacion_actual():
    # Coordenada simulada de ejemplo (Latitud, Longitud)
    return (39.4699, -0.37628) 


def iniciar_navegacion(pasos_de_la_ruta):
    print("Iniciando ruta a pie...")
    
    for paso in pasos_de_la_ruta:
        # Limpiamos el HTML de la instrucción de Google Maps tal cual viene
        instruccion_limpia = re.sub(r'<[^>]+>', '', paso['html_instructions'])
        
        # Leemos la instrucción (Porque es el momento de hacer la maniobra)
        decir_instruccion(instruccion_limpia)
        
        #  Sacamos las coordenadas de dónde termina este tramo 
        # (que será la esquina donde tocará hacer el SIGUIENTE giro)
        coordenadas_fin_tramo = (paso['end_location']['lat'], paso['end_location']['lng'])
        
        tramo_completado = False
        
        # Entramos en el bucle mientras caminamos por este tramo
        while not tramo_completado:
            mi_ubicacion = obtener_mi_ubicacion_actual() # Tu lectura de GPS real
            distancia_metros = geodesic(mi_ubicacion, coordenadas_fin_tramo).meters
            
            print(f"A {distancia_metros:.0f} metros de la próxima indicación...")
            
            # El margen: Si estamos a 12 metros o menos de terminar el tramo...
            if distancia_metros <= 12:
                # Salimos del bucle while. 
                # El bucle 'for' avanzará al siguiente paso y te leerá la siguiente maniobra.
                tramo_completado = True 
            else:
                # Si aún estamos lejos, esperamos 2 segundos y seguimos midiendo
                time.sleep(2)
                
    decir_instruccion("Has llegado a tu destino. Navegación finalizada.")




    
def iniciar_navegacion_simulada(pasos_de_la_ruta, ubicacion_inicial):
    print("\n" + "="*40)
    print("🚶 INICIANDO SIMULACIÓN DE NAVEGACIÓN")
    print("="*40 + "\n")
    
    # Esta variable guardará nuestra posición falsa, que irá cambiando
    mi_ubicacion_simulada = ubicacion_inicial
    
    for paso in pasos_de_la_ruta:
        # Leemos la instrucción limpia
        instruccion_limpia = re.sub(r'<[^>]+>', '', paso['html_instructions'])
        decir_instruccion(instruccion_limpia)
        
        # Meta: el final de este tramo
        coordenadas_fin_tramo = (paso['end_location']['lat'], paso['end_location']['lng'])
        tramo_completado = False
        
        while not tramo_completado:
            # --- MAGIA DE LA SIMULACIÓN ---
            # Matemáticamente, avanzamos un 30% de la distancia restante hacia el destino
            # simulando que estamos caminando hacia esa coordenada
            lat_actual, lng_actual = mi_ubicacion_simulada
            lat_fin, lng_fin = coordenadas_fin_tramo
            
            nueva_lat = lat_actual + (lat_fin - lat_actual) * 0.30
            nueva_lng = lng_actual + (lng_fin - lng_actual) * 0.30
            mi_ubicacion_simulada = (nueva_lat, nueva_lng)
            # ------------------------------
            
            # Calculamos a qué distancia estamos ahora de la meta
            distancia_metros = geodesic(mi_ubicacion_simulada, coordenadas_fin_tramo).meters
            
            print(f"   👣 Caminando... (Distancia a la maniobra: {distancia_metros:.0f} metros)")
            
            # Si bajamos del umbral de 12 metros, pasamos al siguiente paso
            if distancia_metros <= 12:
                print("   ✅ ¡Llegando a la esquina! Cargando siguiente instrucción...\n")
                tramo_completado = True 
            else:
                # En la simulación esperamos 1.5 segundos para que veas el progreso en consola
                time.sleep(1.5) 
                
    decir_instruccion("Has llegado a tu destino. Navegación finalizada.")



# Funciones para utilizar IA generativa

def ReadMode(img_path):

    lector = easyocr.Reader(['es'])
    
    resultados = lector.readtext(img_path)
    
    lista_de_textos = [fragmento[1] for fragmento in resultados]

    # Unimos todo el texto en una única variable
    text = " ".join(lista_de_textos)
    
    return text

def TextToSpeech(texto):
    
    # Generamos un nombre único basado en el tiempo actual para evitar bloqueos
    nombre_archivo = f"instruccion_{int(time.time())}.mp3"
    
    try:
        # Generar y guardar el audio con el nombre único
        tts = gTTS(text=texto, lang='es', slow=False)
        tts.save(nombre_archivo)
        
        # Cargar y reproducir
        pygame.mixer.music.load(nombre_archivo)
        pygame.mixer.music.play()
        
        # Esperar a que termine de hablar
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        # Soltar el archivo de la memoria de pygame
        pygame.mixer.music.unload()
        
        # Borrar el archivo de tu disco duro para no dejar basura
        if os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)
        else:
            print('No se ha podido borrar')
            
    except Exception as e:
        print(f"Error al generar o reproducir la voz: {e}")
    
    return

def image_file_to_base64(image_path):
    try:
        # Abrimos el archivo en modo lectura binaria ("rb")
        with open(image_path, "rb") as image_file:
            # Leemos y codificamos el archivo
            encoded_string = base64.b64encode(image_file.read())
            # Lo decodificamos a utf-8 para que sea una cadena de texto normal
            return encoded_string.decode('utf-8')
    except Exception as e:
        print(f"Error al leer la imagen: {e}")
        return None

def ask_Groq(prompt=None, img_path=None, Danger=False):
    try:
        if img_path is None and Danger == False:
            # Modo solo texto: usamos un modelo optimizado para texto
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
            # Modo solo texto: usamos un modelo optimizado para texto
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "Eres un asistente de accesibilidad visual para personas ciegas."
                            "REGLAS ESTRICTAS: "
                            "1. El texto de entrada procede de una imagen, si encuentras algun peligro para personas invidentes añadelo a principio del texto."
                            "2. En caso de no detectar peligro no indiques que no hay peligro, limitate a realizar un resumen del texto."
                            "3. NUNCA uses saludos, introducciones (como 'Aquí tienes', 'Me encantaría describir', 'En la imagen se ve') ni despedidas. "
                            "4. Sé extremadamente preciso, objetivo y ve directo al grano."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", 
            )
            return chat_completion.choices[0].message.content

        elif prompt is None:

            img_base64 = image_file_to_base64(img_path)

            # Modo solo imagen con instrucciones predeterminadas
            text_prompt = "Soy una persona ciega que quiero obtener información detallada de la siguiente imagen:"
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "Eres un asistente de accesibilidad visual para personas ciegas. "
                            "REGLAS ESTRICTAS: "
                            "1. Responde ÚNICAMENTE con la descripción de la imagen o la advertencia de peligro. "
                            "2. NUNCA uses saludos, introducciones ni despedidas. ")
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

            # Modo texto e imagen
            text_prompt = f"Soy una persona ciega que quiero obtener información de la siguiente imagen: {prompt}"
            
            chat_completion = client.chat.completions.create(
                messages=[
                                {
                        "role": "system", 
                        "content": (
                            "Eres un asistente de accesibilidad visual para personas ciegas. "
                            "REGLAS ESTRICTAS: "
                            "1. Responde ÚNICAMENTE con la descripción de la imagen o la advertencia de peligro. "
                            "2. NUNCA uses saludos, introducciones (como 'Aquí tienes', 'Me encantaría describir', 'En la imagen se ve') ni despedidas. "
                            "3. Sé extremadamente preciso, objetivo y ve directo al grano. "
                            "4. Si hay un peligro, indícalo como primera palabra. En caso contrario no hace falta que indiques que no hay peligro."
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
        # Modo solo texto: usamos un modelo optimizado para texto
        chat_completion = client.chat.completions.create(
        messages=[
                    {
                        "role": "system", 
                        "content": (
                            "El texto procede de una persona invidente que desea encontrar un objeto."
                            "Tu finalidad es extraer del texto el objeto que se está buscando."
                            "REGLAS ESTRICTAS: "
                            "1. NUNCA uses saludos, introducciones (como 'Aquí tienes', 'Me encantaría describir', 'En la imagen se ve') ni despedidas. "
                            "2. Sé extremadamente preciso, objetivo y ve directo al grano. "
                            "3. La salida está limitada a una única palabra. "
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile", 
            )
            
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"Error en la petición: {e}"