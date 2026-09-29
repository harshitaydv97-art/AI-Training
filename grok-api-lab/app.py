import os
from dotenv import load_dotenv
from xai_sdk import Client
from xai_sdk.chat import user

# Load variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("XAI_API_KEY")

# Check API key
if not api_key:
    print("XAI_API_KEY not found")
    exit()

# Create Grok client
client = Client(api_key=api_key)

# Create chat
chat = client.chat.create(
    model="grok-4.7"
)

# Send prompt
chat.append(
    user("Explain Artificial Intelligence in simple words.")
)

# Get response
response = chat.sample()

# Print response
print("\nGrok Response:")
print(response.content)