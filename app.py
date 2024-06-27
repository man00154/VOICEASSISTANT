import streamlit as st
import openai
import base64
from st_audiorec import st_audiorec
import os

def save_input_recording(recorded_audio, file_path='audio.mp3'):
    with open(file_path, 'wb') as file:
        file.write(recorded_audio)

def delete_audio_if_exists(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def transcribe_audio(client, audio_path):
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model='whisper-1', file=audio_file, language='en'
        )
        return transcript.text


def application():
    st.set_page_config(page_title="Voice LLM - Utkarsh", page_icon='🎤')
    st.title("Voice LLM - Utkarsh Gaikwad 🤖")
    st.subheader("Please enter OpenAI api key in sidebar first")
    
    # Sidebar
    with st.sidebar:
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            st.success("Done")

    # If api key is written
    if api_key:
        client = openai.OpenAI(api_key=api_key)
        st.write("Click Start Recording to Record and Stop once Done🎙️")
        recorded_audio = st_audiorec()
        if recorded_audio:
            with st.spinner("Processing"):
                delete_audio_if_exists("audio.mp3")
                save_input_recording(recorded_audio)
                transcribed_text = transcribe_audio(client, 'audio.mp3')
                st.write(f"User Input : {transcribed_text}")

# Run the application
if __name__ == "__main__":
    application()