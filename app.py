import os
import streamlit as st
from docx import Document
import google.generativeai as genai
import textwrap
from IPython.display import Markdown
import io

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
    st.title("Chatbot UNEG")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'full_text' not in st.session_state:
        st.session_state.full_text = ""
    if 'responses' not in st.session_state:
        st.session_state.responses = []

    # Proporcionar una clave única para el file_uploader
    uploaded_file = st.file_uploader("Choose a file to upload", type="docx", key="file_uploader")
    
    if uploaded_file:
        full_text, responses, chat_history = process_document(uploaded_file)
        st.session_state.full_text = full_text
        st.session_state.responses = responses
        st.session_state.chat_history = chat_history

    user_input = st.text_input("Enter your Query:", key="user_query")
    if st.button("Send", key="send_button"):
        if user_input:
            st.write("You:", user_input)
            chat = model.start_chat(history=st.session_state.chat_history)
            # Limitar el contexto a la información del documento procesado
            document_context = "\n".join(st.session_state.responses)
            combined_input = f"Documento: {document_context}\nPregunta: {user_input}"
            try:
                response = chat.send_message(combined_input)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.write("Bot: " + response.text)
            except genai.types.generation_types.StopCandidateException as e:
                print("Error al enviar el mensaje: ", e)
        else:
            st.write("Por favor, ingresa una pregunta.")

    if st.session_state.chat_history:
        st.write("Historial de chat:")
        chat_history_str = ""
        for entry in st.session_state.chat_history:
            if isinstance(entry, dict):  # Verificar que entry sea un diccionario
                role = "Tú" if entry["role"] == "user" else "Bot"
                content = entry["content"]
                chat_history_str += f"{role}: {content}\n"
                st.write(f"{role}: {content}")
        
        # Opción para descargar el historial de chat
        st.download_button(
            label="Descargar historial de chat",
            data=chat_history_str,
            file_name="chat_history.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
