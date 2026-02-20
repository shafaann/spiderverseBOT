import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Updated import: pulling the retriever from gvector.py
from vector import retriever

# Configure the Streamlit page
st.set_page_config(page_title="Gold Price Assistant", page_icon="🪙", layout="centered")
st.title("🪙 Historical Gold Price Chatbot")
st.write("Ask me anything about the historical gold price data!")

# --- 1. Setup LLM & Chain (Cached) ---
# We use @st.cache_resource so the model and chain aren't rebuilt on every user interaction
@st.cache_resource
def get_chain():
    model = OllamaLLM(model="gemma3:1b")
    
    template = """
    You are a factual assistant that answers questions about historical gold prices.

    You must follow these rules:
    - Use ONLY the provided gold price records
    - Do NOT make assumptions or predictions
    - Do NOT calculate averages or trends unless explicitly present
    - If the answer is not found in the records, say: "The data does not contain this information."

    Gold price records:
    {records}

    User question:
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt | model

chain = get_chain()

# --- 2. Manage Chat History ---
# Initialize session state to hold the conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. Handle User Input ---
if question := st.chat_input("Ask a gold price question (e.g., 'What was the highest price in 2023?'):"):
    
    # Display the user's question
    with st.chat_message("user"):
        st.markdown(question)
    
    # Save the user's question to state
    st.session_state.messages.append({"role": "user", "content": question})

    # Generate and display the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Digging through the gold vault..."):
            
            # Retrieve relevant gold price records using gvector
            records = retriever.invoke(question)
            
            # Invoke LLM with grounded context
            response = chain.invoke({
                "records": records,
                "question": question
            })
            
            st.markdown(response)
    
    # Save the assistant's response to state
    st.session_state.messages.append({"role": "assistant", "content": response})