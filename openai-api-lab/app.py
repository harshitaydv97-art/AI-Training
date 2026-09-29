from openai import OpenAI
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

# Create OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Send request to the model
response = client.responses.create
(
    model="gpt-3.5-turbo",
    input="What is matter?"
)

# Display the response
print(response.output_text)
