import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
import io
import speech_recognition as sr

# --- Gemini API Configuration ---
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    st.secrets.load_if_toml_exists()
    if not api_key and st.secrets.get("GEMINI_API_KEY"):
        api_key = st.secrets["GEMINI_API_KEY"]
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found.")
    genai.configure(api_key=api_key)
except (ValueError, TypeError) as e:
    st.error(
        "🚨 Gemini API key not found. "
        "Please set the `GEMINI_API_KEY` environment variable or add it to your Streamlit secrets.",
        icon="🚨"
    )
    st.stop()

# --- Model Setup ---
SYSTEM_PROMPT = (
    "You are an AI-powered Personalized Learning Path Generator. "
    "Your job is to create tailored learning paths for users based on their goals, current skills, and preferences. "
    "Ask clarifying questions if needed, and provide step-by-step, actionable plans with recommended resources, timelines, and checkpoints. "
    "Be friendly, supportive, and always encourage the user. "
    "If a user uploads a resume or skill list, analyze it and use it to personalize the learning path. "
)
MODEL_NAME = "gemini-2.5-flash"
model = genai.GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_PROMPT)

# --- UI Setup ---
st.set_page_config(page_title="AI-Powered Personalized Learning Path Generator", page_icon="🎓", layout="wide")
st.markdown("""
    <style>
    .main {background-color: #f5f7fa;}
    .stButton>button {background-color: #4F8BF9; color: white; font-weight: bold;}
    .stTextInput, .stTextArea {background-color: #eaf0fb;}
    /* Sidebar (left) background: white to purple gradient */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #ffffff 0%, #a259ec 100%) !important;
    }
    /* Right column background: light blue */
    div[data-testid="column"]:nth-child(2) {
        background-color: #e3f2fd !important;
        border-radius: 12px;
        padding: 12px;
    }
    </style>
    """, unsafe_allow_html=True)


st.title("🎓 AI-Powered Personalized Learning Path Generator")
st.caption("Get a custom learning plan for your goals, powered by Gemini AI.")

# --- Onboarding for First-Time Users ---
with st.expander("ℹ️ How to use this platform (First-Time User Guide)", expanded=True):
    st.markdown("""
    **Welcome!** This platform helps you create a personalized learning path for any goal.
    
    **Steps to get started:**
    1. Enter your learning goal (e.g., Become a Data Scientist).
    2. List your current skills or experience (optional).
    3. Add any preferences (learning style, time, resources).
    4. Upload your resume or skill list (optional).
    5. Click **Generate My Learning Path** to get a step-by-step plan.
    6. Interact with the built-in AI assistant for advice or questions.
    
    **Tips:**
    - The more details you provide, the better your plan.
    - Use the open-source links for free learning resources.
    - You can revise your inputs and generate a new plan anytime.
    """)

with st.sidebar:
    st.header("About")
    st.markdown("""
    This tool generates a personalized learning path for any topic or career goal. 
    Just enter your goal, current skills, and preferences. Optionally, upload your resume or skill list for deeper personalization.
    """)
    st.markdown("---")
    st.markdown("Developed by Ranjith Kumar | Powered by Gemini AI")


# --- Interactive Input Section ---
st.markdown("## Step 1: Tell us about your learning goal")
goal = st.text_input("🎯 What is your learning goal? (e.g., Become a Data Scientist)", key="goal")

if goal:
    st.markdown("## Step 2: Share your current skills and experience")
    skills = st.text_area("🛠️ List your current skills or experience (optional)", key="skills")
    st.markdown("## Step 3: Add your preferences")
    preferences = st.text_area("⚙️ Any preferences? (e.g., learning style, time commitment, resources)", key="preferences")
    st.markdown("## Step 4: Upload your resume or skill list (optional)")
    uploaded_file = st.file_uploader("📄 Upload your resume or skill list", type=["txt", "pdf", "docx"], key="resume")
    st.image("https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=800&q=80", caption="Personalized Learning", use_column_width=True)
else:
    skills = ""
    preferences = ""
    uploaded_file = None


# --- Helper: Get file content ---
def get_file_content(file):
    if file is None:
        return ""
    try:
        if file.type == "text/plain":
            return file.getvalue().decode("utf-8")
        else:
            return "[Uploaded file type not supported for preview, but will be used for personalization.]"
    except Exception:
        return "[Error reading file.]"

