from llm import start_chat_session, get_chat_response

# Start a new chat session
chat = start_chat_session()

# Test the chat session with a simple prompt
prompt = "What are some interesting facts about Chicago?"
response = get_chat_response(chat, prompt)
print("Response:", response)