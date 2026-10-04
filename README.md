# 📚 Snap & Study — AI Study Assistant

**Snap & Study** is an AI-powered educational tutor built with **Streamlit** and **Google Gemini Multimodal AI**. It allows students to upload photos of homework, math problems, handwritten notes, diagrams, or code — or simply type a question — and receive clear, step-by-step explanations with interactive follow-up chat.

---

## ✨ Features

- 🖼️ **Multimodal Image Understanding**: Snap or upload diagrams, textbook pages, math formulas, or code.
- 📝 **Text Question Answering**: Type or paste conceptual questions, definitions, or code questions.
- 🎓 **Educational Tutor Persona**: Explanations are structured with *Overview*, *Key Concepts*, *Step-by-Step Solutions*, and *Key Takeaways*.
- 💬 **Interactive Follow-Up Chat**: Ask follow-up questions without re-uploading the original image or re-typing the problem.
- 📤 **1-Click Sharing**: Share explanations directly to **WhatsApp**, **Telegram**, or **Email**.
- 🔄 **Session Controls**: Easily clear questions and start fresh with sidebar controls.

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
                   Shareable Summary
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
           WhatsApp      Telegram       Email
```

---

## 🛠️ Tech Stack

- **Frontend & App Logic**: [Streamlit](https://streamlit.io/)
- **AI Intelligence**: [Google GenAI SDK](https://pypi.org/project/google-genai/) (`gemini-3-flash-preview` / `gemini-3.5-flash`)
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/)
- **Deployment**: Streamlit Community Cloud

---

## 📁 Project Structure

```
snap-and-study/
│
├── app.py                      # Main Streamlit UI, chat flow & sharing logic
├── prompts.py                  # Structured AI tutor system instructions
├── requirements.txt            # Python dependencies (streamlit, google-genai, pillow)
├── README.md                   # Project documentation
├── .gitignore                  # Excludes secrets and virtual envs
│
└── .streamlit/
    ├── secrets.toml.example    # Template showing expected secrets format
    └── secrets.toml            # (Local only - NEVER committed to GitHub)
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

### 4. Configure API Keys
Create `.streamlit/secrets.toml` in the project root:
```toml
GEMINI_API_KEY = "your-actual-gemini-api-key"
```
*(You can obtain an API key from [Google AI Studio](https://aistudio.google.com/)).*

### 5. Run the application
```bash
streamlit run app.py
```

---

## 🌐 Deploying to Streamlit Community Cloud

1. Push your clean code to GitHub (ensure `.streamlit/secrets.toml` is ignored by `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New app"** and select your repository: `urvi-parekh1309/snap_and_study`.
4. Set main file path to: `app.py`.
5. Under **Advanced settings** -> **Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key"
   ```
6. Click **Deploy**!

---

## 🔒 Security
- API keys are never hardcoded and are kept strictly in `.streamlit/secrets.toml`.
- `.gitignore` ensures credentials and cache folders are never tracked or pushed to GitHub.