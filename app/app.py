import streamlit as st
import time
from settings import setup, configure_display_options
from chatbot import chat_all

# Title and Description for the app
st.set_page_config(page_title="PropertyPilot")
st.title("PropertyPilot: InternationAlly")
st.write("PropertyPilot is an AI-powered real estate assistant designed to assist you in your property search journey. Ask anything related to properties, neighborhoods, or real estate trends.")

# Setup the bot and environment, but only once
if 'setup_done' not in st.session_state:
    chat, prompts_dict, neighborhoods_info, neighborhoods_boundaries, vector_store = setup()
    configure_display_options()
    st.session_state.chat = chat
    st.session_state.prompts_dict = prompts_dict
    st.session_state.neighborhoods_info = neighborhoods_info
    st.session_state.neighborhoods_boundaries = neighborhoods_boundaries
    st.session_state.vector_store = vector_store
    st.session_state.setup_done = True

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you with your property search today?"}]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for user to type messages
if user_input := st.chat_input("Enter your query here:"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Retrieve the chatbot and related objects from session state
    chat = st.session_state.chat
    prompts_dict = st.session_state.prompts_dict
    neighborhoods_info = st.session_state.neighborhoods_info
    neighborhoods_boundaries = st.session_state.neighborhoods_boundaries
    vector_store = st.session_state.vector_store
    
    # Get chatbot response
    response, intent = chat_all(chat, prompts_dict, user_input, neighborhoods_info, neighborhoods_boundaries, vector_store)

    # Simulate gradual response with a spinner
    with st.chat_message("assistant"):
        placeholder = st.empty()  # Create a placeholder for the gradual text output
        gradual_text = ""
        
        with st.spinner("Thinking..."):
            for word in response.split():
                gradual_text += word + " "
                placeholder.markdown(gradual_text)  # Update the placeholder with the new word
                time.sleep(0.05)  # Adjust speed here to control how fast the words appear
    
    # Add assistant response to the conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})