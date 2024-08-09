import streamlit as st
from openai import OpenAI

# Title of the app
st.title("💬 Chatbot")

# Access the OpenAI API key from Streamlit secrets
try:
    openai_api_key = st.secrets["openai"]["api_key"]
except KeyError as e:
    st.error(f"KeyError: {str(e)} - Please check your secrets.toml file configuration.")
    st.stop()

if not openai_api_key:
    st.info("Please add your OpenAI API key to the secrets file to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)
    model_options = ["gpt-3.5-turbo", "gpt-4"]
    selected_model = st.selectbox("Select GPT Model", model_options)

    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
        st.session_state.current_session = None

    st.sidebar.title("Chat Sessions")
    for session_name in list(st.session_state.sessions.keys()):
        col1, col2, col3, col4 = st.sidebar.columns([3, 1, 1, 1])
        with col1:
            if st.sidebar.button(session_name):
                st.session_state.current_session = session_name
        with col2:
            if st.sidebar.button("🗑️", key=f"del_{session_name}"):
                del st.session_state.sessions[session_name]
                if st.session_state.current_session == session_name:
                    st.session_state.current_session = None
        with col3:
            if st.sidebar.button("✏️", key=f"ren_{session_name}"):
                new_name = st.text_input("New name for " + session_name, key=session_name)
                if st.button("Rename", key=f"rename_{session_name}"):
                    st.session_state.sessions[new_name] = st.session_state.sessions.pop(session_name)
                    if st.session_state.current_session == session_name:
                        st.session_state.current_session = new_name
        with col4:
            if st.sidebar.button("📦", key=f"arc_{session_name}"):
                st.sidebar.write("Archive logic here")

    new_session_name = st.sidebar.text_input("Create new session")
    if st.sidebar.button("Create Session"):
        if new_session_name and new_session_name not in st.session_state.sessions:
            st.session_state.sessions[new_session_name] = []
            st.session_state.current_session = new_session_name

    if st.session_state.current_session:
        session_messages = st.session_state.sessions[st.session_state.current_session]
        st.subheader(f"Chat Session: {st.session_state.current_session}")
        for message in session_messages:
            st.text(f"{message['role'].capitalize()}: {message['content']}")
        prompt = st.text_input("What is up?")
        if st.button("Send"):
            session_messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=selected_model,
                messages=[{"role": m["role"], "content": m["content"]} for m in session_messages],
                stream=True,
            )
            session_messages.append({"role": "assistant", "content": "Simulated response"})
            st.session_state.sessions[st.session_state.current_session] = session_messages
    else:
        st.info("Please select or create a chat session.")
