# --------------------------------------------------
# -                 Unblinded                      -
# --------------------------------------------------
#
# Creadores: Axel Valton Juan & Joan Merlos Cremades

# Librerías

from Unblinded_Functions import *
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

img_path = 'Imagenes de ejemplo/new_img.png'

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
    
    destino_texto = obtener_destino_valido(gmaps, origen_gps)
    
    # Corrección del texto
    
    Intro = "Corrige el siguiente texto, añadiendo artículos y cambiando palabras si es necesario, para que sea más comprensible: "
    Conc = " Devuelve únicamente la versión corregida del texto, no añadas ningún comentario adicional."
    corr_prompt = Intro + destino_texto + Conc
                    
    text = ask_Groq(prompt = corr_prompt)
    
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

    text = 'Para utilizar el modo búsqueda utiliza el archivo Unblinded_busqueda.ipynb'
    
# Generar el audio de salida

TextToSpeech(text)

