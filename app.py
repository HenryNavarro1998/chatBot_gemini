import os
import streamlit as st
from docx import Document
import google.generativeai as genai
import textwrap
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

# Longitud máxima de cada fragmento (ajústalo según sea necesario)
max_length = 2048  # Ajusta según sea necesario

@st.cache_data
def process_document(uploaded_file):
    documento = Document(uploaded_file)
    full_text = "\n".join([parrafo.text for parrafo in documento.paragraphs if parrafo.text.strip()])
    responses = []

    if full_text:
        chat = model.start_chat(history=[])
        for fragment in divide_text(full_text, max_length):
            try:
                response = chat.send_message(fragment)
                responses.append(response.text)
            except genai.types.generation_types.StopCandidateException as e:
                print("Error al enviar el fragmento: ", e)
                continue

    st.write("El texto ha sido procesado. Puedes hacer preguntas basadas en el texto.")            
    return full_text, responses, chat.history

def main():
    st.title("Chatbot uneg")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    uploaded_file = st.file_uploader("Choose a file to upload", type="docx")
    
    if uploaded_file:
        full_text, responses, chat_history = process_document(uploaded_file)
        st.session_state.full_text = full_text
        st.session_state.responses = responses
        st.session_state.chat_history = chat_history
        
        
        user_input = st.text_input("Enter your Query:")
        if st.button("Send"):
            st.write("You:", user_input)
            try:
                chat = model.start_chat(history=st.session_state.chat_history)
                response = chat.send_message(user_input)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.write("Bot: " + response.text)
            except genai.types.generation_types.StopCandidateException as e:
                print("Error al enviar el mensaje: ", e)

if __name__ == "__main__":
    main()
