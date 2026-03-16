# --------------------------------------------------
# -                 Unblinded                      -
# --------------------------------------------------
#
# Creadores: Axel Valton Juan & Joan Merlos Cremades

# Libraries

from PIL import Image
import easyocr
from gtts import gTTS
import os

# Functions

# !!!Añadir idioma como entrada!!!

def ReadMode(img_path):

    lector = easyocr.Reader(['es'])
    
    resultados = lector.readtext(img_path)
    
    lista_de_textos = [fragmento[1] for fragmento in resultados]

    # Unimos todo el texto en una única variable
    text = " ".join(lista_de_textos)
    
    return text

def TextToSpeech(text):
    
    tts = gTTS(text=text, lang='es', slow=False)
    
    tts.save("lectura.mp3")
    
    os.system("start lectura.mp3")
    
    return


# Mode selector

M = 'R'
'''
print('Available models:')
print('Read -> R')
print('Description -> D')
print('Navigation -> N')
print('Detector -> D\n')

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

img_path = 'example_read.jpeg'

# Generate text

if M == 'R':
    
    text = ReadMode(img_path)

# Generate audio

audio = TextToSpeech(text)


