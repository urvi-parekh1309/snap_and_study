import streamlit as st
from google import genai

MODEL = "gemini-flash-latest"

st.set_page_config(page_title="Snap & Study", page_icon="📚")
st.title("📚 Snap & Study")

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except (KeyError, FileNotFoundError):
    st.error("Gemini API key not found. Add it to .streamlit/secrets.toml.")
    st.stop()

if not st.session_state.get("started"):
    st.subheader("Snap a question. Understand it in seconds.")
    st.write(
        "Upload a photo of a problem, diagram, notes, or code, or just type "
        "your question. Get a simple explanation, then ask follow-ups."
    )
    if st.button("Get Started", type="primary"):
        st.session_state.started = True
        st.rerun()
    st.stop()

image_tab, text_tab = st.tabs(["🖼️ Image", "📝 Text"])

with image_tab:
    source = st.radio("Source", ["Upload", "Camera"], horizontal=True)
    if source == "Upload":
        image = st.file_uploader("Upload a photo", type=["png", "jpg", "jpeg", "webp"])
    else:
        image = st.camera_input("Take a photo")
    note = st.text_input("Anything specific you want to know? (optional)")

    if st.button("Explain image", type="primary"):
        if image is None:
            st.warning("Please upload or capture an image first.")
        else:
            st.image(image, caption="Image received")

with text_tab:
    question = st.text_area("Type or paste your question", height=150)

    if st.button("Explain question", type="primary"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = client.models.generate_content(
                        model=MODEL, contents=question.strip()
                    )
                except Exception as e:
                    print(e)
                    st.error("Couldn't get an explanation right now. Please try again in a moment.")
                else:
                    if response.text:
                        st.markdown(response.text)
                    else:
                        st.warning("Gemini returned an empty answer. Try rephrasing your question.")