"""
app.py
------
Production-quality Streamlit frontend for the Gemini chatbot.

Run with:
    streamlit run app.py
"""

import datetime
import io
import sys
import os

import streamlit as st

# ── Path setup so the backend package is importable ─────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from chatbot_engine import (
    create_client,
    create_chat_session,
    get_response,
    MODEL_DISPLAY,
    MODEL_PROVIDER,
    MODEL_DESCRIPTION,
)

# ════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  (must be the first Streamlit call)
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Lumina AI — Powered by Gemini",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
STYLE = """
<style>
/* ── Google Font import ─────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

/* ── Design tokens ──────────────────────────────────────────────────── */
:root {
  --bg:          #0d0f14;
  --surface:     #13161d;
  --surface-2:   #1a1e28;
  --border:      #272b38;
  --accent:      #7c6af7;
  --accent-soft: #a899ff;
  --accent-glow: rgba(124, 106, 247, 0.18);
  --user-bg:     #1e2235;
  --bot-bg:      #161923;
  --text-hi:     #eef0f7;
  --text-mid:    #9298aa;
  --text-lo:     #555b6e;
  --success:     #3ecf8e;
  --error:       #f7706a;
  --radius:      14px;
  --radius-sm:   8px;
  --shadow:      0 4px 24px rgba(0,0,0,.45);
}

/* ── Base ────────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif;
  color: var(--text-hi);
}

[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Scrollbar ───────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

/* ── Header banner ───────────────────────────────────────────────────── */
.lm-header {
  background: linear-gradient(135deg, #10131b 0%, #151829 60%, #1a1330 100%);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 2rem 2.4rem 1.6rem;
  margin-bottom: 1.4rem;
  position: relative;
  overflow: hidden;
}
.lm-header::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 260px; height: 260px;
  background: radial-gradient(circle, var(--accent-glow) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.lm-header-eyebrow {
  font-size: .72rem;
  font-weight: 600;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--accent-soft);
  margin-bottom: .5rem;
}
.lm-header-title {
  font-family: 'Sora', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-hi);
  letter-spacing: -.02em;
  margin: 0 0 .4rem;
  line-height: 1.15;
}
.lm-header-title span { color: var(--accent-soft); }
.lm-header-sub {
  font-size: .88rem;
  color: var(--text-mid);
  max-width: 520px;
  line-height: 1.55;
}
.lm-badge {
  display: inline-block;
  background: var(--accent-glow);
  border: 1px solid var(--accent);
  color: var(--accent-soft);
  font-size: .7rem;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  padding: .25rem .65rem;
  border-radius: 99px;
  margin-top: 1rem;
}

/* ── Welcome screen ──────────────────────────────────────────────────── */
.lm-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  gap: 1rem;
}
.lm-welcome-icon {
  font-size: 3.2rem;
  line-height: 1;
  filter: drop-shadow(0 0 18px var(--accent));
}
.lm-welcome-title {
  font-family: 'Sora', sans-serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--text-hi);
  margin: 0;
}
.lm-welcome-body {
  font-size: .92rem;
  color: var(--text-mid);
  max-width: 400px;
  line-height: 1.6;
}
.lm-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: .5rem;
  justify-content: center;
  margin-top: .5rem;
}
.lm-chip {
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text-mid);
  font-size: .78rem;
  padding: .35rem .75rem;
  border-radius: 99px;
  cursor: pointer;
  transition: border-color .2s, color .2s;
}

/* ── Chat message bubbles ────────────────────────────────────────────── */
.lm-msg-row {
  display: flex;
  align-items: flex-start;
  gap: .85rem;
  margin-bottom: 1.1rem;
  animation: fadeUp .25s ease both;
}
.lm-msg-row.user { flex-direction: row-reverse; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.lm-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
  border: 1.5px solid var(--border);
}
.lm-avatar.user { background: var(--user-bg); }
.lm-avatar.bot  { background: var(--accent-glow); border-color: var(--accent); }

.lm-bubble {
  max-width: 78%;
  padding: .9rem 1.15rem;
  border-radius: var(--radius);
  font-size: .9rem;
  line-height: 1.65;
  word-break: break-word;
}
.lm-bubble.user {
  background: var(--user-bg);
  border: 1px solid #2a304a;
  border-top-right-radius: 4px;
  color: var(--text-hi);
}
.lm-bubble.bot {
  background: var(--bot-bg);
  border: 1px solid var(--border);
  border-top-left-radius: 4px;
  color: var(--text-hi);
}

.lm-ts {
  font-size: .67rem;
  color: var(--text-lo);
  margin-top: .45rem;
  text-align: right;
}
.lm-msg-row.bot .lm-ts { text-align: left; }

/* ── Typing indicator ───────────────────────────────────────────────── */
.lm-typing {
  display: flex;
  align-items: center;
  gap: .85rem;
  margin-bottom: .6rem;
}
.lm-typing-dots {
  background: var(--bot-bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  border-top-left-radius: 4px;
  padding: .75rem 1rem;
  display: flex; gap: .4rem; align-items: center;
}
.lm-dot {
  width: 7px; height: 7px;
  background: var(--accent);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease;
}
.lm-dot:nth-child(2) { animation-delay: .2s; }
.lm-dot:nth-child(3) { animation-delay: .4s; }
@keyframes bounce {
  0%,80%,100% { transform: translateY(0); opacity: .5; }
  40%         { transform: translateY(-6px); opacity: 1; }
}

/* ── Input area ─────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input {
  background: var(--surface-2) !important;
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text-hi) !important;
  font-size: .92rem !important;
  padding: .7rem 1rem !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── Buttons ────────────────────────────────────────────────────────── */
[data-testid="stButton"] > button {
  background: var(--accent) !important;
  color: #fff !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  font-size: .88rem !important;
  transition: opacity .18s !important;
}
[data-testid="stButton"] > button:hover { opacity: .88 !important; }
[data-testid="stButton"] > button[kind="secondary"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-mid) !important;
}

/* ── Sidebar elements ───────────────────────────────────────────────── */
.lm-sidebar-section {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 1rem 1.1rem;
  margin-bottom: .9rem;
}
.lm-sidebar-label {
  font-size: .68rem;
  font-weight: 600;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--text-lo);
  margin-bottom: .55rem;
}
.lm-stat { display: flex; justify-content: space-between; align-items: center; }
.lm-stat-val {
  font-family: 'Sora', sans-serif;
  font-size: 1.45rem;
  font-weight: 700;
  color: var(--accent-soft);
}
.lm-stat-sub { font-size: .75rem; color: var(--text-mid); }

/* ── Divider ────────────────────────────────────────────────────────── */
.lm-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: .75rem 0;
}

/* ── Footer ─────────────────────────────────────────────────────────── */
.lm-footer {
  text-align: center;
  font-size: .7rem;
  color: var(--text-lo);
  padding: 1.2rem 0 .4rem;
  border-top: 1px solid var(--border);
  margin-top: 1rem;
}
.lm-footer a { color: var(--text-lo); text-decoration: none; }

/* ── Notification ───────────────────────────────────────────────────── */
.lm-notice {
  font-size: .8rem;
  padding: .6rem .9rem;
  border-radius: var(--radius-sm);
  margin-bottom: .7rem;
}
.lm-notice.error   { background: rgba(247,112,106,.1); border: 1px solid var(--error); color: var(--error); }
.lm-notice.success { background: rgba(62,207,142,.1);  border: 1px solid var(--success); color: var(--success); }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISATION
# ════════════════════════════════════════════════════════════════════════════

def init_session() -> None:
    """Initialise all session state keys once per session."""
    if "messages" not in st.session_state:
        st.session_state.messages: list[dict] = []

    if "gemini_client" not in st.session_state:
        try:
            st.session_state.gemini_client = create_client()
            st.session_state.chat_session  = create_chat_session(st.session_state.gemini_client)
            st.session_state.backend_error = None
        except EnvironmentError as e:
            st.session_state.gemini_client = None
            st.session_state.chat_session  = None
            st.session_state.backend_error = str(e)

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = None
    if "backend_error" not in st.session_state:
        st.session_state.backend_error = None
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.datetime.now()
    if "total_tokens_est" not in st.session_state:
        st.session_state.total_tokens_est = 0


init_session()


# ════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def add_message(role: str, content: str) -> None:
    """Append a message dict to the conversation history."""
    st.session_state.messages.append({
        "role":    role,
        "content": content,
        "ts":      datetime.datetime.now().strftime("%H:%M"),
    })


def clear_chat() -> None:
    """Reset conversation and create a fresh chat session."""
    st.session_state.messages = []
    st.session_state.total_tokens_est = 0
    if st.session_state.gemini_client:
        st.session_state.chat_session = create_chat_session(st.session_state.gemini_client)


def export_chat() -> str:
    """Render the chat history as a plain-text string for download."""
    lines: list[str] = [
        "═" * 60,
        "  LUMINA AI — Chat Export",
        f"  Session started : {st.session_state.session_start.strftime('%Y-%m-%d %H:%M')}",
        f"  Exported at     : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"  Model           : {MODEL_DISPLAY} ({MODEL_PROVIDER})",
        "═" * 60,
        "",
    ]
    for m in st.session_state.messages:
        who = "You" if m["role"] == "user" else "Lumina"
        lines.append(f"[{m['ts']}] {who}:")
        lines.append(m["content"])
        lines.append("")
    return "\n".join(lines)


def count_words(text: str) -> int:
    return len(text.split())


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    # ── Branding ──────────────────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:1.2rem;">
      <span style="font-size:1.6rem;filter:drop-shadow(0 0 8px #7c6af7)">✦</span>
      <div>
        <div style="font-family:'Sora',sans-serif;font-weight:700;font-size:1.05rem;
                    color:#eef0f7;letter-spacing:-.01em;">Lumina AI</div>
        <div style="font-size:.7rem;color:#555b6e;">Powered by Gemini 2.5 Flash</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Connection status ──────────────────────────────────────────────────
    if st.session_state.backend_error:
        st.markdown(
            f'<div class="lm-notice error">⚠ {st.session_state.backend_error}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="lm-notice success">● Connected to Gemini</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="lm-divider">', unsafe_allow_html=True)

    # ── Conversation stats ─────────────────────────────────────────────────
    st.markdown('<div class="lm-sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="lm-sidebar-label">Conversation stats</div>', unsafe_allow_html=True)

    msgs       = st.session_state.messages
    user_msgs  = sum(1 for m in msgs if m["role"] == "user")
    bot_msgs   = sum(1 for m in msgs if m["role"] == "assistant")
    total_words = sum(count_words(m["content"]) for m in msgs)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="lm-stat">
          <div>
            <div class="lm-stat-val">{user_msgs}</div>
            <div class="lm-stat-sub">You sent</div>
          </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="lm-stat">
          <div>
            <div class="lm-stat-val">{bot_msgs}</div>
            <div class="lm-stat-sub">Replies</div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:.7rem;">
      <div class="lm-stat-val" style="font-size:1.1rem">{total_words:,}</div>
      <div class="lm-stat-sub">total words exchanged</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Actions ────────────────────────────────────────────────────────────
    st.markdown('<div class="lm-sidebar-label" style="margin-top:.6rem">Actions</div>',
                unsafe_allow_html=True)

    if st.button("🗑  Clear chat", use_container_width=True):
        clear_chat()
        st.rerun()

    if msgs:
        export_text = export_chat()
        filename    = f"lumina_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        st.download_button(
            label="⬇  Export chat (.txt)",
            data=export_text,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown('<hr class="lm-divider">', unsafe_allow_html=True)

    # ── Model info ─────────────────────────────────────────────────────────
    st.markdown('<div class="lm-sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="lm-sidebar-label">Model information</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:.82rem;color:#9298aa;line-height:1.6;">
      <div style="margin-bottom:.35rem;">
        <span style="color:#eef0f7;font-weight:600;">{MODEL_DISPLAY}</span>
      </div>
      <div style="margin-bottom:.35rem;color:#555b6e;">Provider: {MODEL_PROVIDER}</div>
      <div>{MODEL_DESCRIPTION}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Session info ───────────────────────────────────────────────────────
    elapsed = datetime.datetime.now() - st.session_state.session_start
    mins    = int(elapsed.total_seconds() // 60)
    st.markdown(f"""
    <div style="font-size:.7rem;color:#555b6e;margin-top:.5rem;text-align:center;">
      Session active for {mins} min
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT AREA
# ════════════════════════════════════════════════════════════════════════════

