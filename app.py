import smtplib
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

# Fast and reliable Gemini multimodal models
MODELS = ["gemini-3-flash-preview", "gemini-3.5-flash"]

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for modern styling
st.markdown(
    """
    <style>
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
    .email-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.2);
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
# Automated Email Delivery Helper
# ---------------------------------------------------------
def send_study_email(to_email, student_name, summary):
    """Sends study notes directly to the recipient email via secure SMTP."""
    try:
        sender_email = st.secrets["SMTP_EMAIL"].strip().strip("[]")
        sender_password = st.secrets["SMTP_PASSWORD"].strip()
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com").strip()
        smtp_port = int(st.secrets.get("SMTP_PORT", 465))
    except (KeyError, FileNotFoundError):
        return False, "SMTP credentials not found in secrets.toml (SMTP_EMAIL and SMTP_PASSWORD required)."

    clean_to = to_email.strip().strip("[]")

    try:
        msg = MIMEMultipart()
        msg["From"] = f"Snap & Study <{sender_email}>"
        msg["To"] = clean_to
        msg["Subject"] = f"📚 Snap & Study Notes for {student_name}"

        body = (
            f"Hi {student_name}!\n\n"
            f"Here are your study notes from your Snap & Study session:\n\n"
            f"{summary}\n\n"
            f"--------------------------------------------------\n"
            f"Generated with Snap & Study AI Tutor\n"
            f"Keep up the great learning! 🚀\n"
        )
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Primary: Secure SSL on port 465 (most reliable)
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=15) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        else:
            # Fallback: STARTTLS on port 587
            with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
        return True, "Success"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------
# Step 1: Onboarding Screen
# ---------------------------------------------------------
if "onboarded" not in st.session_state:
    st.markdown('<div class="badge">⚡ AI-Powered Learning</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">📚 Snap & Study</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #94A3B8; margin-bottom: 20px;">'
        'Snap a photo of homework, notes, code, or diagrams — get clear, step-by-step explanations in seconds.'
        '</div>',
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
# Step 4: Header & Email Action Bar
# ---------------------------------------------------------
header_col, email_btn_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.markdown('<div class="hero-title">📚 Snap & Study</div>', unsafe_allow_html=True)
    st.caption(f"Studying with **{st.session_state.name}** • Ask questions or snap notes below")

with email_btn_col:
    if st.button("📧 Email Study Notes", use_container_width=True):
        if len(st.session_state.messages) <= 1:
            st.warning("Please ask a question or snap notes in the chat first!")
        else:
            st.session_state.show_email_card = True
            st.rerun()

# Display initial welcome greeting or replay session messages
if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)


# ---------------------------------------------------------
# Step 5: Email Delivery Section
# ---------------------------------------------------------
if st.session_state.get("show_email_card", False) and len(st.session_state.messages) > 1:
    st.markdown('<div class="email-card">', unsafe_allow_html=True)
    st.markdown("#### 📧 Email Your Study Notes")

    if "share_summary" not in st.session_state or not st.session_state.share_summary:
        with st.spinner("Synthesizing clean study notes..."):
            st.session_state.share_summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

    st.info(st.session_state.share_summary)

    recipient_email = st.text_input(
        "Enter your email address:",
        placeholder="e.g. yourname@gmail.com",
        key="target_recipient_email",
    )

    btn_col, close_col = st.columns([3, 1], vertical_alignment="center")
    with btn_col:
        if st.button("Send Notes to My Email 🚀", type="primary", use_container_width=True):
            if not recipient_email.strip() or "@" not in recipient_email:
                st.warning("Please enter a valid email address.")
            else:
                with st.spinner("Sending study notes to your inbox..."):
                    success, info = send_study_email(
                        recipient_email.strip(), st.session_state.name, st.session_state.share_summary
                    )
                    if success:
                        st.success(f"Sent! Study notes delivered to {recipient_email.strip()} 📬")
                    else:
                        st.error(f"Automated send error: {info}")
                        # 1-click fallback opening Gmail to the entered email
                        encoded_body = urllib.parse.quote(st.session_state.share_summary)
                        encoded_sub = urllib.parse.quote(f"📚 Snap & Study Notes for {st.session_state.name}")
                        gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={recipient_email.strip()}&su={encoded_sub}&body={encoded_body}"
                        st.link_button(f"📧 Open in Gmail to send to {recipient_email.strip()}", gmail_url, use_container_width=True)

    with close_col:
        if st.button("✕ Close", use_container_width=True):
            st.session_state.show_email_card = False
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