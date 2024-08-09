import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")

# Access the OpenAI API key from Streamlit secrets
openai_api_key = st.secrets["openai"]["api_key"]

# Check if the API key is present
if not openai_api_key:
    st.info("Please add your OpenAI API key to the secrets file to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Add a dropdown for model selection
    model_options = ["gpt-3.5-turbo", "gpt-4"]
    selected_model = st.selectbox("Select GPT Model", model_options)

    # Create a session state variable to store the chat messages.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API with the selected model.
        stream = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
