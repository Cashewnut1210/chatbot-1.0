import streamlit as st
from openai import OpenAI

# Set up Streamlit page layout
st.set_page_config(page_title="GPT-powered Chatbot", layout="wide")

# Title and description in the sidebar
st.sidebar.title("Chatbot Settings")
st.sidebar.subheader("API Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.secrets["openai_api_key"])

# Model selection dropdown in the sidebar
model_options = ["gpt-3.5-turbo", "gpt-4", "davinci-codex", "text-davinci-003"]
selected_model = st.sidebar.selectbox("Choose your model", model_options, index=0)

st.sidebar.subheader("Chat Interface")
st.title("💬 Chatbot")

if not api_key:
    st.sidebar.error("Please add your OpenAI API key in the secrets to continue.", icon="🗝️")
else:
    # Create an OpenAI client
    client = OpenAI(api_key=api_key)

    # Session state for persisting chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input field for user messages
    if prompt := st.chat_input("What is up?"):
        # Store and display user prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the selected model and OpenAI API
        stream = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream and store the response
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
