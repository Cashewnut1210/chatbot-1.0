import streamlit as st
from openai import OpenAI

st.title("💬 Chatbot")

# Initialize OpenAI client
try:
    openai_api_key = st.secrets["openai"]["api_key"]
    client = OpenAI(api_key=openai_api_key)
except KeyError as e:
    st.error("API key is missing from the secrets. Please add it to continue.")
    st.stop()

# Select model for the chat
model_options = ["gpt-3.5-turbo", "gpt-4"]
selected_model = st.sidebar.selectbox("Select GPT Model", model_options)

# Session management initialization
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# Sidebar for session selection and management
st.sidebar.title("Chat Sessions")
if st.sidebar.button("Load Session"):
    session_names = list(st.session_state.sessions.keys())
    session_name = st.sidebar.selectbox("Choose a session", session_names)
    st.session_state.current_session = session_name

new_session_name = st.sidebar.text_input("Create new session")
if st.sidebar.button("Create Session"):
    st.session_state.sessions[new_session_name] = []
    st.session_state.current_session = new_session_name

# Display and manage the current session
if st.session_state.current_session:
    st.header(f"Chat Session: {st.session_state.current_session}")
    session_messages = st.session_state.sessions[st.session_state.current_session]

    for message in session_messages:
        st.text(f"{message['role'].capitalize()}: {message['content']}")

    user_input = st.text_input("What is up?", key="user_input")
    if st.button("Send"):
        if user_input:
            session_messages.append({"role": "user", "content": user_input})
            try:
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in session_messages],
                    stream=True
                )
                response_text = response.choices[0].text.strip() if response.choices else "No response generated."
            except Exception as e:
                st.error(f"Failed to fetch response: {str(e)}")
                response_text = "Failed to fetch response."

            session_messages.append({"role": "assistant", "content": response_text})
            st.session_state.sessions[st.session_state.current_session] = session_messages
else:
    st.info("Please select or create a chat session.")
