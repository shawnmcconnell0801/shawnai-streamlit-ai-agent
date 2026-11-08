import json
import os
import textwrap
import uuid
from datetime import datetime

import ollama
import streamlit as st

from database import (
    initialize_database,
    save_chat,
    save_message,
    load_chats,
    load_messages,
    delete_chat as db_delete_chat,
    clear_chat_messages,
)


# ============================================================
# 1. APP CONFIGURATION
# ============================================================

APP_NAME = "ShawnAI"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_CLIENT = ollama.Client(host=OLLAMA_HOST)
APP_TAGLINE = "Think clearly. Explore ideas. Build something great."

st.set_page_config(
    page_title=f"{APP_NAME} | AI Workspace",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. CUSTOM DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #0a1020;
        --sidebar: #0e192b;
        --surface: #121f33;
        --surface-2: #172840;
        --surface-3: #1b304b;
        --border: #263c58;
        --border-soft: rgba(132, 164, 198, .13);
        --text: #edf5ff;
        --muted: #91a6c0;
        --muted-2: #7188a5;
        --accent: #67d5ff;
        --accent-2: #37b8e8;
        --success: #53d6a4;
        --danger: #ff7e8b;
    }

    html, body, [class*="css"] { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: radial-gradient(ellipse at 50% -18%, #172b46 0%, var(--bg) 47%) !important;
        color: var(--text) !important;
    }
    [data-testid="stHeader"] { background: rgba(10,16,32,.82) !important; }
    [data-testid="stToolbar"] { right: 1rem; }
    .block-container { max-width: 1480px; padding-top: 1.8rem; padding-bottom: 2.5rem; }

    /* Sidebar */
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, #101d31 0%, #0d1728 100%) !important;
        border-right: 1px solid var(--border-soft);
    }
    [data-testid="stSidebar"] .block-container { padding-top: 1.15rem; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .55rem; }
    [data-testid="stSidebar"] hr { border-color: var(--border-soft) !important; margin: .7rem 0; }

    /* Brand */
    .brand-wrap { padding: .35rem .15rem 1.15rem; }
    .brand-mark {
        display: inline-flex; align-items: center; justify-content: center;
        width: 36px; height: 36px; border-radius: 12px;
        color: #071321; font-size: 21px; font-weight: 900;
        background: linear-gradient(135deg, #8ce4ff, #39b8e8);
        box-shadow: 0 7px 24px rgba(55,184,232,.18);
        vertical-align: middle; margin-right: 9px;
    }
    .brand-name { display: inline-block; color: #f2f7ff; font-size: 26px; font-weight: 850; letter-spacing: -1.2px; vertical-align: middle; }
    .brand-name span { color: var(--accent); }
    .brand-caption { color: #7890ad; font-size: 9px; letter-spacing: 2.2px; font-weight: 800; margin: 9px 0 0 3px; }

    /* General buttons */
    .stButton > button, .stDownloadButton > button {
        min-height: 2.55rem; border-radius: 10px !important;
        border: 1px solid #2b425f !important;
        background: #172840 !important; color: #e4effc !important;
        font-weight: 650 !important; transition: all .18s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--accent) !important; background: #1d3855 !important;
        color: #fff !important; transform: translateY(-1px);
        box-shadow: 0 5px 18px rgba(0,0,0,.15);
    }
    .stButton > button:focus, .stDownloadButton > button:focus { box-shadow: 0 0 0 2px rgba(103,213,255,.2) !important; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #174563, #15344f) !important;
        border-color: #4384a5 !important; color: #effaff !important;
    }
    [data-testid="stPopover"] > button {
        background: linear-gradient(135deg, #173a55, #152b43) !important;
        border: 1px solid #39708f !important; color: #e6f8ff !important;
        border-radius: 10px !important; font-weight: 700 !important;
    }
    [data-testid="stPopover"] > button:hover { border-color: var(--accent) !important; background: #1d4968 !important; }

    /* Inputs */
    [data-testid="stTextInput"] input, [data-testid="stChatInput"] textarea {
        background: #111f33 !important; color: var(--text) !important;
        border: 1px solid #2b425f !important; border-radius: 11px !important;
    }
    [data-testid="stTextInput"] input:focus, [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent) !important; box-shadow: 0 0 0 1px rgba(103,213,255,.15) !important;
    }
    [data-testid="stTextInput"] input::placeholder, [data-testid="stChatInput"] textarea::placeholder { color: #7087a3 !important; }
    [data-testid="stChatInput"] { background: #111f33 !important; border: 1px solid #304a68 !important; border-radius: 15px !important; }
    [data-testid="stChatInput"] button { color: var(--accent) !important; }

    /* Sidebar section labels and chat list */
    .section-label { color: #8da4bf; font-size: 10px; font-weight: 800; letter-spacing: 1.65px; margin: .15rem 0 .25rem; }
    .history-hint { color: #6f86a2; font-size: 11px; line-height: 1.5; padding: .2rem 0 .4rem; }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { gap: .35rem; align-items: center; }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child .stButton > button {
        min-height: 2.35rem; padding-left: .25rem; padding-right: .25rem;
        color: #9bb0c8 !important; background: transparent !important;
        border-color: transparent !important;
    }
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child .stButton > button:hover {
        color: var(--danger) !important; background: rgba(255,126,139,.08) !important;
        border-color: rgba(255,126,139,.25) !important;
    }

    /* Model card */
    .model-card { background: linear-gradient(145deg, #172b43, #122238); border: 1px solid #2b425e; border-radius: 14px; padding: 14px; margin-top: .35rem; }
    .model-card-title { color: #e8f2ff; font-size: 12px; font-weight: 800; letter-spacing: .5px; }
    .model-card-copy { color: #8198b3; font-size: 10px; line-height: 1.7; margin-top: 7px; }
    .status-dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 7px; vertical-align: 1px; }
    .status-dot.online { background: var(--success); box-shadow: 0 0 9px rgba(83,214,164,.45); }
    .status-dot.offline { background: var(--danger); }
    .status-dot.warning { background: #f5c66b; }
    .sidebar-footer { color: #607995; font-size: 9px; letter-spacing: 1.4px; text-align: center; padding: 1rem 0 .25rem; }

    /* Main header */
    .eyebrow { color: var(--accent); font-size: 10px; font-weight: 800; letter-spacing: 2.1px; }
    .main-title { color: #f2f7ff; font-size: clamp(30px, 3.2vw, 42px); line-height: 1.12; font-weight: 850; letter-spacing: -1.8px; margin-top: 5px; }
    .main-title span { color: var(--accent); }
    .main-subtitle { color: #91a7c1; font-size: 13px; margin-top: 8px; }
    .header-status { display: inline-flex; align-items: center; gap: 7px; background: rgba(35,105,82,.18); border: 1px solid rgba(83,214,164,.28); color: #83e7bf; border-radius: 30px; padding: 7px 11px; font-size: 10px; font-weight: 800; letter-spacing: .7px; white-space: nowrap; }
    .header-status.offline { background: rgba(140,45,58,.15); border-color: rgba(255,126,139,.28); color: #ff9ca6; }

    /* Welcome area */
    .welcome-card { position: relative; overflow: hidden; background: linear-gradient(125deg, rgba(26,54,82,.98), rgba(16,30,49,.98)); border: 1px solid #2d4967; border-radius: 20px; padding: clamp(25px, 4vw, 42px); margin: 1.1rem 0 1.2rem; }
    .welcome-card:after { content: "✦"; position: absolute; right: 6%; top: 7%; color: rgba(103,213,255,.09); font-size: 150px; line-height: 1; pointer-events: none; }
    .welcome-kicker { color: var(--accent); font-size: 10px; font-weight: 800; letter-spacing: 2px; }
    .welcome-title { color: #f3f8ff; font-size: clamp(25px, 3vw, 34px); line-height: 1.2; font-weight: 850; letter-spacing: -1px; margin-top: 11px; }
    .welcome-copy { color: #a1b4ca; font-size: 13px; line-height: 1.85; max-width: 650px; margin-top: 10px; }
    .feature-card { min-height: 142px; height: 100%; background: linear-gradient(150deg, #152840, #111e31); border: 1px solid #2a405b; border-radius: 15px; padding: 19px; }
    .feature-icon { color: var(--accent); font-size: 21px; margin-bottom: 10px; }
    .feature-title { color: #e9f2fd; font-size: 13px; font-weight: 800; }
    .feature-copy { color: #879db7; font-size: 11px; line-height: 1.7; margin-top: 7px; }

    /* Chat transcript */
    [data-testid="stChatMessage"] { background: rgba(19,34,55,.82) !important; border: 1px solid #263d59 !important; border-radius: 15px !important; padding: 15px 17px !important; margin-bottom: 13px !important; }
    [data-testid="stChatMessage"] p { line-height: 1.72; }
    [data-testid="stChatMessage"] code { color: #a8e8ff; }
    [data-testid="stChatMessage"] pre { border: 1px solid #2c4561; border-radius: 10px; }
    [data-testid="stChatMessage"] a { color: var(--accent) !important; }

    /* Popovers, expanders and misc */
    [data-testid="stPopoverBody"], [data-testid="stExpander"] { background: #132238 !important; border: 1px solid #2b425e !important; border-radius: 12px !important; }
    [data-testid="stDownloadButton"] > button { font-size: 12px !important; }
    [data-testid="stAlert"] { border-radius: 12px; }
    .main-footer { color: #637d9a; font-size: 10px; text-align: center; letter-spacing: .4px; padding: 1.1rem 0 .2rem; }
    hr { border-color: rgba(132,164,198,.14) !important; margin: 1.05rem 0 !important; }

    /* Hide Streamlit's default footer/menu, keep the toolbar available. */
    #MainMenu, footer { visibility: hidden; }

    @media (max-width: 760px) {
        .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }
        .main-title { font-size: 31px; }
        .welcome-card { padding: 25px; }
    }

    /* ShawnAI active conversation */
[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #174563, #15344F) !important;
    border: 1px solid #4384A5 !important;
    color: #EAF8FF !important;
}

[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, #205B7D, #194766) !important;
    border-color: #67D5FF !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_html(content: str) -> None:
    """Render trusted, static app markup with consistent indentation."""
    st.html(textwrap.dedent(content).strip())


# ============================================================
# 3. OLLAMA HEALTH CHECK
# ============================================================

@st.cache_data(ttl=25, show_spinner=False)
def get_ollama_status():
    """Return connection state and locally available model names."""
    try:
        result = OLLAMA_CLIENT.list()
        models = result.get("models", []) if isinstance(result, dict) else getattr(result, "models", [])
        names = []
        for item in models:
            if isinstance(item, dict):
                name = item.get("model") or item.get("name")
            else:
                name = getattr(item, "model", None) or getattr(item, "name", None)
            if name:
                names.append(name)
        return True, names, None
    except Exception as exc:
        return False, [], str(exc)


ollama_online, installed_models, ollama_error = get_ollama_status()
model_available = MODEL_NAME in installed_models


# ============================================================
# 4. DATABASE AND SESSION STATE
# ============================================================

initialize_database()

if "chats" not in st.session_state:
    st.session_state.chats = {}
    for saved_chat_id, saved_title in load_chats():
        saved_messages = load_messages(saved_chat_id)

        # Repair default titles created by earlier versions of the app.
        if saved_title == "New Conversation":
            first_user_message = next(
                (m["content"] for m in saved_messages if m["role"] == "user"),
                None,
            )
            if first_user_message:
                cleaned = " ".join(first_user_message.split())
                saved_title = cleaned[:27] + "..." if len(cleaned) > 30 else cleaned
                save_chat(saved_chat_id, saved_title)

        st.session_state.chats[saved_chat_id] = {
            "title": saved_title,
            "messages": saved_messages,
        }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "chat_search" not in st.session_state:
    st.session_state.chat_search = ""


# ============================================================
# 5. CHAT MANAGEMENT
# ============================================================

def create_new_chat():
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "title": "New Conversation",
        "messages": [],
    }
    st.session_state.current_chat = chat_id
    save_chat(chat_id, "New Conversation")


def delete_chat(chat_id: str):
    if chat_id not in st.session_state.chats:
        return

    del st.session_state.chats[chat_id]
    db_delete_chat(chat_id)

    if st.session_state.current_chat == chat_id:
        if st.session_state.chats:
            st.session_state.current_chat = next(iter(st.session_state.chats))
        else:
            create_new_chat()


def clear_current_chat(chat_id: str):
    chat = st.session_state.chats[chat_id]
    chat["messages"] = []
    chat["title"] = "New Conversation"
    clear_chat_messages(chat_id)
    save_chat(chat_id, "New Conversation")


def make_chat_title(message: str) -> str:
    cleaned = " ".join(message.split())
    return cleaned[:27] + "..." if len(cleaned) > 30 else cleaned


if not st.session_state.chats:
    create_new_chat()

if st.session_state.current_chat not in st.session_state.chats:
    st.session_state.current_chat = next(iter(st.session_state.chats))


# ============================================================
# 6. SIDEBAR — BRAND, HISTORY, MODEL STATUS
# ============================================================

with st.sidebar:
    render_html(
        """
        <div class="brand-wrap">
            <div><span class="brand-mark">✦</span><span class="brand-name">Shawn<span>AI</span></span></div>
            <div class="brand-caption">YOUR PERSONAL AI WORKSPACE</div>
        </div>
        """
    )

    if st.button("＋  New conversation", use_container_width=True, type="primary"):
        create_new_chat()
        st.rerun()

    st.divider()
    render_html('<div class="section-label">YOUR CONVERSATIONS</div>')

    search_value = st.text_input(
        "Search conversations",
        placeholder="Find a conversation...",
        label_visibility="collapsed",
        key="chat_search",
    )

    chat_items = list(st.session_state.chats.items())
    query = search_value.strip().casefold()
    if query:
        chat_items = [
            (cid, chat) for cid, chat in chat_items
            if query in chat["title"].casefold()
            or any(query in msg["content"].casefold() for msg in chat["messages"])
        ]

    if not chat_items:
        render_html('<div class="history-hint">No matching conversations. Try another search.</div>')
    else:
        for saved_chat_id, chat in chat_items:
            is_active = saved_chat_id == st.session_state.current_chat
            title = chat["title"] or "New Conversation"
            display_title = title if len(title) <= 31 else title[:28] + "..."
            chat_col, menu_col = st.columns([5.2, 1])

            with chat_col:
                if st.button(
                    ("●  " if is_active else "   ") + display_title,
                    key=f"open_{saved_chat_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    help=title,
                ):
                    st.session_state.current_chat = saved_chat_id
                    st.rerun()

            with menu_col:
                with st.popover("⋯", help="Conversation actions"):
                    st.caption("Conversation actions")
                    if st.button(
                        "Delete conversation",
                        key=f"delete_{saved_chat_id}",
                        use_container_width=True,
                    ):
                        delete_chat(saved_chat_id)
                        st.rerun()

    st.divider()

    if ollama_online and model_available:
        model_dot_class = "online"
        model_status_text = "CONNECTED · MODEL READY"
    elif ollama_online:
        model_dot_class = "warning"
        model_status_text = "CONNECTED · MODEL NOT FOUND"
    else:
        model_dot_class = "offline"
        model_status_text = "OLLAMA NOT REACHABLE"

    render_html(
        f"""
        <div class="model-card">
            <div class="model-card-title"><span class="status-dot {model_dot_class}"></span>MODEL STATUS</div>
            <div class="model-card-copy">
                <strong style="color:#dcecff">{MODEL_NAME}</strong><br>
                {model_status_text}<br>
                LOCAL INFERENCE VIA OLLAMA
            </div>
        </div>
        <div class="sidebar-footer">SHAWNAI · PRIVATE LOCAL AI WORKSPACE</div>
        """
    )


# ============================================================
# 7. CURRENT CONVERSATION AND EXPORT DATA
# ============================================================

chat_id = st.session_state.current_chat
current_chat = st.session_state.chats[chat_id]
messages = current_chat["messages"]


def create_text_export(chat: dict) -> str:
    lines = [f"ShawnAI Conversation: {chat['title']}", "=" * 58, ""]
    for message in chat["messages"]:
        speaker = "You" if message["role"] == "user" else "ShawnAI"
        lines.extend([f"{speaker}:", message["content"], "", "-" * 58, ""])
    return "\n".join(lines)


current_export = {
    "application": APP_NAME,
    "title": current_chat["title"],
    "messages": messages,
}
all_chats_export = {
    "application": APP_NAME,
    "exported_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    "conversations": {
        saved_chat_id: {"title": chat["title"], "messages": chat["messages"]}
        for saved_chat_id, chat in st.session_state.chats.items()
    },
}


# ============================================================
# 8. MAIN HEADER AND ACTIONS
# ============================================================

header_col, export_col, clear_col = st.columns([5.2, 1.35, 1.35])

with header_col:
    render_html(
        f"""
        <div class="eyebrow">PERSONAL AI ASSISTANT</div>
        <div class="main-title">ShawnAI <span>✦</span></div>
        <div class="main-subtitle">{APP_TAGLINE}</div>
        """
    )

with export_col:
    with st.popover("⇩  Export", use_container_width=True):
        st.markdown("**Export conversations**")
        st.caption("Download this chat or back up your complete history.")
        st.download_button(
            "↓  Current chat · TXT",
            data=create_text_export(current_chat),
            file_name="shawnaI_conversation.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=not messages,
            key="export_current_txt",
        )
        st.download_button(
            "◇  Current chat · JSON",
            data=json.dumps(current_export, indent=2, ensure_ascii=False),
            file_name="shawnaI_conversation.json",
            mime="application/json",
            use_container_width=True,
            disabled=not messages,
            key="export_current_json",
        )
        st.divider()
        st.download_button(
            "⇩  Backup all conversations",
            data=json.dumps(all_chats_export, indent=2, ensure_ascii=False),
            file_name="shawnaI_all_conversations.json",
            mime="application/json",
            use_container_width=True,
            disabled=not any(c["messages"] for c in st.session_state.chats.values()),
            key="export_all_chats",
        )

with clear_col:
    with st.popover("⌫  Clear chat", use_container_width=True):
        st.caption("This removes all messages from the current conversation. It cannot be undone.")
        if st.button("Confirm clear", key="confirm_clear_chat", use_container_width=True):
            clear_current_chat(chat_id)
            st.rerun()

status_class = "" if ollama_online and model_available else "offline"
status_label = "MODEL READY" if ollama_online and model_available else ("MODEL MISSING" if ollama_online else "OLLAMA OFFLINE")
render_html(
    f'<div style="display:flex;justify-content:flex-end;margin-top:.15rem"><span class="header-status {status_class}">● {status_label}</span></div>'
)
st.divider()


# ============================================================
# 9. WELCOME SCREEN
# ============================================================

if not messages:
    render_html(
        """
        <div class="welcome-card">
            <div class="welcome-kicker">WELCOME TO SHAWNAI</div>
            <div class="welcome-title">A smarter space to think.</div>
            <div class="welcome-copy">
                Ask questions, explore new concepts, solve problems and turn your ideas into reality.
                Your AI assistant is ready whenever you are.
            </div>
        </div>
        """
    )

    feature_columns = st.columns(3)
    feature_data = [
        ("✦", "Explore ideas", "Brainstorm, discover concepts and explore new possibilities."),
        ("⌘", "Code & create", "Work through programming problems and develop your ideas."),
        ("◈", "Learn anything", "Break down difficult topics with clear, structured explanations."),
    ]
    for column, (icon, title, description) in zip(feature_columns, feature_data):
        with column:
            render_html(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{icon}</div>
                    <div class="feature-title">{title}</div>
                    <div class="feature-copy">{description}</div>
                </div>
                """
            )

    st.markdown(" ")
    st.caption("💡 Tip: Ask a follow-up question at any time to keep exploring the same topic.")


# ============================================================
# 10. CHAT HISTORY
# ============================================================

for message in messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# ============================================================
# 11. CHAT INPUT AND RESPONSE GENERATION
# ============================================================

prompt = st.chat_input("Message ShawnAI...", disabled=not (ollama_online and model_available))

if prompt and prompt.strip():
    prompt = prompt.strip()

    # Name a conversation from its first user message.
    if not messages:
        current_chat["title"] = make_chat_title(prompt)
        save_chat(chat_id, current_chat["title"])

    messages.append({"role": "user", "content": prompt})
    save_message(chat_id, "user", prompt)

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    system_message = {
        "role": "system",
        "content": (
            "You are ShawnAI, a helpful and intelligent AI assistant. "
            "Remember relevant information from this conversation and use it for follow-up questions. "
            "Be friendly, accurate, and clear. Explain difficult concepts in simple language. "
            "Use Markdown formatting when it improves readability, and avoid unnecessary repetition. "
            "If you are uncertain, say so rather than inventing facts."
        ),
    }

    with st.chat_message("assistant", avatar="🤖"):
        try:
            with st.spinner("ShawnAI is thinking..."):
                response_stream = OLLAMA_CLIENT.chat(
                    model=MODEL_NAME,
                    messages=[system_message] + messages,
                    stream=True,
                )
                answer = st.write_stream(
                    chunk["message"]["content"] for chunk in response_stream
                )

            if not isinstance(answer, str) or not answer.strip():
                answer = "I couldn't produce a response this time. Please try again."
                st.warning(answer)

            messages.append({"role": "assistant", "content": answer})
            save_message(chat_id, "assistant", answer)

        except Exception as exc:
            st.error(
                "ShawnAI couldn't complete the response. Check that Ollama is running "
                f"and that **{MODEL_NAME}** is installed, then try again."
            )
            with st.expander("Technical details"):
                st.code(str(exc))

    # Refresh title, exports, and sidebar history after the new turn.
    st.rerun()


# ============================================================
# 12. CONNECTION HELP
# ============================================================

if not ollama_online:
    st.warning(
        "Ollama is currently unreachable. Start the Ollama application or run `ollama serve`, "
        "then refresh ShawnAI."
    )
elif not model_available:
    st.warning(
        f"The Ollama service is available, but **{MODEL_NAME}** was not found. "
        f"Install it with `ollama pull {MODEL_NAME}`, then refresh ShawnAI."
    )

render_html('<div class="main-footer">SHAWNAI · BUILT FOR THOUGHTFUL CONVERSATIONS</div>')