# ── Header banner ──────────────────────────────────────────────────────────
st.markdown("""
<div class="lm-header">
  <div class="lm-header-eyebrow">✦ AI Assistant</div>
  <h1 class="lm-header-title">Lumina <span>AI</span></h1>
  <p class="lm-header-sub">
    A production-grade conversational AI built on Google's Gemini 2.5 Flash.
    Ask anything — from creative writing to code, analysis to advice.
  </p>
  <span class="lm-badge">Live · Multi-turn · Context-aware</span>
</div>
""", unsafe_allow_html=True)

# ── Error banner (API key / network) ──────────────────────────────────────
if st.session_state.backend_error:
    st.markdown(f"""
    <div class="lm-notice error" style="font-size:.88rem;padding:.8rem 1rem;">
      <strong>Configuration error:</strong> {st.session_state.backend_error}<br>
      <span style="opacity:.75">Open <code>.env</code> and set 
      <code>GEMINI_API_KEY=your_key_here</code>, then restart the app.</span>
    </div>""", unsafe_allow_html=True)

# ── Chat area container ────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        # ── Welcome screen ─────────────────────────────────────────────────
        st.markdown("""
        <div class="lm-welcome">
          <div class="lm-welcome-icon">✦</div>
          <p class="lm-welcome-title">How can I help you today?</p>
          <p class="lm-welcome-body">
            I'm Lumina, your AI assistant powered by Gemini 2.5 Flash.
            I retain context throughout our conversation, so feel free to ask
            follow-up questions.
          </p>
          <div class="lm-chip-row">
            <span class="lm-chip">✍ Draft an email</span>
            <span class="lm-chip">🐍 Write Python code</span>
            <span class="lm-chip">📊 Explain a concept</span>
            <span class="lm-chip">🔍 Research a topic</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── Render message history ──────────────────────────────────────────
        for msg in st.session_state.messages:
            is_user   = msg["role"] == "user"
            row_class = "user" if is_user else "bot"
            avatar    = "🧑" if is_user else "✦"
            av_class  = "user" if is_user else "bot"

            # Escape HTML in user content but allow markdown in assistant content
            content = msg["content"].replace("<", "&lt;").replace(">", "&gt;") \
                      if is_user else msg["content"]

            st.markdown(f"""
            <div class="lm-msg-row {row_class}">
              <div class="lm-avatar {av_class}">{avatar}</div>
              <div>
                <div class="lm-bubble {row_class}">{content}</div>
                <div class="lm-ts">{msg['ts']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

# ── Typing indicator placeholder ──────────────────────────────────────────
typing_placeholder = st.empty()

# ── Input row ──────────────────────────────────────────────────────────────
# ── Input row ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):

    user_input = st.text_input(
        label="Message",
        placeholder="Type your message...",
        label_visibility="collapsed",
        disabled=bool(st.session_state.backend_error),
    )

    send_btn = st.form_submit_button(
        "Send",
        use_container_width=True,
        disabled=bool(st.session_state.backend_error),
    )

# ── Handle send ────────────────────────────────────────────────────────────
if send_btn and user_input.strip():
    prompt = user_input.strip()

    # Record user message
    add_message("user", prompt)

    # Show typing indicator
    with typing_placeholder:
        st.markdown("""
        <div class="lm-typing">
          <div class="lm-avatar bot">✦</div>
          <div class="lm-typing-dots">
            <div class="lm-dot"></div>
            <div class="lm-dot"></div>
            <div class="lm-dot"></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── Call backend ────────────────────────────────────────────────────────
    try:
        with st.spinner(""):
            reply = get_response(st.session_state.chat_session, prompt)
        add_message("assistant", reply)
        # Rough token estimate (4 chars ≈ 1 token)
        st.session_state.total_tokens_est += (len(prompt) + len(reply)) // 4
    except Exception as exc:
        add_message(
            "assistant",
            f"⚠ Something went wrong: {exc}\n\nPlease try again.",
        )

    typing_placeholder.empty()
    st.rerun()

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lm-footer">
  Lumina AI &nbsp;·&nbsp; Powered by <a href="https://deepmind.google/technologies/gemini/"
  target="_blank">Gemini 2.5 Flash</a> &nbsp;·&nbsp;
  Conversations are not stored beyond this session.
</div>
""", unsafe_allow_html=True)
