import os
import streamlit as st
from docx import Document
import google.generativeai as genai
import textwrap
from IPython.display import Markdown

# Configurar la API con tu clave
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key='AIzaSyAtiOxtcjunWyZS1fK1tX7rkFpa9q6FAw8')

model = genai.GenerativeModel("gemini-pro")

# Función para convertir texto a Markdown
def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Función para dividir texto en fragmentos
def divide_text(text, max_length):
    for i in range(0, len(text), max_length):
        yield text[i:i + max_length]

# Función para procesar el documento subido
@st.cache_resource
def process_document(uploaded_file):
    document = Document(uploaded_file)
    full_text = "\n".join([para.text for para in document.paragraphs if para.text.strip()])
    responses = []

    if full_text:
        chat = model.start_chat(history=[])
        for fragment in divide_text(full_text, max_length=2048):
            try:
                response = chat.send_message(fragment)
                responses.append(response.text)
            except genai.types.generation_types.StopCandidateException as e:
                print("Error al enviar el fragmento: ", e)
                continue

    st.write("El texto ha sido procesado. Puedes hacer preguntas basadas en el texto.")
    return full_text, responses, chat

# Función principal de la aplicación
def main():
    st.title("Chatbot UNEG")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'full_text' not in st.session_state:
        st.session_state.full_text = ""

    if 'responses' not in st.session_state:
        st.session_state.responses = []

    # Interfaz de usuario
    uploaded_file = st.file_uploader("Choose a file to upload", type="docx", key="file_uploader")
    
    if uploaded_file:
        full_text, responses, chat = process_document(uploaded_file)
        st.session_state.full_text = full_text
        st.session_state.responses = responses
        st.session_state.chat = chat

    user_input = st.text_input("Ingresa tu consulta:", key="user_query")
    
    if st.button("Send", key="send_button"):
        if user_input:
            st.write("Usuario:", user_input)
            if 'chat' not in st.session_state:
                st.session_state.chat = model.start_chat(history=st.session_state.chat_history)
            
            document_context = "\n".join(st.session_state.responses)
            combined_input = f"Documento: {document_context}\nPregunta: {user_input}"
            try:
                response = st.session_state.chat.send_message(combined_input)
                st.session_state.chat_history.append({"role": "Usuario", "content": user_input})
                st.session_state.chat_history.append({"role": "Bot", "content": response.text})
                st.write("Bot:", response.text)
            except genai.types.generation_types.StopCandidateException as e:
                print("Error al enviar el mensaje: ", e)
        else:
            st.write("Por favor ingresa una pregunta.")

    # Mostrar historial de chat
    if st.session_state.chat_history:
        st.write("Historial de Chat:")
        for entry in st.session_state.chat_history:
            if isinstance(entry, dict) and 'role' in entry and 'content' in entry:
                role = entry["role"]
                content = entry["content"]
                st.write(f"{role}: {content}")

    # Opción para descargar historial de chat
    if st.session_state.chat_history:
        chat_history_str = "\n\n".join([f"{entry['role']}: {entry['content']}" for entry in st.session_state.chat_history if isinstance(entry, dict) and 'role' in entry and 'content' in entry])
        st.download_button(
            label="Descargar Historial de Chat",
            data=chat_history_str,
            file_name="chat_history.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()
