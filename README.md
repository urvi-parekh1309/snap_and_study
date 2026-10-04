# 📚 Snap & Study — AI Study Assistant

**Snap & Study** is an AI-powered educational assistant built with **Streamlit** and **Google Gemini Multimodal AI**. It allows students to upload photos of problems, diagrams, handwritten notes, or code — or simply type a question — and receive structured, step-by-step explanations with interactive follow-up chat. When finished, students can email the full study summary directly to their inbox with one click.

---

## ✨ Features

- 🖼️ **Multimodal Image Understanding**: Upload or capture photos of textbook problems, diagrams, handwritten notes, math formulas, or code.
- 📝 **Text Question Answering**: Type or paste conceptual questions, math equations, or code debugging requests.
- 🎓 **Educational Tutor Persona**: Explanations adapt to the subject with *Overview*, *Key Concepts*, *Step-by-Step Solutions*, and *Key Takeaways*.
- 💬 **Interactive Follow-Up Chat**: Persistent multi-turn conversation memory allows students to ask follow-up questions without re-uploading the original image.
- 📧 **Automated Email Delivery**: Send a clean study summary and revision notes straight to your personal email inbox via secure SMTP.
- 🔄 **Session Controls**: Easily clear conversation history and start fresh with a sidebar reset button.

---

## 🏗️ Architecture

```
                         SNAP & STUDY
                              │
                              ▼
                    ┌──────────────────┐
                    │    Streamlit     │
                    │    Frontend      │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
             🖼️ Image               📝 Text
         (Upload / Camera)       (Typed Question)
                  │                     │
                  └──────────┬──────────┘
                             │
                   Input + System Prompt (prompts.py)
                             │
                             ▼
                    ┌──────────────────┐
                    │    Gemini API    │
                    │  (Multimodal AI) │
                    └────────┬─────────┘
                             │
                       Explanation
                             │
                             ▼
                    ┌──────────────────┐
                    │  Chat Interface  │
                    │   (Follow-ups)   │
                    └────────┬─────────┘
                             │
                      Study Summary
                             │
                             ▼
                    ┌──────────────────┐
                    │  Automated Email │
                    │   (SMTP Send)    │
                    └──────────────────┘
```

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **AI Engine**: [Google GenAI SDK](https://pypi.org/project/google-genai/) (`gemini-3-flash-preview` / `gemini-3.5-flash`)
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/)
- **Email Delivery**: Python `smtplib` (SSL Port 465)
- **Deployment**: Streamlit Community Cloud

---

## 📁 Project Structure

```
snap-and-study/
│
├── app.py                      # Main Streamlit UI, chat engine & email delivery
├── prompts.py                  # Structured AI tutor system instructions & templates
├── requirements.txt            # Python dependencies (streamlit, google-genai, pillow)
├── README.md                   # Project documentation & setup instructions
├── .gitignore                  # Excludes secrets and virtual environments
│
└── .streamlit/
    ├── config.toml             # Custom theme styling (Slate & Indigo)
    ├── secrets.toml.example    # Configuration template with placeholder values
    └── secrets.toml            # (Local only — NEVER committed to GitHub)
```

---

## 🚀 Getting Started Locally

### 1. Clone the repository
```bash
git clone https://github.com/urvi-parekh1309/snap_and_study.git
cd snap_and_study
```

### 2. Create and activate a virtual environment
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
Create `.streamlit/secrets.toml` in your project root (see `.streamlit/secrets.toml.example`):
```toml
# 1. Gemini API Key (from Google AI Studio: https://aistudio.google.com/)
GEMINI_API_KEY = "your-gemini-api-key"

# 2. Email Configuration (for automated delivery via Gmail SMTP)
SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-16-character-google-app-password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
```

> **Note on Gmail App Password**:
> 1. Go to your [Google Account Security](https://myaccount.google.com/security).
> 2. Ensure **2-Step Verification** is turned on.
> 3. Search for **"App passwords"**, create one named `Snap and Study`, and copy the 16-letter password into `SMTP_PASSWORD`.

### 5. Run the application
```bash
streamlit run app.py
```

---

## 🌐 Deploying to Streamlit Community Cloud

1. Push your code to a public GitHub repository. Ensure `.streamlit/secrets.toml` is ignored by `.gitignore`.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Click **"New app"** and select:
   - **Repository**: `urvi-parekh1309/snap_and_study`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Under **Advanced settings ➔ Secrets**, paste your secrets:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key"
   SMTP_EMAIL = "your-email@gmail.com"
   SMTP_PASSWORD = "your-app-password"
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = 465
   ```
5. Click **Deploy**!

---

## 🔒 Security & Best Practices

- Real API keys and passwords are kept strictly in `.streamlit/secrets.toml` and never hardcoded in source files.
- `.gitignore` prevents secrets, virtual environments (`venv/`), and Python cache files from entering version control.
- `.streamlit/secrets.toml.example` provides a safe template for collaborators without exposing sensitive credentials.