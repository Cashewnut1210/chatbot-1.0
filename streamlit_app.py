import streamlit as st
from openai import OpenAI

st.title("💬 Chatbot")

# Access the OpenAI API key from Streamlit's secrets
openai_api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)

# Sidebar for model selection and session management
model_options = ["gpt-3.5-turbo", "gpt-4"]
selected_model = st.sidebar.selectbox("Select GPT Model", model_options)

# Manage chat sessions
if "sessions" not in st.session_state:
    st.session_state.sessions = {}
if "current_session" not in st.session_state:
    st.session_state.current_session = None

session_names = list(st.session_state.sessions.keys())
session_name = st.sidebar.selectbox("Load Session", session_names)

new_session_name = st.sidebar.text_input("Create new session")
if st.sidebar.button("Create Session"):
    st.session_state.sessions[new_session_name] = []
    st.session_state.current_session = new_session_name

# Display and manage current chat session
if st.session_state.current_session:
    st.subheader(f"Chat Session: {st.session_state.current_session}")
    session_messages = st.session_state.sessions[st.session_state.current_session]

    # Display existing chat messages
    for message in session_messages:
        role = message['role']
        content = message['content']
        st.text(f"{role.capitalize()}: {content}")

    # Create a chat input field to allow the user to enter a message
    user_input = st.text_input("What is up?")
    if st.button("Send"):
        # Append user message to session
        session_messages.append({"role": "user", "content": user_input})

        # Generate a response using the OpenAI API
        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": m["role"], "content": m["content"]} for m in session_messages]
        )
        response_text = response.choices[0].text.strip() if response.choices else "No response generated."
        session_messages.append({"role": "assistant", "content": response_text})
        
        # Update the session state
        st.session_state.sessions[st.session_state.current_session] = session_messages
else:
    st.info("Please select or create a chat session.")
