# Unblinded

Este proyecto, desarrollado por Axel Valton Juan y Joan Merlos Cremades, ha consistido en el desarrollo de un software que permita leer texto, describir paisajes, guiar hacia una determinada dirección y buscar objetos con la intención de hacer más sencillo el día a día de las personas invidentes. Para que este proyecto fuera concluido de forma adecuada se deberian implementar estas funciones en un dispositivo que tuviese cámara, micrófono y gps, conectándose a unos auriculares. No obstante, en nuestro caso nos hemos limitado a desarrollar el código para que sea funcional en un ordenador convencional.

Los archivos de código desarrollado son:

* `Unblinded_Script.py`: es el Script principal del código que nos permite elegir entre los diferentes modos de nuestro dispositivo, siendo estos **Lectura**, **Descripción**, **Navegación guiada** (se ha implementado un modo que simula el trayecto de una persona a través de una ruta dada) y **Búsqueda** (que se encuentra en el archivo `Unblinded_busqueda.ipynb`).

* `Unblinded_Functions.py`: es el Script secundario que contiene todas las funciones que permiten que el programa funcione. Cabe destacar que estas funciones utilizan diferentes modelos como gTTS para pasar de texto a audio, Whisper para poder reproducir el audio, google Maps para obtener las rutas y diferentes modelos de la IA generativa `llama` para poder procesar tanto imágenes como texto.

* `Unblinded_busqueda.ipynb`: este archivo nos permite obtener una descripción detallada de la posición espacial de un objeto mencionado. Cabe destacar que se ha realizado en que este modo se encuentra en un archivo por separado debido a que utiliza el modelo sam3, el cual requiere de una targeta gráfica para funcionar. Ante dicha situación hemos obtado por programar dicho modo en un notebook que pueda ser ejecutado fácilmente desde la plataforma google Colab.
