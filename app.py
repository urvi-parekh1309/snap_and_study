import urllib.parse
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

# Primary model (fast and reliable)
MODEL_NAME = "gemini-3-flash-preview"

# Streamlit Page Setup
st.set_page_config(page_title="Snap & Study", page_icon="📚", layout="centered")

# Ensure API Key exists in secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("Gemini API key not found. Please add it to .streamlit/secrets.toml.")
    st.stop()

# Build the Gemini client once, cached so it survives every Streamlit rerun
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()

# ---------------------------------------------------------
# Step 3: Student Onboarding & Session Initialization
# ---------------------------------------------------------
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Snap a problem. Understand it in seconds. Share your notes.")

    with st.form("onboarding_form"):
        name = st.text_input("Your Name", placeholder="e.g. Alex")
        submitted = st.form_submit_button("Start Studying 🚀", type="primary")

        if submitted:
            if not name.strip():
                st.warning("Please enter your name to get started.")
            else:
                st.session_state.name = name.strip()
                # Create the persistent Gemini chat session with our tutor persona
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()
    st.stop()

# ---------------------------------------------------------
# Step 4: Message Rendering & Chat Engine
# ---------------------------------------------------------
def render_message(message):
    """Draws a single message (text or image) into the chat feed."""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])

def add_message(role, kind, content):
    """Saves a message to session history and renders it immediately."""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])

def ask_gemini(parts):
    """Sends prompt or image parts to the persistent Gemini chat session."""
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as error:
        return f"Sorry, couldn't get an explanation right now: {error}"

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Study Session")
    st.write(f"Student: **{st.session_state.name}**")
    if st.button("🔄 Start New Topic", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.divider()
    st.markdown("### 💡 Study Tips")
    st.markdown("- **Math/Physics:** Snap clear photos of formulas.")
    st.markdown("- **Code:** Ask for line-by-line breakdown.")
    st.markdown("- **Diagrams:** Ask what each component does.")

# Main app title
st.title("📚 Snap & Study")

# Welcome message on first load, or replay chat history on rerun
if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)

# ---------------------------------------------------------
# Step 5: Multimodal Input (Camera & Chat Input)
# ---------------------------------------------------------

# Optional camera capture for students snapping physical notebook pages
with st.expander("📸 Or snap a photo with your webcam"):
    camera_photo = st.camera_input("Capture homework or problem")
    if camera_photo and st.button("Explain camera photo", type="primary"):
        photo_bytes = camera_photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts = [
            types.Part.from_bytes(data=photo_bytes, mime_type=camera_photo.type),
            "Please explain the problem, diagram, notes, or code shown in this photo step-by-step."
        ]
        with st.spinner("Analyzing your photo..."):
            answer = ask_gemini(parts)
            add_message("assistant", "text", answer)

# Unified chat input (Text + File Attachment)
user_input = st.chat_input(
    "Ask a study question, or attach a photo of notes / homework",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    # 1. If an image was attached, display and package it
    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    # 2. If text was typed, record and package it
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        # Default prompt if student attached a bare photo without typing
        parts.append("Please explain the problem, diagram, notes, or code shown in this image step-by-step.")

    # 3. Call Gemini and render the structured explanation
    with st.spinner("Analyzing and preparing explanation..."):
        answer = ask_gemini(parts)
        add_message("assistant", "text", answer)

# ---------------------------------------------------------
# Step 6: Study Notes Sharing Toolbar
# ---------------------------------------------------------
if len(st.session_state.messages) > 1:
    st.divider()
    st.subheader("📤 Share Your Study Notes")

    # Button to generate a clean, bulleted study summary from the conversation
    if st.button("📝 Generate Shareable Study Summary", type="secondary", use_container_width=True):
        with st.spinner("Generating clean study summary..."):
            summary_text = ask_gemini([SUMMARY_REQUEST_PROMPT])
            st.session_state.share_summary = summary_text

    # If a summary has been generated, preview it and display sharing options
    if "share_summary" in st.session_state and st.session_state.share_summary:
        st.markdown("**Preview of your study note:**")
        st.info(st.session_state.share_summary)

        # URL-encode the study notes safely for messaging protocols
        encoded_text = urllib.parse.quote(st.session_state.share_summary)
        encoded_subject = urllib.parse.quote(f"Snap & Study Notes for {st.session_state.name}")

        wa_url = f"https://api.whatsapp.com/send?text={encoded_text}"
        tg_url = f"https://t.me/share/url?url=&text={encoded_text}"
        mail_url = f"mailto:?subject={encoded_subject}&body={encoded_text}"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.link_button("📱 WhatsApp", wa_url, use_container_width=True)
        with col2:
            st.link_button("✈️ Telegram", tg_url, use_container_width=True)
        with col3:
            st.link_button("📧 Email", mail_url, use_container_width=True)

        st.caption("Clicking any button opens the app with your notes pre-filled and ready to send.")