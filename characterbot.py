import streamlit as st
import ollama
import base64
from pathlib import Path
import random
import time


# -----------------------------
# Helper Functions (Cached)
# -----------------------------
@st.cache_data
def video_to_base64(video_path):
    return base64.b64encode(Path(video_path).read_bytes()).decode()

@st.cache_data
def image_to_base64(image_path):
    return base64.b64encode(Path(image_path).read_bytes()).decode()


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Spider-Verse AI Chatbot", layout="wide")


# -----------------------------
# TOP RIGHT MODE SWITCH
# -----------------------------
top_left, top_right = st.columns([8, 2])

with top_right:
    character_mode = st.radio(
        "",
        ["Miles", "Gwen", "Dual"],
        horizontal=True,
        label_visibility="collapsed"
    )


# -----------------------------
# Sidebar Controls
# -----------------------------
with st.sidebar:
    st.markdown("## ⚙️ AI Settings")

    model = st.selectbox("Choose Model", ["gemma3:1b"])

    temperature = st.slider(
        "Creativity Level",
        min_value=0.0,
        max_value=1.5,
        value=0.9,
        step=0.1
    )

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.initialized = False
        st.rerun()


# -----------------------------
# Theme + Background Setup
# -----------------------------
bg_type = "video"

if character_mode == "Miles":
    theme_color = "#ff003c"
    glow_color = "#ff003c"
    bg_type = "video"
    video_file = "miles_bg.mp4"

elif character_mode == "Gwen":
    theme_color = "#ff4fd8"
    glow_color = "#ffffff"
    bg_type = "image"
    image_file = "gwen_bg.jpg"

else:
    theme_color = "#b300ff"
    glow_color = "#ff4fd8"
    bg_type = "image"
    image_file = "migw_bg.jpg"


# -----------------------------
# Load Background
# -----------------------------
video_base64 = ""
image_base64 = ""

if bg_type == "video":
    video_base64 = video_to_base64(video_file)
else:
    image_base64 = image_to_base64(image_file)


# -----------------------------
# Background HTML
# -----------------------------
if bg_type == "video":
    background_html = f"""
    <div class="bg-video">
        <video autoplay loop muted playsinline preload="auto">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
    </div>
    """
else:
    background_html = f"""
    <div class="bg-image"></div>
    <style>
    .bg-image {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -10;
        background-image: url("data:image/jpg;base64,{image_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        filter: brightness(0.85) contrast(1.15) saturate(1.3);
    }}
    </style>
    """


