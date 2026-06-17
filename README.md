# Lumina AI — Gemini Chatbot

A production-quality Streamlit frontend for a multi-turn AI chatbot powered by
Google Gemini 2.5 Flash.

---

## Folder structure

```
gemini_chatbot/
├── app.py                  ← Streamlit UI entry point  (run this)
├── requirements.txt        ← Python dependencies
├── .env.example            ← Copy to .env and add your key
├── .env                    ← Your real API key (git-ignored)
├── backend/
│   ├── __init__.py
│   └── chatbot_engine.py   ← Pure backend: client, session, response logic
└── assets/                 ← (optional) logos, images
```

---

## Quick start

```bash
# 1. Clone / download the folder
cd gemini_chatbot

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
cp .env.example .env
# Edit .env → GEMINI_API_KEY=your_key_here

# 5. Run
streamlit run app.py
```

The app opens at http://localhost:8501.

---

## Where to integrate backend changes

All model / API logic lives in **`backend/chatbot_engine.py`**:

| What you want to change         | Where                          |
|---------------------------------|--------------------------------|
| Switch Gemini model             | `MODEL_ID` constant            |
| Add system instructions         | `create_chat_session()`        |
| Change generation config        | `create_chat_session()`        |
| Handle streaming responses      | `_async_get_response()`        |
| Add tool / function calling     | `create_chat_session()`        |

`app.py` imports only three things from the backend:
`create_client`, `create_chat_session`, `get_response`.
Keep it that way — UI and logic stay cleanly separated.

---

## Features

- Modern dark UI with custom CSS design system
- Multi-turn conversation with full context retention
- Chat history with timestamps
- Conversation statistics (messages, words)
- Export chat as `.txt`
- Clear chat with one click
- Loading / typing indicator
- Friendly error messages for missing API key
- Welcome screen for new sessions
- Professional sidebar with model info
- Session timer
