# 📚 Snap & Study — AI Study Assistant

> An AI-powered study companion that explains homework, diagrams, handwritten notes, and coding problems with step-by-step clarity and 1-click email delivery.

🌐 **Live Deployed App**: [https://snap--study.streamlit.app/](https://snap--study.streamlit.app/)

---

## 🎯 What Snap & Study Does

**Snap & Study** turns questions and photos into interactive, personalized learning experiences:

- **Multimodal Explanations**: Snap a photo using your camera or upload an image (textbook problems, equations, diagrams, handwritten notes, or code) — or simply type your question.
- **Step-by-Step AI Tutoring**: Powered by Google Gemini, it breaks complex problems down into an overview, key concepts, numbered step-by-step solutions, and exam takeaways.
- **Interactive Follow-Up Chat**: Keep chatting to ask clarifying questions without losing context.
- **Automated Email Delivery**: Enter your email address and receive synthesized study notes directly in your inbox with a single click.

---

## 🚀 How to Run It Locally

### 1. Clone the repository
```bash
git clone https://github.com/urvi-parekh1309/snap_and_study.git
cd snap_and_study
```

### 2. Set up virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
Create a `.streamlit/secrets.toml` file in the project root (refer to `.streamlit/secrets.toml.example`):
```toml
# Google Gemini API Key (from https://aistudio.google.com/)
GEMINI_API_KEY = "your-gemini-api-key"

# Gmail SMTP for sending study notes
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-16-character-google-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
```

### 5. Launch the app
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.