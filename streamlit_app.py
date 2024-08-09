import streamlit as st
from openai import OpenAI

# Title and main description
st.title("💬 Chatbot Enhanced UI")

# Access OpenAI API key from secrets
openai_api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)

# Model selection
model_options = ["gpt-3.5-turbo", "gpt-4"]
selected_model = st.sidebar.selectbox("GPT Model", model_options)

# Session Management in Sidebar
st.sidebar.header("Chat Sessions")
if "sessions" not in st.session_state:
    st.session_state.sessions = {}

# Adding a session
new_session_name = st.sidebar.text_input("Create new session")
if st.sidebar.button("Create"):
    if new_session_name and new_session_name not in st.session_state.sessions:
        st.session_state.sessions[new_session_name] = []
        st.sidebar.success("Session created successfully!")

# Session selection
session_name = st.sidebar.selectbox("Select a session", options=list(st.session_state.sessions.keys()))

# Delete a session
if st.sidebar.button("Delete"):
    if session_name in st.session_state.sessions:
        del st.session_state.sessions[session_name]
        st.sidebar.success(f"Deleted session: {session_name}")

# Display session chat
st.header(f"Chat Session: {session_name}")
if session_name:
    messages = st.session_state.sessions[session_name]
    for message in messages:
        st.write(f"{message['role'].capitalize()}: {message['content']}")

    user_input = st.text_input("Type your message here")
    if st.button("Send"):
        messages.append({"role": "user", "content": user_input})
        # Call to OpenAI API to get a response
        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": user_input}],
            stream=True,
        )
        messages.append({"role": "assistant", "content": response.choices[0].message['content']})
        st.session_state.sessions[session_name] = messages
