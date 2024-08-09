import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")

# Access the OpenAI API key from Streamlit secrets
try:
    openai_api_key = st.secrets["openai"]["api_key"]
except KeyError as e:
    st.error(f"KeyError: {str(e)} - Please check your secrets.toml file configuration.")
    st.stop()

# Check if the API key is present
if not openai_api_key:
    st.info("Please add your OpenAI API key to the secrets file to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Add a dropdown for model selection
    model_options = ["gpt-3.5-turbo", "gpt-4"]
    selected_model = st.selectbox("Select GPT Model", model_options)

    # Initialize session state for managing chat sessions
    if "sessions" not in st.session_state:
        st.session_state.sessions = {}
        st.session_state.current_session = None

    # Sidebar for managing chat sessions
    st.sidebar.title("Chat Sessions")
    session_names = list(st.session_state.sessions.keys())
    session_action = st.sidebar.radio("Action", ["Select", "Create", "Delete"])
    
    if session_action == "Select" and session_names:
        session_selection = st.sidebar.selectbox("Select a chat session", session_names)
        if st.sidebar.button("Load Session"):
            st.session_state.current_session = session_selection
    
    elif session_action == "Create":
        new_session_name = st.sidebar.text_input("Enter new session name")
        if st.sidebar.button("Create Session") and new_session_name:
            st.session_state.sessions[new_session_name] = []
            st.session_state.current_session = new_session_name
    
    elif session_action == "Delete" and session_names:
        session_deletion = st.sidebar.selectbox("Select a chat session to delete", session_names)
        if st.sidebar.button("Delete Session"):
            del st.session_state.sessions[session_deletion]
            if st.session_state.current_session == session_deletion:
                st.session_state.current_session = None

    # Display the selected chat session
    if st.session_state.current_session:
        st.subheader(f"Chat Session: {st.session_state.current_session}")
        session_messages = st.session_state.sessions[st.session_state.current_session]

        # Display existing chat messages
        for message in session_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field
        if prompt := st.chat_input("What is up?"):
            # Store and display the current prompt
            session_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API
            stream = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in session_messages
                ],
                stream=True,
            )

            # Stream the response to the chat
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            session_messages.append({"role": "assistant", "content": response})

            # Update the session with new messages
            st.session_state.sessions[st.session_state.current_session] = session_messages
    else:
        st.info("Please select or create a chat session.", icon="ℹ️")
