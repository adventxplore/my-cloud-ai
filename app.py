import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS
import pypdf
import requests
from io import BytesIO
from PIL import Image
from gtts import gTTS  # Web-safe voice streaming player card

st.set_page_config(page_title="Global AI Workspace", page_icon="🤖", layout="centered")
st.title("🤖 My Global AI Workspace")

# Premium Multi-Modal Navigation Tabs
tab1, tab2 = st.tabs(["💬 Cloud Chat Assistant", "🎨 AI Image Generator"])

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Missing Gemini API Key! Configure it in your Streamlit Secrets.")

def run_web_search(query):
    try:
        with DDGS() as ddgs:
            results = [r["body"] for r in ddgs.text(query, max_results=3)]
            return "\n".join(results) if results else "No data found."
    except:
        return "Web search rate limit reached."

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- CONTROL PANEL SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.subheader("🌐 Web Access")
    web_search_active = st.checkbox("🔍 Enable Live Web Search", value=False)
        
    st.markdown("---")
    st.subheader("🔊 Voice Engine")
    speak_output = st.checkbox("🔊 Read answers out loud", value=False)
        
    st.markdown("---")
    st.subheader("📁 Document Analysis")
    uploaded_file = st.file_uploader("Upload a PDF to analyze", type=["pdf"])
    
    pdf_context = ""
    if uploaded_file is not None:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            extracted_text = [page.extract_text() for page in reader.pages if page.extract_text()]
            pdf_context = "\n".join(extracted_text)
            st.success("✅ PDF analyzed successfully!")
        except Exception as e:
            st.error(f"❌ PDF read error: {e}")

# --- TAB 1: CONVERSATIONAL ASSISTANT ---
with tab1:
    st.caption("🚀 Universal Cloud AI Assistant Interface")
    
    # Render Past Chat Threads
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_prompt := st.chat_input("Message Cloud AI..."):
        with st.chat_message("user"):
            st.markdown(user_prompt)
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("assistant"):
            with st.spinner("🧠 Synthesizing cloud data..."):
                try:
                    final_prompt = f"User Question: {user_prompt}\n"
                    if pdf_context:
                        final_prompt = f"Document Context:\n{pdf_context}\n\n" + final_prompt
                    if web_search_active:
                        final_prompt = f"Live Web Data:\n{run_web_search(user_prompt)}\n\n" + final_prompt

                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(final_prompt)
                    answer_text = response.text
                    
                    st.markdown(answer_text)
                    st.session_state.messages.append({"role": "assistant", "content": answer_text})
                    
                    # Web-Safe Voice Synthesis Out loud player streaming module
                    if speak_output:
                        tts = gTTS(text=answer_text, lang='en')
                        sound_fp = BytesIO()
                        tts.write_to_fp(sound_fp)
                        st.audio(sound_fp, format="audio/mp3", autoplay=True)
                except Exception as e:
                    st.error(f"❌ Cloud Connection Error: {e}")
        st.rerun()

# --- TAB 2: IMAGE GENERATOR CANVAS ---
with tab2:
    st.header("🎨 Text-to-Image Canvas")
    img_prompt = st.text_input("Enter art prompt here:")
    if st.button("🚀 Generate Visual Artwork") and img_prompt:
        with st.spinner("🔮 Rendering visual art vectors..."):
            try:
                encoded_prompt = requests.utils.quote(img_prompt)
                url = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&nologo=true"
                response = requests.get(url, timeout=20)
                
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    st.image(img, use_container_width=True)
                    
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button(label="💾 Download PNG", data=buf.getvalue(), file_name="ai_art.png", mime="image/png")
                else:
                    st.error("The drawing server node is busy. Try again!")
            except Exception as e:
                st.error(f"❌ Image generation error: {e}")
