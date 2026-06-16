import streamlit as st
import requests
from io import BytesIO
from PIL import Image
from langchain_ollama import OllamaLLM
import pypdf
import speech_recognition as sr
import pyttsx3

st.set_page_config(page_title="Local AI Hub", layout="centered")
st.title("?? My Local AI Workspace")

tab1, tab2 = st.tabs(["?? Chat Assistant", "?? AI Image Generator"])

def speak_text(text):
    try:
        engine = pyttsx3.init()
        engine.say(text.replace("*", "").replace("#", ""))
        engine.runAndWait()
    except: pass 

def listen_to_mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner("??? Listening... Speak now!"):
            try:
                r.adjust_for_ambient_noise(source, duration=1)
                return r.recognize_google(r.listen(source, timeout=5))
            except: st.sidebar.warning("?? Audio issue.")
    return ""

if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.header("?? Settings")
    if st.button("??? Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    voice_trigger = st.button("?? Talk to AI")
    speak_output = st.checkbox("?? Read answers out loud", value=False)
    uploaded_file = st.file_uploader("?? Upload a PDF", type=["pdf"])

pdf_context = ""
if uploaded_file is not None:
    try:
        reader = pypdf.PdfReader(uploaded_file)
        pdf_context = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        st.success("? PDF analyzed successfully!")
    except: st.error("? PDF read error.")

with tab1:
    user_prompt = listen_to_mic() if voice_trigger else st.chat_input("Message My Local AI...")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if user_prompt:
        with st.chat_message("user"): st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("assistant"):
            with st.spinner("?? Thinking..."):
                prompt = f"User Question: {user_prompt}\n"
                if pdf_context: prompt = f"Context:\n{pdf_context}\n\n" + prompt
                try:
                    res = OllamaLLM(model="llama3.2").invoke(prompt)
                    st.markdown(res)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    if speak_output: speak_text(res)
                except: st.error("? Is Ollama running in your second window?")
        st.rerun()

with tab2:
    st.header("?? Local Image Generator")
    img_prompt = st.text_input("Enter art prompt:")
    if st.button("?? Generate Visual Artwork") and img_prompt:
        with st.spinner("?? Rendering..."):
            try:
                url = f"https://pollinations.ai{requests.utils.quote(img_prompt)}?width=1024&height=1024&nologo=true"
                st.image(Image.open(BytesIO(requests.get(url).content)), use_container_width=True)
            except Exception as e: st.error(f"? Error: {e}")
