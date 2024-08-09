import streamlit as st
from openai import OpenAI

# Set up Streamlit page layout
st.set_page_config(page_title="GPT-powered Chatbot", layout="wide")

# Sidebar for API and Model configuration
st.sidebar.title("Chatbot Settings")
st.sidebar.subheader("API Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.secrets["openai_api_key"])
model_options = ["gpt-3.5-turbo", "gpt-4", "davinci-codex", "text-davinci-003"]
selected_model = st.sidebar.selectbox("Choose your model", model_options)

# Session Manager in the sidebar
st.sidebar.subheader("Session Manager")
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
session_name = st.sidebar.text_input("New session name")
if st.sidebar.button("Create session"):
    if session_name:
        st.session_state.chat_sessions[session_name] = []

# List, rename, and delete options for sessions
for session in list(st.session_state.chat_sessions):
    with st.sidebar.expander(session):
        rename = st.text_input("Rename session", key=f"rename_{session}")
        if st.button("Save changes", key=f"save_{session}"):
            if rename and rename != session:
                st.session_state.chat_sessions[rename] = st.session_state.chat_sessions.pop(session)
                st.experimental_rerun()
        if st.button("Delete session", key=f"delete_{session}"):
            del st.session_state.chat_sessions[session]
            st.experimental_rerun()

# Main chat interface
st.title("💬 Chatbot")

if not api_key:
    st.sidebar.error("Please add your OpenAI API key in the secrets to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=api_key)
    selected_session = st.selectbox("Select chat session", options=list(st.session_state.chat_sessions.keys()))
    if selected_session:
        messages = st.session_state.chat_sessions[selected_session]
        
        # Display chat messages
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input field for user messages
        if prompt := st.chat_input("What is up?"):
            messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate a response using the selected model
            stream = client.chat.completions.create(
                model=selected_model,
                messages=messages,
                stream=True,
            )

            # Stream and store the response
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            messages.append({"role": "assistant", "content": response})
            st.session_state.chat_sessions[selected_session] = messages