# --- Open Source Resource Links ---
OPEN_SOURCE_LINKS = [
    {"name": "Coursera", "url": "https://www.coursera.org/"},
    {"name": "edX", "url": "https://www.edx.org/"},
    {"name": "Khan Academy", "url": "https://www.khanacademy.org/"},
    {"name": "freeCodeCamp", "url": "https://www.freecodecamp.org/"},
    {"name": "MIT OpenCourseWare", "url": "https://ocw.mit.edu/"},
    {"name": "Codecademy", "url": "https://www.codecademy.com/"},
    {"name": "Harvard Online", "url": "https://online-learning.harvard.edu/"},
    {"name": "Stanford Online", "url": "https://online.stanford.edu/"},
]

with st.expander("💡 Explore Open Source Learning Resources"):
    for resource in OPEN_SOURCE_LINKS:
        st.markdown(f"- [{resource['name']}]({resource['url']})")

# --- Interactive Chat Section ---
st.markdown("---")
st.subheader("📝 Your Personalized Learning Path")

if 'learning_path' not in st.session_state:
    st.session_state['learning_path'] = ""

def generate_learning_path(goal, skills, preferences, resume):
    # Validate input
    if not goal or goal.strip() == "":
        return "Please enter a learning goal to get started."
    prompt = (
        f"You are an AI learning path generator.\n"
        f"User Goal: {goal}\n"
        f"User Skills: {skills}\n"
        f"User Preferences: {preferences}\n"
        f"Resume/Skill List: {resume}\n"
        "Generate a clear, concise, and actionable learning path for the user. "
        "Break the path into steps, recommend open-source resources, and provide checkpoints. "
        "Format the output as a numbered list with explanations and links. "
        "Always encourage the user and suggest how to track progress."
    )
    try:
        response = model.generate_content(prompt)
        # Check for valid response
        if hasattr(response, "text") and response.text and response.text.strip():
            return response.text
        else:
            return "Sorry, the AI could not generate a learning path. Please try again with more details or check your API quota."
    except Exception as e:
        return f"Error generating learning path: {e}"


# --- Interactive Generation and Feedback ---
if goal:
    if st.button("🚀 Generate My Learning Path", use_container_width=True):
        resume_content = get_file_content(uploaded_file)
        learning_path = generate_learning_path(goal, skills, preferences, resume_content)
        st.session_state['learning_path'] = learning_path

if st.session_state.get('learning_path'):
    st.markdown(st.session_state['learning_path'])
    st.success("Your personalized learning path is ready! Use the above steps and resources to start your journey.")
    st.info("Tip: Save this plan and revisit the open-source links for more resources.")

    st.markdown("---")
    st.markdown("### Was this learning path helpful?")
    feedback = st.radio("Rate your plan:", ["👍 Yes, it's great!", "👌 It's okay, but could be better", "👎 Not helpful"], key="feedback")

    if feedback == "👍 Yes, it's great!":
        st.balloons()
        st.success("Awesome! Start your journey and come back anytime to update your plan.")
    elif feedback == "👌 It's okay, but could be better":
        st.warning("You can revise your goal, skills, or preferences and generate a new plan.")
    elif feedback == "👎 Not helpful":
        st.error("Sorry about that! Please provide more details or change your inputs for a better plan.")

    st.markdown("---")
    st.subheader("🤖 AI Assistant: Ask Anything About Your Learning Path")
    if 'assistant_history' not in st.session_state:
        st.session_state['assistant_history'] = []

    user_message = st.text_input("Type your question or message to the AI assistant", key="assistant_input")

    st.markdown("**Or use voice input:**")
    audio_file = st.file_uploader("Upload a voice message (WAV format, <30s)", type=["wav"], key="voice_input")
    voice_text = None
    if audio_file is not None:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        try:
            voice_text = recognizer.recognize_google(audio)
            st.success(f"Transcribed voice: {voice_text}")
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")

    # Use either text or voice input
    final_message = user_message if user_message else (voice_text if voice_text else None)
    if st.button("Ask AI", key="ask_ai_btn") and final_message:
        # Compose context for the assistant
        context = f"User's learning path: {st.session_state['learning_path']}\nUser's question: {final_message}"
        try:
            response = model.generate_content(context)
            if hasattr(response, "text") and response.text and response.text.strip():
                st.session_state['assistant_history'].append((final_message, response.text))
            else:
                st.session_state['assistant_history'].append((final_message, "Sorry, the AI could not answer. Please try again or rephrase your question."))
        except Exception as e:
            st.session_state['assistant_history'].append((final_message, f"Error: {e}"))

    if st.session_state['assistant_history']:
        st.markdown("#### Conversation History")
        for q, a in st.session_state['assistant_history']:
            st.markdown(f"**You:** {q}")
            st.markdown(f"**AI Assistant:** {a}")

st.markdown("---")
st.markdown("**Tip:** The more details you provide, the better your learning path! You can always update your goal, skills, or preferences and generate a new plan.")
