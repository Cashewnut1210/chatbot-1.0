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
        st.session_state.visible_options = None

    st.sidebar.title("Chat Sessions")
    for session_name in list(st.session_state.sessions.keys()):
        col1, col2 = st.sidebar.columns([4, 1])
        with col1:
            st.sidebar.text(session_name)
        with col2:
            if st.sidebar.button("...", key=f"options_{session_name}"):
                st.session_state.visible_options = session_name if st.session_state.visible_options != session_name else None

        if st.session_state.visible_options == session_name:
            if st.sidebar.button("Rename", key=f"rename_{session_name}"):
                new_name = st.text_input("New name for " + session_name, key="new_name_" + session_name)
                if st.button("Save", key=f"save_{session_name}"):
                    st.session_state.sessions[new_name] = st.session_state.sessions.pop(session_name)
                    st.session_state.current_session = new_name
                    st.session_state.visible_options = None
            if st.sidebar.button("Delete", key=f"delete_{session_name}"):
                del st.session_state.sessions[session_name]
                if st.session_state.current_session == session_name:
                    st.session_state.current_session = None
                st.session_state.visible_options = None

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
