import googlemaps
import re
from datetime import datetime
import time
import os
from gtts import gTTS
import pygame
from geopy.distance import geodesic
import speech_recognition as sr

#  Inicializar el mezclador de audio de pygame
pygame.mixer.init()

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