import streamlit as st
import ollama

st.set_page_config(page_title="Local AI Chatbot", layout="centered")
st.title("🧠 Local AI Chatbot")

# -----------------------------
# Sidebar (Controls)
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    model = st.selectbox(
        "Choose model",
        ["gemma3:1b"]
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        value=0.7,
        step=0.1
    )

    if st.button("🧹 Clear chat"):
        st.session_state.messages = []
        st.rerun()

# -----------------------------
# Session Memory
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Render Chat History
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# Chat Input
# -----------------------------
user_input = st.chat_input("Type your message")

if user_input:
    # store user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    # call local LLM
    response = ollama.chat(
        model=model,
        messages=st.session_state.messages,
        options={"temperature": temperature}
    )

    reply = response["message"]["content"]

    # store assistant reply
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.write(reply)