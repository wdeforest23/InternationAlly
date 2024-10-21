############# v3 ##############

import streamlit as st
import time
from settings import setup, configure_display_options
from chatbot import chat_all

# Title and Description for the app
st.set_page_config(page_title="PropertyPilot")
st.title("PropertyPilot")
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


############# v2 ##############

# import streamlit as st
# import time
# from settings import setup, configure_display_options
# from chatbot import chat_all

# # Initialize the setup in session state if it hasn't been done yet
# if 'setup_done' not in st.session_state:
#     # Setup the bot and environment
#     chat, prompts_dict, neighborhoods_info, neighborhoods_boundaries, vector_store = setup()
#     configure_display_options()
    
#     # Store them in session state
#     st.session_state.chat = chat
#     st.session_state.prompts_dict = prompts_dict
#     st.session_state.neighborhoods_info = neighborhoods_info
#     st.session_state.neighborhoods_boundaries = neighborhoods_boundaries
#     st.session_state.vector_store = vector_store
    
#     # Mark the setup as done
#     st.session_state.setup_done = True

# # Streamlit app setup
# st.title("PropertyPilot")
# st.write("PropertyPilot is an AI-powered real estate assistant designed to transform the home-buying process.")

# # Initialize session state for conversation history if it hasn't been done yet
# if 'conversation' not in st.session_state:
#     st.session_state.conversation = []

# # Chat input
# user_input = st.text_input("Enter your query here:")

# # If there is user input, process the query
# if user_input:
#     # Retrieve the setup objects from session state
#     chat = st.session_state.chat
#     prompts_dict = st.session_state.prompts_dict
#     neighborhoods_info = st.session_state.neighborhoods_info
#     neighborhoods_boundaries = st.session_state.neighborhoods_boundaries
#     vector_store = st.session_state.vector_store
    
#     # Call the chatbot function with user input
#     response, intent = chat_all(chat, prompts_dict, user_input, neighborhoods_info, neighborhoods_boundaries, vector_store)
    
#     # Store conversation history in session state
#     st.session_state.conversation.append({"User": user_input, "PropertyPilot": str(intent) + '\n\n' + response})

# # Display conversation history
# for message in st.session_state.conversation:
#     st.write(f"**You:** {message['User']}")
    
#     # Simulate gradual output for the PropertyPilot's response
#     placeholder = st.empty()  # Create a placeholder for the gradual text output
#     full_response = message['PropertyPilot']
#     gradual_text = ""
    
#     for char in full_response:
#         gradual_text += char
#         placeholder.write(f"**PropertyPilot:** {gradual_text}")
#         time.sleep(0.02)  # Adjust the speed here (0.02 seconds between each character)


############# Original ##############

# import streamlit as st
# from settings import setup, configure_display_options
# from chatbot import chat_all

# # Setup the bot and environment
# chat, prompts_dict, neighborhoods_info, neighborhoods_boundaries, vector_store = setup()
# configure_display_options()

# # Streamlit app setup
# st.title("PropertyPilot")
# st.write("PropertyPilot is an AI-powered real estate assistant designed to transform the home-buying process.")

# # Initialize session state for conversation history
# if 'conversation' not in st.session_state:
#     st.session_state.conversation = []

# # Chat input
# user_input = st.text_input("Enter your query here:")

# # If there is user input, process the query
# if user_input:
#     # Call the chatbot function with user input
#     response, intent = chat_all(chat, prompts_dict, user_input, neighborhoods_info, neighborhoods_boundaries, vector_store)
    
#     # Store conversation history in session state
#     st.session_state.conversation.append({"User": user_input, "PropertyPilot": str(intent) + '\n\n' + response})

# # Display conversation history
# for message in st.session_state.conversation:
#     st.write(f"**You:** {message['User']}")
#     st.write(f"**PropertyPilot:** {message['PropertyPilot']}")