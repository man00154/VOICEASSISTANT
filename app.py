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
    
def get_llm_response(client, input_text):
    messages = [
        {"role":"system", "content":"You are a helpful assistant"},
        {"role":"user", "content":input_text}
    ]
    response = client.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages = messages
    )
    return response.choices[0].message.content

def convert_text_to_audio(client, text, audio_path):
    with client.audio.speech.with_streaming_response.create(
        model='tts-1', voice='nova',  input=text
    ) as response:
        response.stream_to_file(audio_path) 

def autoplay_audio(audio_file):
    with open(audio_file, 'rb') as file:
        audio_bytes = file.read()
    base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    audio = f'<audio src="data:audio/mp3;base64,{base64_audio}" controls autoplay>'
    st.markdown(audio, unsafe_allow_html=True)       

def create_card(title, text):
    # Define CSS for the card
    card_css = """
    <style>
    .card {
        border-style: solid;
        border-radius: 15px;
        box-shadow: 0 10px 10px rgba(0, 0, 0, 0.2);
        padding: 20px;
        margin: 20px 0;
        background-color: white;
    }
    .card-title {
        font-size: 24px;
        font-weight: bold;
    }
    .card-text {
        font-size: 16px;
        color: #555;
    }
    </style>
    """
    
    # Create the card HTML
    card_html = f"""
    <div class="card">
        <div class="card-title">{title}</div>
        <div class="card-text">{text}</div>
    </div>
    """
    
    # Render the card with CSS
    st.markdown(card_css ,unsafe_allow_html=True)
    st.markdown(card_html,unsafe_allow_html=True)

def application():
    st.set_page_config(page_title="Voice LLM - Manish Singh", page_icon='🎤')
    st.title("Voice LLM - Manish Singh 🤖")
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
                delete_audio_if_exists("audio_response.mp3")
                save_input_recording(recorded_audio)
                transcribed_text = transcribe_audio(client, 'audio.mp3')
                create_card("User Input", transcribed_text)
                ai_response = get_llm_response(client, transcribed_text)
                audio_response_file = "audio_response.mp3"
                convert_text_to_audio(client, ai_response, audio_response_file)
                autoplay_audio(audio_response_file)
                create_card("AI Response", ai_response)              

# Run the application
if __name__ == "__main__":
    application()