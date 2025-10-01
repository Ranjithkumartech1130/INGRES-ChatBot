import streamlit as st
import google.generativeai as genai
import os
import speech_recognition as sr

# --- Helper Functions ---
def get_or_init_session_state(key, default_value):
    """Gets a value from session state or initializes it."""
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]
# --- Gemini API Configuration ---
try:
    # It's highly recommended to set your API key as a Streamlit secret
    # for security and ease of deployment.
    # In your Streamlit Cloud dashboard, add a secret with the key "GEMINI_API_KEY".
    # This correctly fetches the key from an environment variable or a Streamlit secret.
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY"))
except (KeyError, FileNotFoundError):
    st.error(
        "🚨 Gemini API key not found. "
        "Please set the `GEMINI_API_KEY` environment variable or add it to your Streamlit secrets.",
        icon="🚨"
    )
    st.stop()

# --- Model Selection and Initialization ---
# A system instruction to guide the chatbot's behavior
SYSTEM_PROMPT = (
    "You are 'INGRES Assistant', a helpful and friendly virtual assistant specialized in the INGRES relational database management system (RDBMS). "
    "Your role is to provide clear, accurate, and concise answers to questions about INGRES, its features, SQL queries related to it, general database concepts and excel formulas. You are developed by Ranjith Kumar."
    "If a question is outside of this scope, politely state that you specialize in INGRES and cannot answer."
)

# Use the latest and most capable flash model
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)

# --- Core Functions ---
def handle_prompt(prompt: str):
    """Handles user prompt, displays it, gets a response, and updates the chat."""
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                bot_reply = response.text
                st.markdown(bot_reply)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                bot_reply = "Sorry, I ran into a problem. Please try again."
                st.markdown(bot_reply)

    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

def get_voice_input():
    """Captures and transcribes voice input."""
    recognizer = sr.Recognizer()
    st.info("Preparing to listen...", icon="⏳")
    with sr.Microphone() as source:
        st.info("Listening... Speak now!", icon="🎤")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            st.info("Transcribing...", icon="✍️")
            text = recognizer.recognize_google(audio)
            st.success(f"You said: \"{text}\"")
            return text
        except sr.WaitTimeoutError:
            st.warning("No speech detected. Please try again.")
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio. Please speak clearly.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
    return None

# --- Streamlit App UI ---
st.set_page_config(page_title="INGRES Virtual Assistant", page_icon="🤖")

st.title("🤖 INGRES Virtual Assistant")
st.caption(f"Powered by Google Gemini {MODEL_NAME.replace('2.5', '1.5')}")

# --- Sidebar for settings and actions ---
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()
    st.markdown("---")
    if st.button("🎤 Speak to Assistant", use_container_width=True):
        voice_prompt = get_voice_input()
        if voice_prompt:
            handle_prompt(voice_prompt)
    st.markdown("---")
    st.markdown(
        "**About:** This chatbot is powered by Google's Gemini model and is "
        "specialized in answering questions about the INGRES database system."
    )

# Initialize chat session in Streamlit's session state
get_or_init_session_state("messages", [
    {"role": "assistant", "content": "Hello! I am your INGRES virtual assistant. How can I help you?"}
])
get_or_init_session_state("chat_session", model.start_chat(history=[]))

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Handle text input at the bottom of the main page
if prompt := st.chat_input("Your message..."):
    handle_prompt(prompt)
