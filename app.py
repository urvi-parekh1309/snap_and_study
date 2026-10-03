import json
import urllib.parse
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

# Fast and reliable Gemini multimodal models
MODELS = ["gemini-3-flash-preview", "gemini-3.5-flash"]

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for modern, aesthetic EdTech styling
st.markdown(
    """
    <style>
    /* Card and surface styling */
    .stChatFloatingInputContainer {
        bottom: 20px;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        border-radius: 9999px;
        background: rgba(99, 102, 241, 0.15);
        color: #818CF8;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 8px;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    .share-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 16px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Safe API key loading from Streamlit secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error("🔑 Gemini API key not found. Please configure it in .streamlit/secrets.toml.")
    st.stop()

# Build the Gemini client once, cached so it survives every Streamlit rerun
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()


# ---------------------------------------------------------
# Step 1: Onboarding Screen
# ---------------------------------------------------------
if "onboarded" not in st.session_state:
    st.markdown('<div class="badge">⚡ AI-Powered Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">📚 Snap & Study</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Snap a photo of homework, notes, code, or diagrams — get clear, step-by-step explanations in seconds.</div>',
        unsafe_allow_html=True,
    )

    with st.form("onboarding_form"):
        st.markdown("### Welcome! Let's get you set up")
        name = st.text_input("Your Name", placeholder="e.g. Alex")
        study_focus = st.selectbox(
            "What are you studying today?",
            ["General Studies", "Mathematics / Calculus", "Science & Physics", "Computer Science / Coding", "Exam Prep / Revision"],
        )
        submitted = st.form_submit_button("Start Studying 🚀", type="primary", use_container_width=True)

        if submitted:
            if not name.strip():
                st.warning("Please enter your name to start.")
            else:
                st.session_state.name = name.strip()
                st.session_state.study_focus = study_focus
                # Create persistent multi-turn chat session with Gemini
                st.session_state.chat = gemini_client.chats.create(
                    model=MODELS[0],
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()
    st.stop()


# ---------------------------------------------------------
# Step 2: Chat & Message Helper Functions
# ---------------------------------------------------------
def render_message(message):
    """Draws a single message (text or image) with appropriate formatting."""
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], caption="Attached Material", use_container_width=True)

def add_message(role, kind, content):
    """Persists a message in session history and draws it immediately."""
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])

def ask_gemini(parts):
    """Calls Gemini with automatic model fallback in case of high traffic."""
    for model_name in MODELS:
        try:
            response = st.session_state.chat.send_message(parts)
            return response.text
        except Exception:
            continue
    return "Sorry, Gemini servers are currently busy. Please try again in a few moments."


# ---------------------------------------------------------
# Step 3: Sidebar Controls & Study Tools
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="badge">Session Active</div>', unsafe_allow_html=True)
    st.markdown(f"### 👤 {st.session_state.name}")
    st.caption(f"Topic: {st.session_state.get('study_focus', 'General')}")

    if st.button("🔄 Start New Topic", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown("### 💡 Quick Study Tips")
    st.markdown("- **📐 Math:** Snap clear, well-lit formulas.")
    st.markdown("- **💻 Code:** Ask for line-by-line debugging.")
    st.markdown("- **📊 Diagrams:** Ask what each component does.")
    st.markdown("- **📝 Notes:** Ask for exam summaries & mnemonics.")


# ---------------------------------------------------------
# Step 4: Header & Live Sharing Bar
# ---------------------------------------------------------
header_col, share_btn_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.markdown('<div class="hero-title">📚 Snap & Study</div>', unsafe_allow_html=True)
    st.caption(f"Studying with **{st.session_state.name}** • Ask questions or snap notes below")

# Sharing is enabled once there is an actual conversation
has_conversation = len(st.session_state.messages) > 1

with share_btn_col:
    if st.button("📤 Share Notes", disabled=not has_conversation, use_container_width=True):
        st.session_state.show_share_modal = True

# Display initial welcome greeting or replay session messages
if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)


# ---------------------------------------------------------
# Step 5: Sharing Modal / Card
# ---------------------------------------------------------
if st.session_state.get("show_share_modal", False) and has_conversation:
    st.markdown('<div class="share-card">', unsafe_allow_html=True)
    st.markdown("#### 📤 Export & Share Study Summary")

    if "share_summary" not in st.session_state or not st.session_state.share_summary:
        with st.spinner("Synthesizing clean study notes..."):
            st.session_state.share_summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

    st.info(st.session_state.share_summary)

    encoded_text = urllib.parse.quote(st.session_state.share_summary)
    encoded_subject = urllib.parse.quote(f"Study Notes for {st.session_state.name}")

    wa_url = f"https://api.whatsapp.com/send?text={encoded_text}"
    tg_url = f"https://t.me/share/url?url=&text={encoded_text}"
    mail_url = f"mailto:?subject={encoded_subject}&body={encoded_text}"

    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
    with c1:
        st.link_button("📱 WhatsApp", wa_url, use_container_width=True)
    with c2:
        st.link_button("✈️ Telegram", tg_url, use_container_width=True)
    with c3:
        st.link_button("📧 Email", mail_url, use_container_width=True)
    with c4:
        if st.button("✕ Close", use_container_width=True):
            st.session_state.show_share_modal = False
            st.session_state.share_summary = ""
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# Step 6: Multimodal Inputs (Camera Expander & Chat Bar)
# ---------------------------------------------------------
with st.expander("📸 Or snap a photo using your webcam"):
    camera_photo = st.camera_input("Capture homework or problem")
    if camera_photo and st.button("Explain camera photo", type="primary", use_container_width=True):
        photo_bytes = camera_photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts = [
            types.Part.from_bytes(data=photo_bytes, mime_type=camera_photo.type),
            "Please explain the problem, diagram, notes, or code shown in this photo step-by-step.",
        ]
        with st.spinner("Analyzing photo with Gemini..."):
            answer = ask_gemini(parts)
            add_message("assistant", "text", answer)

# Unified chat input (Text + File Upload)
user_input = st.chat_input(
    "Ask a question, or attach a photo of your notes / homework...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append("Please explain the problem, diagram, notes, or code shown in this image step-by-step.")

    with st.spinner("Analyzing and preparing your explanation..."):
        answer = ask_gemini(parts)
        add_message("assistant", "text", answer)