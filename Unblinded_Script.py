# --------------------------------------------------
# -                 Unblinded                      -
# --------------------------------------------------
#
# Creadores: Axel Valton Juan & Joan Merlos Cremades

# Libraries

from funciones_navegacion import *

# Mode selector

M = 'F'
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
    print('Detector -> D\n')
    
    M = input('Mode: ')
'''

# Image input

img_path = 'example_read_pc.png'

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

elif M == 'F':

    # Tratamiento del texto obtenido

    text = "Quiero que me digas donde se encuentra el pelo"

    # Reduction of the text

    text = find_Groq(prompt=text)

    # Traduction to english

    Intro = "Traduceme el siguiente texto a inglés: "
    prompt = Intro + text

    prompt = ask_Groq(prompt=prompt)
    print(prompt)
    text = prompt
    
# Generate audio

TextToSpeech(text)


