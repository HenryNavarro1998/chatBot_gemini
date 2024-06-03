import pathlib
import textwrap
import os

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key="AIzaSyAtiOxtcjunWyZS1fK1tX7rkFpa9q6FAw8")

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

while True:
    ask = input("You: ")

    if ask.lower() == "exit":
        break

    response = chat.send_message(ask)
    print("R: %s" %response.text)

#API KEY DE GEMINI
#AIzaSyAtiOxtcjunWyZS1fK1tX7rkFpa9q6FAw8
