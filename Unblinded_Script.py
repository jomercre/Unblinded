# --------------------------------------------------
# -                 Unblinded                      -
# --------------------------------------------------
#
# Creadores: Axel Valton Juan & Joan Merlos Cremades

# Librerías

from funciones_navegacion import *
import tkinter as tk
from tkinter import ttk, messagebox

# Selector de modos

M = ''

def confirmar_seleccion():
    
    global M
    
    M = combo.get()
    messagebox.showinfo("Selección Final", f"Has elegido: {M}")
    ventana.destroy()

ventana = tk.Tk()
ventana.title("Selector de modos")
ventana.geometry("350x200")
label = tk.Label(ventana, text="¿Qué modo deseas activar?", font=("Arial", 12))
label.pack(pady=20)
opciones = ["Lectura", "Descripción", "Navegación guiada", "Búsqueda"]
combo = ttk.Combobox(ventana, values=opciones, state="readonly")
combo.pack(pady=5)
combo.current(0)
boton = tk.Button(ventana, text="Ejecutar", command=confirmar_seleccion, bg="#4CAF50", fg="white")
boton.pack(pady=20)
ventana.mainloop()

# Imagen de entrada

img_path = 'new_img.png'

# Generar el texto de salida

if M == 'Lectura':
    
    # Leer la imagen
    
    text = ReadMode(img_path)
    
    # Detectar si hay texto
    
    if text == "":
        text = "Texto no detectado"
    else:
        
        # Corrección del texto
        
        Intro = "Corrige el siguiente texto, añadiendo artículos y cambiando palabras si es necesario, para que sea más comprensible: "
        Conc = " Devuelve únicamente la versión corregida del texto, no añadas ningún comentario adicional."
        corr_prompt = Intro + text + Conc
                        
        text = ask_Groq(prompt = corr_prompt)
    
elif M == 'Descripción':
    
    # Obtener información de la imagen
    
    descr = ask_Groq(img_path=img_path)
    
    # Detectar si hay peligro
    
    text = ask_Groq(prompt=descr, Danger = True)
    
elif M == 'Navegación guiada':
    
    origen_gps = (39.4699, -0.3763)
    
    '''
    destino_texto = obtener_destino_valido(gmaps, origen_gps)
    
    # Corrección del texto
    
    Intro = "Corrige el siguiente texto, añadiendo artículos y cambiando palabras si es necesario, para que sea más comprensible: "
    Conc = " Devuelve únicamente la versión corregida del texto, no añadas ningún comentario adicional."
    corr_prompt = Intro + text + Conc
                    
    text = ask_Groq(prompt = corr_prompt)
    '''
    
    text = 'Ciudad de las artes y las ciencias'
    
    # Cálculo de la ruta
    mi_ubicacion = "Valencia, España" 
    mi_destino = text
    
    resultado=calcular_ruta(gmaps, mi_ubicacion, mi_destino)
    
    # Comprobamos que exista una ruta válida
    
    if resultado:
        # Iniciamos la navegación simulada
        
        pasos = resultado[0]['legs'][0]['steps']
        iniciar_navegacion_simulada(pasos, origen_gps)
    
    text = "Has llegado a tu destino. Navegación finalizada."
    
elif M == 'Búsqueda':

    # Tratamiento del texto obtenido
    
    text = None
    
    while text is None:
        
        text = SpeechToText()
        
     # Corrección del texto
     
    Intro = "Corrige el siguiente texto, añadiendo artículos y cambiando palabras si es necesario, para que sea más comprensible: "
    Conc = " Devuelve únicamente la versión corregida del texto, no añadas ningún comentario adicional."
    corr_prompt = Intro + text + Conc
                     
    text = ask_Groq(prompt = corr_prompt)

    # Reducción del texto

    text = find_Groq(prompt=text)

    # Traduccción del texto al inglés

    Intro = "Traduceme el siguiente texto a inglés: "
    prompt = Intro + text

    prompt = ask_Groq(prompt=prompt)
    print(prompt)
    
    input('Pon cualquier cosa cuando hayas obtenido la imagen: ')
    
    # Obtener información de la imagen
    
    prompt = """Actúa como un asistente experto en accesibilidad visual. Te voy a proporcionar una imagen donde hay varios objetos resaltados explícitamente con colores vistosos.
                Tu objetivo es ayudar a una persona ciega a construir un mapa mental preciso de la escena. Por favor, sigue exactamente estos pasos:
                            
                1. Describe en una sola oración el entorno general de la imagen (por ejemplo, 'Es una cocina vista desde el frente' o 'Es una calle concurrida').
                2. Por cada objeto resaltado que detectes, indica qué es y detalla su posición utilizando una cuadrícula imaginaria de 3x3 (arriba/centro/abajo y izquierda/centro/derecha). 
                3. Si hay varios objetos resaltados, describe brevemente cómo están ubicados unos respecto a otros (ej. 'El objeto A está justo a la derecha y ligeramente por delante del objeto B').
                            
                Ignora los objetos que no estén resaltados, a menos que sean un punto de referencia indispensable para ubicar a los que sí lo están. Sé claro, objetivo y preciso."""

    text = ask_Groq(img_path=img_path, prompt=prompt)
    
# Generar el audio de salida

TextToSpeech(text)

