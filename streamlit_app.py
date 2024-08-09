import streamlit as st
from openai import OpenAI

st.title("💬 Chatbot")

# Initialize OpenAI client
try:
    openai_api_key = st.secrets["openai"]["api_key"]
    client = OpenAI(api_key=openai_api_key)
except KeyError as e:
    st.error("OpenAI API key is missing from the secrets. Please add it to continue.")
    st.stop()

# Dropdown to select the GPT model
model_options = ["gpt-3.5-turbo", "gpt-4"]
selected_model = st.sidebar.selectbox("Select GPT Model", model_options)

# Manage sessions
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# Sidebar for session management
st.sidebar.title("Chat Sessions")
session_names = list(st.session_state.sessions.keys())
session_name = st.sidebar.selectbox("Choose a session", session_names)
if st.sidebar.button("Load Session"):
    st.session_state.current_session = session_name

new_session_name = st.sidebar.text_input("Create new session")
if st.sidebar.button("Create Session"):
    st.session_state.sessions[new_session_name] = []
    st.session_state.current_session = new_session_name

# Display the current session
if st.session_state.current_session:
    st.header(f"Chat Session: {st.session_state.current_session}")
    session_messages = st.session_state.sessions[st.session_state.current_session]

    # Display chat messages
    for message in session_messages:
        role, content = message['role'], message['content']
        st.text(f"{role.capitalize()}: {content}")

    # Input for new message
    user_input = st.text_input("What is up?", key="user_input")
    if st.button("Send", key="send"):
        if user_input:
            # Append user message
            session_messages.append({"role": "user", "content": user_input})
            
            # Generate and append response from OpenAI
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": m["role"], "content": m["content"]} for m in session_messages],
                stream=True
            )
            response_text = response.choices[0].text.strip() if response.choices else "No response generated."
            session_messages.append({"role": "assistant", "content": response_text})
            
            # Update session state
            st.session_state.sessions[st.session_state.current_session] = session_messages
else:
    st.info("Please select or create a chat session.")
