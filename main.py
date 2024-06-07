import pathlib
import textwrap
import os
from docx import Document
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def divide_text(text, max_length):
    for i in range(0, len(text), max_length):
        yield text[i:i + max_length]

# Configurar la API con tu clave
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key="AIzaSyAtiOxtcjunWyZS1fK1tX7rkFpa9q6FAw8")

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Longitud máxima de cada fragmento (ajústalo según sea necesario)
max_length = 2048  # Ajusta según sea necesario

# Cargar el documento
documento = Document('documento.docx')

# Leer todo el contenido del documento
full_text = "\n".join([parrafo.text for parrafo in documento.paragraphs if parrafo.text.strip()])

# Dividir el texto en fragmentos y enviar cada uno
for fragment in divide_text(full_text, max_length):
    try:
        response = chat.send_message(fragment)
        #print("R: %s" % response.text)
        #print("_" * 80)
    except genai.types.generation_types.StopCandidateException as e:
        print("Error al enviar el fragmento: ", e)
        continue

print("El texto ha sido procesado. Puedes hacer preguntas basadas en el texto.")

# Conversación interactiva después de enviar el archivo
while True:
    ask = input("You: ")

    if ask.lower() == "exit":
        break

    try:
        response = chat.send_message(ask)
        print("R: %s" % response.text)
    except genai.types.generation_types.StopCandidateException as e:
        print("Error al enviar el mensaje: ", e)


#API KEY DE GEMINI
#AIzaSyAtiOxtcjunWyZS1fK1tX7rkFpa9q6FAw8
