import streamlit as st 
import google.generativeai as genai 
from duckduckgo_search import DDGS 
import pypdf 
import requests 
from io import BytesIO 
from PIL import Image 
st.set_page_config(page_title="Global AI Workspace", layout="centered") 
st.title("Cloud AI Workspace") 
if "GEMINI_API_KEY" in st.secrets: 
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) 
else: 
    st.error("Missing API Key! Please configure it in your Streamlit Secrets panel.") 
tab1, tab2 = st.tabs(["Cloud Chat Assistant", "AI Image Generator"]) 
def run_web_search(query): 
    try: 
        with DDGS() as ddgs: 
            results = [r["body"] for r in ddgs.text(query, max_results=3)] 
            return "\n".join(results) if results else "No data found." 
    except: return "Search limit reached." 
if "messages" not in st.session_state: st.session_state.messages = [] 
with st.sidebar: 
    st.header("Settings") 
    if st.button("Clear Chat"): 
        st.session_state.messages = [] 
        st.rerun() 
    web_search_active = st.checkbox("Enable Live Web Search", value=False) 
    uploaded_file = st.file_uploader("Upload a PDF to analyze", type=["pdf"]) 
pdf_context = "" 
if uploaded_file is not None: 
    try: 
        reader = pypdf.PdfReader(uploaded_file) 
        pdf_context = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()]) 
        st.success("PDF analyzed successfully!") 
    except Exception as e: st.error(f"PDF error: {e}") 
with tab1: 
    for message in st.session_state.messages: 
        with st.chat_message(message["role"]): st.markdown(message["content"]) 
    if user_prompt := st.chat_input("Message Cloud AI..."): 
        with st.chat_message("user"): st.markdown(user_prompt) 
        st.session_state.messages.append({"role": "user", "content": user_prompt}) 
        with st.chat_message("assistant"): 
            with st.spinner("Synthesizing cloud data..."): 
                try: 
                    final_prompt = f"User Question: {user_prompt}\n" 
                    if pdf_context: final_prompt = f"PDF Context:\n{pdf_context}\n\n" + final_prompt 
                    if web_search_active: final_prompt = f"Web Context:\n{run_web_search(user_prompt)}\n\n" + final_prompt 
                    model = genai.GenerativeModel('gemini-1.5-flash') 
                    response = model.generate_content(final_prompt) 
                    st.markdown(response.text) 
                    st.session_state.messages.append({"role": "assistant", "content": response.text}) 
                except Exception as e: st.error(f"Cloud Connection Error: {e}") 
        st.rerun() 
with tab2: 
    st.header("Cloud Image Generator") 
    img_prompt = st.text_input("Enter creative prompt:") 
    if st.button("Compile Web Image") and img_prompt: 
        with st.spinner("Rendering visual vectors..."): 
            try: 
                url = f"https://pollinations.ai{requests.utils.quote(img_prompt)}?width=1024&height=1024&nologo=true" 
                img = Image.open(BytesIO(requests.get(url).content)) 
                st.image(img, use_container_width=True) 
            except Exception as e: st.error(f"Image compilation error: {e}") 