# -----------------------------
# CSS Styling
# -----------------------------
st.markdown(
    f"""
    <style>

    /* REMOVE HEADER / TOOLBAR */
    div[data-testid="stDecoration"] {{
        display: none !important;
    }}

    header[data-testid="stHeader"] {{
        display: none !important;
    }}

    div[data-testid="stToolbar"] {{
        display: none !important;
    }}

    /* Remove padding */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
    }}

    .stApp {{
        background: transparent !important;
    }}

    /* BACKGROUND VIDEO */
    .bg-video {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -10;
        overflow: hidden;
    }}

    .bg-video video {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        filter: brightness(0.85) contrast(1.2) saturate(1.4);
    }}

    /* Overlay */
    .overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.22);
        z-index: -9;
    }}

    /* Title (MOVED UP) */
    .main-title {{
        font-size: 55px;
        font-weight: 900;
        text-align: center;
        color: white;
        text-shadow: 0px 0px 25px {glow_color};
        margin-top: 5px;
        margin-bottom: 0px;
    }}

    .sub-title {{
        font-size: 18px;
        font-weight: 800;
        text-align: center;
        color: {theme_color};
        text-shadow: 0px 0px 20px {glow_color};
        margin-top: 6px;
        margin-bottom: 20px;
        letter-spacing: 2px;
    }}

    /* Chat container */
    .chat-container {{
        background: rgba(0,0,0,0.25);
        border: 2px solid {theme_color};
        box-shadow: 0px 0px 35px {glow_color};
        border-radius: 25px;
        padding: 25px;
        backdrop-filter: blur(10px);
    }}

    /* Remove black chat input bar container */
    div[data-testid="stChatInput"] {{
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        padding: 0px !important;
    }}

    div[data-testid="stChatInput"] > div {{
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }}

    /* Chat input textarea */
    textarea {{
        background: rgba(0,0,0,0.35) !important;
        border: 2px solid {theme_color} !important;
        color: white !important;
        border-radius: 18px !important;
        box-shadow: 0px 0px 18px {glow_color} !important;
        font-size: 16px !important;
    }}

    /* Chat messages */
    .stChatMessage {{
        border-radius: 18px !important;
        padding: 12px !important;
        font-size: 16px;
    }}

    /* User bubble */
    div[data-testid="stChatMessage"][aria-label="Chat message from user"] {{
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        box-shadow: 0px 0px 15px rgba(255,255,255,0.18);
    }}

    /* Assistant bubble */
    div[data-testid="stChatMessage"][aria-label="Chat message from assistant"] {{
        background: rgba(0,0,0,0.40) !important;
        border: 1px solid {theme_color} !important;
        box-shadow: 0px 0px 18px {glow_color};
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: rgba(0,0,0,0.65) !important;
        border-right: 2px solid {theme_color};
        box-shadow: 0px 0px 25px {glow_color};
    }}

    /* TOP RIGHT SWITCH */
    div[role="radiogroup"] {{
        background: rgba(0,0,0,0.45);
        padding: 7px 12px;
        border-radius: 18px;
        border: 1px solid {theme_color};
        box-shadow: 0px 0px 15px {glow_color};
        display: flex;
        justify-content: center;
        gap: 12px;
    }}

    div[role="radiogroup"] label {{
        color: white !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }}

    /* WEB SHOOT LOADING ANIMATION */
    .web-line {{
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, transparent, {theme_color}, white, {theme_color}, transparent);
        animation: shoot 0.7s linear infinite;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 15px;
        box-shadow: 0px 0px 15px {glow_color};
    }}

    @keyframes shoot {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}

    </style>

    {background_html}

    <div class="overlay"></div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Title
# -----------------------------
st.markdown("<div class='main-title'>🕷️ Spider-Verse AI Chatbot</div>", unsafe_allow_html=True)

if character_mode == "Miles":
    st.markdown("<div class='sub-title'>MILES MORALES MODE 🔥</div>", unsafe_allow_html=True)
elif character_mode == "Gwen":
    st.markdown("<div class='sub-title'>GWEN STACY MODE 🎸</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='sub-title'>DUAL MODE ⚡ MILES + GWEN</div>", unsafe_allow_html=True)


# -----------------------------
# System Prompt
# -----------------------------
def get_system_prompt(mode):
    if mode == "Miles":
        return """
        You are Miles Morales from Spider-Verse.
        Speak like a chill Brooklyn teen: funny, energetic, heroic.
        Use slang lightly, be supportive, interactive, playful.
        NEVER insult the user.
        Ask questions back often.
        """

    elif mode == "Gwen":
        return """
        You are Gwen Stacy (Spider-Gwen).
        Speak confident, witty, calm, sometimes sarcastic but caring.
        Mention music/drums occasionally.
        Ask questions back often.
        """

    else:
        return """
        You are BOTH Miles Morales and Gwen Stacy.
        Respond like a duo conversation.

        Format replies like:

        Miles: ...
        Gwen: ...

        Miles is funny and chill.
        Gwen is confident and witty.
        Keep it lively and interactive.
        Ask the user questions back.
        """


# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "last_mode" not in st.session_state:
    st.session_state.last_mode = character_mode


# Reset if mode changes
if st.session_state.last_mode != character_mode:
    st.session_state.messages = []
    st.session_state.initialized = False
    st.session_state.last_mode = character_mode
    st.rerun()


# Init system prompt
if not st.session_state.initialized:
    st.session_state.messages.append(
        {"role": "system", "content": get_system_prompt(character_mode)}
    )
    st.session_state.initialized = True


# -----------------------------
# Chat History
# -----------------------------
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Chat Input
# -----------------------------
user_input = st.chat_input("Type your message... 🕸️")


if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # WEB SHOOT LOADING EFFECT
    web_anim = st.empty()
    web_anim.markdown("<div class='web-line'></div>", unsafe_allow_html=True)

    response = ollama.chat(
        model=model,
        messages=st.session_state.messages,
        options={"temperature": temperature}
    )

    web_anim.empty()

    reply = response["message"]["content"]

    effects = ["🕷️", "🔥", "💥", "⚡", "🎸", "🕸️", "😏", "😈"]
    reply = reply + "\n\n" + random.choice(effects)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.write(reply)
